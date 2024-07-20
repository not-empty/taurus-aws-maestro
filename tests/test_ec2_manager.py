from helpers.ec2_manager import EC2Manager
from unittest import mock
import unittest

class TestEC2Manager(unittest.TestCase):

  @mock.patch('helpers.ec2_manager.DEBUG_MODE', 0)
  @mock.patch('boto3.client')
  def test_get_instance_status(self, mock_boto_client):
    mock_ec2 = mock_boto_client.return_value
    mock_ec2.describe_instance_status.return_value = {
      'InstanceStatuses': [
          {
              'InstanceId': 'i-test-1',
              'InstanceState': {
                  'Name': 'running'
              },
          },
          {
              'InstanceId': 'i-test-2',
              'InstanceState': {
                  'Name': 'pending'
              },
          }
      ],
    }

    instance = EC2Manager()
    result = instance.get_instance_status(
      ['i-test-1', 'i-test-2'],
      'stopped'
    )
    
    expected = {'i-test-1': 'running', 'i-test-2': 'pending'}
    
    self.assertEqual(result, expected)
    
  @mock.patch('helpers.ec2_manager.DEBUG_MODE', 1)
  def test_get_instance_status_when_debug_mode_is_activated(self):
    instance = EC2Manager()
    result = instance.get_instance_status(
      ['i-test-1', 'i-test-2'],
      'stopped'
    )

    expected = {'i-test-1': 'stopped', 'i-test-2': 'stopped'}
    
    self.assertEqual(result, expected)

  @mock.patch('helpers.ec2_manager.DEBUG_MODE', 0)
  @mock.patch('boto3.client')
  def test_start_instances(self, mock_boto_client):
    mock_ec2 = mock_boto_client.return_value
    instance_ids = ['i-test-1', 'i-test-2']

    instance = EC2Manager()
    instance.start_instances(
      instance_ids,
    )

    mock_ec2.start_instances.assert_called_once_with(InstanceIds=instance_ids)

  @mock.patch('helpers.ec2_manager.DEBUG_MODE', 1)
  @mock.patch('builtins.print')
  def test_start_instances_when_debug_mode_is_activated(self, mock_print):
    instance = EC2Manager()
    instance_ids = ['i-test-1', 'i-test-2']

    instance.start_instances(
      instance_ids,
    )

    mock_print.assert_called_once_with(f"Debug Mode: Pretending to start instance {instance_ids}")


  @mock.patch('helpers.ec2_manager.DEBUG_MODE', 0)
  @mock.patch('boto3.client')
  def test_stop_instances(self, mock_boto_client):
    mock_ec2 = mock_boto_client.return_value
    instance_ids = ['i-test-1', 'i-test-2']

    instance = EC2Manager()
    instance.stop_instances(
      instance_ids,
    )

    mock_ec2.stop_instances.assert_called_once_with(InstanceIds=instance_ids)
    
  @mock.patch('helpers.ec2_manager.DEBUG_MODE', 1)
  @mock.patch('builtins.print')
  def test_stop_instances_when_debug_mode_is_activated(self, mock_print):
    instance = EC2Manager()
    instance_ids = ['i-test-1', 'i-test-2']

    instance.stop_instances(
      instance_ids,
    )
    
    mock_print.assert_called_once_with(f"Debug Mode: Pretending to stop instance {instance_ids}")


if __name__ == '__main__':
    unittest.main()
