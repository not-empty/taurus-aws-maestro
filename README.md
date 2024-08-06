# Taurus-AWS-Maestro
---
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

![Architecture sample](resources/images/diagrama-funcionamento-taurus-aws-maestro.png)

Taurus AWS Maestro is an open-source project developed to analyze queues and applications running on AWS EC2 instances, with the aim of automatically deciding the scalability of applications based on queue demand. This project aims to help reduce costs in environments with high resource demand.

#### Introduction
In environments where we adopt the use of AWS EC2 instances for the infrastructure of applications that are consumed by queues, the variability of consumption according to demand can result in high costs, especially if we keep the application machines active during periods of low usage.

Taurus AWS Maestro offers an automatic and customizable solution for the scalability of applications hosted on the AWS EC2 service, adapting to queue consumption. This system ensures that the application is available whenever necessary, performing environment availability checks before releasing processing, ensuring efficiency and security.

#### Features
- **Automatic Scalability:** Automatically adapts to queue consumption, scaling applications according to demand.
- **Resource Optimization:** Ensures that computing resources are used efficiently, avoiding waste.
- **Customizable Solution:** Offers adjustable settings to meet the specific needs of each environment and application.
- **Availability Checks:** Performs environment availability checks before releasing processing, ensuring the application is always ready to operate.
- **Simplified Automation:** Facilitates the implementation of automatic scalability, reducing the need for manual interventions and operational complexity.
- **Integration with AWS EC2:** The project is aimed at environments that use AWS EC2 instances to host queue-consuming applications.

#### Configuration
Copy the `.env.example` file to the `.env` file and change its parameters:

- **AWS_ACCESS_KEY_ID:** Your public access key provided by AWS.
- **AWS_SECRET_ACCESS_KEY:** Your secret access key provided by AWS.
- **AWS_REGION:** AWS region where the queues and EC2 instances are operating.
- **DEBUG_MODE:** Enables or disables debug mode. The value `1` enables debug mode, while `0` disables it.
- **LOG_SCHEDULES:** Specifies whether schedules should be logged. The value `1` enables schedule logging.
- **LOG_EVENTS:** Specifies whether events should be logged. The value `1` enables event logging.
- **LOG_QUEUES:** Specifies whether queue statuses should be logged. The value `1` enables queue logging.
- **LOG_ACTIONS:** Specifies whether actions defined by the maestro should be logged. The value `1` enables action logging.
- **MYSQL_HOST:** Your MySQL server host address.
- **MYSQL_USER:** Your MySQL username.
- **MYSQL_PASSWORD:** Your MySQL password.
- **MYSQL_DATABASE:** The name of the database to be used.
- **REDIS_HOST:** Your Redis host.
- **REDIS_PORT:** Your Redis port.
- **REDIS_DB:** Your Redis database name.
- **SAVE_DB_HISTORY:** Specifies whether the log history should be saved in the database. The value `1` enables history saving.
- **TIME_SCAN_QUEUE_SCHEDULE:** Specifies the time interval, in seconds, for checking the scheduling queue.
- **TIME_SCAN_EC2_STARTED_SCHEDULE:** Specifies the time interval, in seconds, for checking started EC2 instances.
- **TIME_SCAN_EC2_STOPPED_SCHEDULE:** Specifies the time interval, in seconds, for checking stopped EC2 instances.
- **TIME_SCAN_API_HEALTHCHECK_SCHEDULE:** Specifies the time interval, in seconds, for performing API health checks.

Copy the `config.json.example` file to the `config.json` file and change the values according to the definitions below:

- **name:** Name of your queue.
- **min_on_time:** Minimum time the instance must remain active when started, in seconds.
- **healthchecks:** List of health check URLs to monitor the status of applications associated with the queue.
- **instance_ids:** List of EC2 instance IDs associated with the queue.

#### Installation
After forking or cloning the repository, run the following command to start the project:

```sh
docker-compose up
```

Note that the version of docker-compose used is 1.27.0+.

We should also grant the correct permissions to the storage folder using the following command:

```sh
chmod -R 777 ./storage
```

By following all the steps, Taurus AWS Maestro will be able to analyze your queues and instances, automatically making scalability decisions, thus ensuring application availability and efficiency.

**Not Empty Foundation - Free codes, full minds**
