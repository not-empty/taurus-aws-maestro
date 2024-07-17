from config import DEBUG_MODE
import boto3

class EC2Manager:
    def __init__(self):
        if DEBUG_MODE == 0:
            self.ec2 = boto3.client('ec2')

    def get_instance_status(
        self,
        instance_ids,
        desired_status='running'
    ):
        if DEBUG_MODE == 1:
            return {instance_id: desired_status for instance_id in instance_ids}

        statuses = {instance_id: 'stopped' for instance_id in instance_ids}
        response = self.ec2.describe_instance_status(
            InstanceIds=instance_ids
        )

        for instance_status in response['InstanceStatuses']:
            instance_id = instance_status['InstanceId']
            status = instance_status['InstanceState']['Name']
            statuses[instance_id] = status

        return statuses

    def start_instances(
        self,
        instance_ids
    ):
        if DEBUG_MODE == 1:
            print(f"Debug Mode: Pretending to start instance {instance_ids}")
            return

        self.ec2.start_instances(
            InstanceIds=instance_ids
        )

    def stop_instances(self, instance_ids):
        if DEBUG_MODE == 1:
            print(f"Debug Mode: Pretending to stop instance {instance_ids}")
            return

        self.ec2.stop_instances(
            InstanceIds=instance_ids
        )
