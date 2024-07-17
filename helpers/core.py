from colorama import Fore
from datetime import datetime
import config
import sched
import time
import ulid

from helpers.ec2_manager import EC2Manager
from helpers.taurus_manager import TaurusManager
from helpers.request_manager import RequestManager  
from helpers.db_manager import DBManager

db_manager = DBManager()
ec2_manager = EC2Manager()
request_manager = RequestManager()
taurus_queue = TaurusManager(
    redis_host=config.REDIS_HOST,
    redis_port=config.REDIS_PORT,
    redis_db=config.REDIS_DB
)
scheduler = sched.scheduler(
    time.time,
    time.sleep
)

scheduled_events = {}
instance_statuses = {}
queue_statuses = {}

execution_id = str(
    ulid.new()
)

def log_initial_instance_status():
    print(Fore.YELLOW + "=" * 30)
    print(Fore.YELLOW + 'Initial AWS Instance States')
    for queue_config in config.configuration['queues']:
        queue_name = queue_config['name']
        instance_ids = queue_config['instance_ids']
        statuses = ec2_manager.get_instance_status(instance_ids, 'stopped')
        for instance_id, status in statuses.items():
            status_code = 0
            if status == 'running':
                status_code = 1

            instance_statuses[instance_id] = status
            db_manager.save_ec2_status(
                execution_id,
                queue_name,
                instance_id,
                status_code
            )
            print(Fore.YELLOW + f"{queue_name} ({instance_id}) - {status}")
    print(Fore.YELLOW + "=" * 30)

def log_event(event_type, queue_name):
    if config.LOG_EVENTS == 1:
        print(Fore.WHITE + f"{datetime.now()} - Event: {event_type} for queue: {queue_name}")

def log_action(message, queue_name, color):
    if config.LOG_ACTIONS == 1:
        print(color + f"{datetime.now()} - Action: {message} for queue: {queue_name}")

def log_important_action(message, queue_name, color):
    print(color + f"{datetime.now()} - Important Action: {message} for queue: {queue_name}")

def log_schedule(event_type, queue_name, time):
    if config.LOG_SCHEDULES == 1:
        print(Fore.MAGENTA + f"{datetime.now()} - Schedule: {event_type} for queue: {queue_name} in {time} seconds")

def log_queue_status(queue_name, is_paused, waiting, active, paused):
    if config.LOG_QUEUES == 1:
        print(Fore.CYAN + f"{datetime.now()} - Queue {queue_name} - Paused: {is_paused} - Waiting: {waiting} - Active: {active} - Paused: {paused}")

def check_api_healthcheck(queue_config):
    queue_name = queue_config['name']
    log_event(
        'check_api_healthcheck',
        queue_name
    )
    endpoints = queue_config.get('healthchecks', [])
    
    all_healthy = True
    for endpoint in endpoints:
        is_healthy, message = request_manager.check_endpoint(endpoint)
        log_action(message, queue_name, Fore.GREEN)
        if not is_healthy:
            all_healthy = False
    
    if all_healthy:
        log_important_action(
            f"All healthchecks {endpoints} passed. Unpausing queue..",
            queue_name,
            Fore.GREEN
        )
        db_manager.save_queue_action(
            execution_id, queue_name,
            1
        )
        taurus_queue.unpause_queue(queue_name)
        next_check_delay = queue_config['min_on_time']
        schedule_next_event(
            queue_config,
            'scan_queue',
            next_check_delay
        )
    else:
        log_important_action(
            f"Some healthchecks failed for queue {queue_name}, rescheduling healthcheck",
            queue_name,
            Fore.GREEN
        )
        schedule_next_event(
            queue_config,
            'check_api_healthcheck'
        )

def check_running_instances(queue_config):
    queue_name = queue_config['name']
    log_event(
        'check_running_instances',
        queue_name
    )

    instance_ids = queue_config['instance_ids']
    statuses = ec2_manager.get_instance_status(
        instance_ids,
        'running'
    )

    action_confirmed = True
    for instance_id, status in statuses.items():
        instance_statuses[instance_id] = status
        if status != 'running':
            action_confirmed = False

    if action_confirmed:
        log_important_action(
            f"All instances {instance_ids} are running.",
            queue_name,
            Fore.GREEN
        )
        healthchecks = queue_config['healthchecks']
        time_to_check_healthchecks = config.TIME_SCAN_API_HEALTHCHECK_SCHEDULE
        if not healthchecks:
            time_to_check_healthchecks = 0            

        schedule_next_event(
            queue_config,
            'check_api_healthcheck',
            time_to_check_healthchecks
        )
    else:
        schedule_next_event(
            queue_config,
            'check_running_instances',
            config.TIME_SCAN_EC2_STARTED_SCHEDULE
        )

def scan_queue(queue_config):
    queue_name = queue_config['name']
    log_event(
        'scan_queue',
        queue_name
    )

    instance_ids = queue_config['instance_ids']
    waiting, active, paused, is_paused = taurus_queue.get_queue_status(queue_name)
    
    log_queue_status(
        queue_name,
        is_paused,
        waiting,
        active,
        paused
    )

    has_items = (waiting + active + paused) > 0
    current_status = (is_paused, has_items)

    if queue_name not in queue_statuses or queue_statuses[queue_name] != current_status:
        db_manager.save_queue_status(
            execution_id,
            queue_name,
            waiting,
            active,
            paused,
            is_paused
        )

        queue_statuses[queue_name] = current_status
    
    if not has_items:
        action_taken = False
        queue_is_paused = False
        for instance_id in instance_ids:
            if instance_statuses.get(instance_id) == 'running':
                db_manager.save_aws_action_made(
                    execution_id,
                    queue_name,
                    instance_id,
                    0
                )

                instance_statuses[instance_id] = 'stopping'
                if (not queue_is_paused):
                    queue_is_paused = True
                    db_manager.save_queue_action(
                        execution_id,
                        queue_name,
                        0
                    )
                    log_important_action(
                        'Pausing queue to stop instances',
                        queue_name,
                        Fore.RED
                    )
                    taurus_queue.pause_queue(queue_name)
                ec2_manager.stop_instances([instance_id])
                action_taken = True

        if action_taken:
            log_important_action(
                f"Stoping all instances {instance_ids}",
                queue_name,
                Fore.RED
            )
            schedule_next_event(
                queue_config,
                'checking_stopped_instances',
                config.TIME_SCAN_EC2_STOPPED_SCHEDULE
            )
        else:
            log_action(
                'no actions to perform',
                queue_name,
                Fore.YELLOW
            )
            schedule_next_event(
                queue_config,
                'scan_queue'
            )
    else:
        action_taken = False
        for instance_id in instance_ids:
            if instance_statuses.get(instance_id) == 'stopped':
                db_manager.save_aws_action_made(
                    execution_id,
                    queue_name,
                    instance_id,
                    1
                )
                instance_statuses[instance_id] = 'pending'
                ec2_manager.start_instances([instance_id])
                action_taken = True

        if action_taken:
            log_important_action(
                f"Starting instances {instance_ids}",
                queue_name,
                Fore.GREEN
            )
            schedule_next_event(
                queue_config,
                'check_running_instances',
                config.TIME_SCAN_EC2_STARTED_SCHEDULE
            )
        else:
            log_action(
                'no actions to perform',
                queue_name,
                Fore.YELLOW
            )
            schedule_next_event(
                queue_config,
                'scan_queue'
            )

def checking_stopped_instances(queue_config):
    queue_name = queue_config['name']
    log_event(
        'checking_stopped_instances',
        queue_name
    )
    instance_ids = queue_config['instance_ids']
    statuses = ec2_manager.get_instance_status(
        instance_ids,
        'stopped'
    )
    all_stopped = True

    for instance_id, status in statuses.items():
        instance_statuses[instance_id] = status
        if status != 'stopped':
            all_stopped = False

    if all_stopped:
        log_important_action(
            f"All instances {instance_ids} are stopped",
            queue_name,
            Fore.RED
        )
        schedule_next_event(
            queue_config,
            'scan_queue'
        )
    else:
        log_important_action(
            f"Some instances {instance_ids} still no stopped",
            queue_name,
            Fore.RED
        )
        schedule_next_event(
            queue_config,
            'checking_stopped_instances',
            config.TIME_SCAN_EC2_STOPPED_SCHEDULE
        )

def schedule_next_event(
    queue_config,
    event_type,
    time_schedule=config.TIME_SCAN_QUEUE_SCHEDULE
):
    queue_name = queue_config['name']
    scheduler.enter(
        time_schedule,
        1,
        event_wrapper,
        (queue_config, event_type)
    )
    log_schedule(
        f'{event_type}',
        queue_name,
        time_schedule
    )

def event_wrapper(
    queue_config,
    event_type
):
    queue_name = queue_config['name']
    try:
        eval(event_type)(queue_config)
    finally:
        scheduled_events.pop(
            queue_name,
            None
        )

def initialize_scheduler():
    global execution_id
    execution_id = str(
        ulid.new()
    )
    print(Fore.CYAN + f"Execution ID: {execution_id}")

    log_initial_instance_status()
    for queue_config in config.configuration['queues']:
        schedule_next_event(
            queue_config,
            'scan_queue',
            0
        )
    
    scheduler.run()
