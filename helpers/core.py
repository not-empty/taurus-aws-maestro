# core.py
from colorama import Fore
from datetime import datetime
import config
import sched
import time
import ulid

from helpers.manager_factory import build_ec2_manager, build_taurus_manager, build_request_manager
from helpers.db_manager import DBManager

db_manager       = DBManager()
ec2_manager      = build_ec2_manager()
taurus_queue     = build_taurus_manager()
request_manager  = build_request_manager()

scheduler = sched.scheduler(time.time, time.sleep)

scheduled_events = {}
instance_statuses = {}
queue_statuses    = {}

execution_id = str(ulid.new())

def log_event(event_type, name):
    if config.LOG_EVENTS == 1:
        print(Fore.WHITE + f"{datetime.now()} - Event: {event_type} for rule: {name}")

def log_action(message, name, color):
    if config.LOG_ACTIONS == 1:
        print(color + f"{datetime.now()} - Action: {message} for rule: {name}")

def log_important_action(message, name, color):
    print(color + f"{datetime.now()} - Important Action: {message} for rule: {name}")

def log_schedule(event_type, name, secs):
    if config.LOG_SCHEDULES == 1:
        print(Fore.MAGENTA + f"{datetime.now()} - Schedule: {event_type} for rule: {name} in {secs} seconds")

def log_queue_status(queue_name, is_paused, waiting, active, paused):
    if config.LOG_QUEUES == 1:
        print(Fore.CYAN + f"{datetime.now()} - Queue {queue_name} - Paused: {is_paused} - Waiting: {waiting} - Active: {active} - Paused: {paused}")

def log_initial_instance_status():
    print(Fore.YELLOW + "=" * 30)
    print(Fore.YELLOW + "Initial AWS Instance States")
    for rule in config.configuration["rules"]:
        rule_name    = rule["name"]
        instance_ids = rule["instance_ids"]
        statuses     = ec2_manager.get_instance_status(instance_ids, "stopped")
        for instance_id, status in statuses.items():
            instance_statuses[instance_id] = status
            status_code = 1 if status == "running" else 0
            db_manager.save_ec2_status(execution_id, rule_name, instance_id, status_code)
            print(Fore.YELLOW + f"{rule_name} ({instance_id}) - {status}")
    print(Fore.YELLOW + "=" * 30)

def aggregate_rule_queues(rule):
    queue_stats = {}
    group_has_items = False
    all_paused = True
    for q in rule["queues"]:
        waiting, active, paused, is_paused = taurus_queue.get_queue_status(q)
        queue_stats[q] = (waiting, active, paused, is_paused)
        log_queue_status(q, is_paused, waiting, active, paused)

        if (waiting + active + paused) > 0:
            group_has_items = True
        if not is_paused:
            all_paused = False

        current = (is_paused, (waiting + active + paused) > 0)
        if q not in queue_statuses or queue_statuses[q] != current:
            db_manager.save_queue_status(execution_id, q, waiting, active, paused, is_paused)
            queue_statuses[q] = current

    return queue_stats, group_has_items, all_paused

def all_instances_running(rule):
    instance_ids = rule["instance_ids"]
    statuses = ec2_manager.get_instance_status(instance_ids, "running")
    all_ok = True
    for iid, st in statuses.items():
        instance_statuses[iid] = st
        if st != "running":
            all_ok = False
    return all_ok

def all_instances_stopped(rule):
    instance_ids = rule["instance_ids"]
    statuses = ec2_manager.get_instance_status(instance_ids, "stopped")
    all_ok = True
    for iid, st in statuses.items():
        instance_statuses[iid] = st
        if st != "stopped":
            all_ok = False
    return all_ok

def check_api_healthcheck(rule):
    rule_name  = rule["name"]
    log_event("check_api_healthcheck", rule_name)
    endpoints = rule.get("healthchecks", []) or []

    all_healthy = True
    for endpoint in endpoints:
        ok, message = request_manager.check_endpoint(endpoint)
        log_action(message, rule_name, Fore.GREEN if ok else Fore.RED)
        if not ok:
            all_healthy = False

    if all_healthy:
        for q in rule["queues"]:
            taurus_queue.unpause_queue(q)
            db_manager.save_queue_action(execution_id, q, 1)
            log_important_action(f"Unpausing queue {q}", rule_name, Fore.GREEN)

        next_delay = int(rule.get("min_on_time", config.TIME_SCAN_QUEUE_SCHEDULE))
        schedule_next_event(rule, "scan_rule", next_delay)
    else:
        log_important_action(f"Some healthchecks failed for rule {rule_name}, rescheduling", rule_name, Fore.YELLOW)
        schedule_next_event(rule, "check_api_healthcheck", config.TIME_SCAN_API_HEALTHCHECK_SCHEDULE)

def check_running_instances(rule):
    rule_name = rule["name"]
    log_event("check_running_instances", rule_name)

    if all_instances_running(rule):
        log_important_action(f"All instances are running.", rule_name, Fore.GREEN)
        if rule.get("healthchecks"):
            delay = config.TIME_SCAN_API_HEALTHCHECK_SCHEDULE
            schedule_next_event(rule, "check_api_healthcheck", delay)
        else:
            for q in rule["queues"]:
                taurus_queue.unpause_queue(q)
                db_manager.save_queue_action(execution_id, q, 1)
                log_important_action(f"Unpausing queue {q}", rule_name, Fore.GREEN)
            next_delay = int(rule.get("min_on_time", config.TIME_SCAN_QUEUE_SCHEDULE))
            schedule_next_event(rule, "scan_rule", next_delay)
    else:
        schedule_next_event(rule, "check_running_instances", config.TIME_SCAN_EC2_STARTED_SCHEDULE)

def scan_rule(rule):
    rule_name = rule["name"]
    log_event("scan_rule", rule_name)

    queue_stats, group_has_items, _ = aggregate_rule_queues(rule)
    instance_ids = rule["instance_ids"]

    running_instances = [iid for iid in instance_ids if instance_statuses.get(iid) == "running"]
    stopped_instances = [iid for iid in instance_ids if instance_statuses.get(iid) == "stopped"]

    if not group_has_items:
        if running_instances:
            paused_now = []
            for q, (_w, _a, _p, is_paused) in queue_stats.items():
                if not is_paused:
                    taurus_queue.pause_queue(q)
                    db_manager.save_queue_action(execution_id, q, 0)
                    paused_now.append(q)
            if paused_now:
                log_important_action(f"Pausing queues for shutdown: {paused_now}", rule_name, Fore.RED)

            action_taken = False
            for iid in running_instances:
                db_manager.save_aws_action_made(execution_id, rule_name, iid, 0)
                instance_statuses[iid] = "stopping"
                ec2_manager.stop_instances([iid])
                action_taken = True

            if action_taken:
                log_important_action(f"Stopping instances {running_instances}", rule_name, Fore.RED)
                schedule_next_event(rule, "checking_stopped_instances", config.TIME_SCAN_EC2_STOPPED_SCHEDULE)
            else:
                log_action("no stop actions to perform", rule_name, Fore.YELLOW)
                schedule_next_event(rule, "scan_rule", config.TIME_SCAN_QUEUE_SCHEDULE)
        else:
            sync_paused = []
            for q, (_w, _a, _p, is_paused) in queue_stats.items():
                if not is_paused:
                    taurus_queue.pause_queue(q)
                    db_manager.save_queue_action(execution_id, q, 0)
                    sync_paused.append(q)
            if sync_paused:
                log_action(f"sync pause (instances stopped): {sync_paused}", rule_name, Fore.YELLOW)
            schedule_next_event(rule, "scan_rule", config.TIME_SCAN_QUEUE_SCHEDULE)

    else:
        to_start = stopped_instances
        action_taken = False
        for iid in to_start:
            db_manager.save_aws_action_made(execution_id, rule_name, iid, 1)
            instance_statuses[iid] = "pending"
            ec2_manager.start_instances([iid])
            action_taken = True

        if action_taken:
            log_important_action(f"Starting instances {to_start}", rule_name, Fore.GREEN)
            schedule_next_event(rule, "check_running_instances", config.TIME_SCAN_EC2_STARTED_SCHEDULE)
        else:
            unpaused_now = []
            for q, (_w, _a, _p, is_paused) in queue_stats.items():
                if is_paused:
                    taurus_queue.unpause_queue(q)
                    db_manager.save_queue_action(execution_id, q, 1)
                    unpaused_now.append(q)
            if unpaused_now:
                log_important_action(f"Unpausing queues (instances running): {unpaused_now}", rule_name, Fore.GREEN)
            next_delay = int(rule.get("min_on_time", config.TIME_SCAN_QUEUE_SCHEDULE))
            schedule_next_event(rule, "scan_rule", next_delay)

def checking_stopped_instances(rule):
    rule_name = rule["name"]
    log_event("checking_stopped_instances", rule_name)

    if all_instances_stopped(rule):
        log_important_action("All instances are stopped", rule_name, Fore.RED)
        schedule_next_event(rule, "scan_rule", config.TIME_SCAN_QUEUE_SCHEDULE)
    else:
        log_important_action("Some instances still not stopped", rule_name, Fore.RED)
        schedule_next_event(rule, "checking_stopped_instances", config.TIME_SCAN_EC2_STOPPED_SCHEDULE)

def schedule_next_event(rule_config, event_type, time_schedule=None):
    name = rule_config["name"]
    delay = time_schedule if time_schedule is not None else config.TIME_SCAN_QUEUE_SCHEDULE
    scheduler.enter(delay, 1, event_wrapper, (rule_config, event_type))
    log_schedule(event_type, name, delay)

def event_wrapper(rule_config, event_type):
    name = rule_config["name"]
    try:
        eval(event_type)(rule_config)
    finally:
        scheduled_events.pop(name, None)

def initialize_scheduler():
    global execution_id
    execution_id = str(ulid.new())
    print(Fore.CYAN + f"Execution ID: {execution_id}")

    log_initial_instance_status()
    for rule_cfg in config.configuration["rules"]:
        schedule_next_event(rule_cfg, "scan_rule", 0)

    scheduler.run()
