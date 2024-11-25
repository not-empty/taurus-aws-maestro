from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, SAVE_DB_HISTORY
import mysql.connector
import ulid

class DBManager:
    def __init__(self):
        self.enabled = SAVE_DB_HISTORY != 0

    def _connect(self):
        return mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

    def _execute_query(self, query, params):
        if not self.enabled:
            return
        connection = self._connect()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def save_queue_status(
        self,
        execution_id,
        queue_name,
        waiting,
        active,
        paused,
        is_paused
    ):
        if SAVE_DB_HISTORY == 0:
            return
        query = """
            INSERT INTO
                queue_logs (
                    id,
                    execution_id,
                    queue_name,
                    waiting,
                    active,
                    paused,
                    is_paused,
                    created_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    NOW()
                )
        """
        log_id = str(
            ulid.new()
        )
        self._execute_query(
            query,
            (
                log_id,
                execution_id,
                queue_name,
                waiting,
                active,
                paused,
                is_paused)
            )

    def save_ec2_status(
        self,
        execution_id,
        queue_name,
        instance_id,
        status
    ):
        if SAVE_DB_HISTORY == 0:
            return
        query = """
            INSERT INTO
                ec2_logs (
                    id,
                    execution_id,
                    queue_name,
                    instance_id,
                    status,
                    created_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    NOW()
                )
        """
        log_id = str(
            ulid.new()
        )
        self._execute_query(
            query,
            (
                log_id,
                execution_id,
                queue_name,
                instance_id,
                status
            )
        )

    def save_aws_action_made(
        self,
        execution_id,
        queue_name,
        instance_id,
        action
    ):
        if SAVE_DB_HISTORY == 0:
            return
        query = """
            INSERT INTO
                aws_action_logs (
                    id,
                    execution_id,
                    queue_name,
                    instance_id,
                    action,
                    created_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    NOW()
                )
        """
        log_id = str(ulid.new())
        self._execute_query(
            query,
            (
                log_id,
                execution_id,
                queue_name,
                instance_id,
                action)
            )

    def save_queue_action(
        self,
        execution_id,
        queue_name,
        action
    ):
        if SAVE_DB_HISTORY == 0:
            return
        query = """
            INSERT INTO
                queue_action_logs (
                    id,
                    execution_id,
                    queue_name,
                    action,
                    created_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    NOW()
                )
        """
        log_id = str(
            ulid.new()
        )
        self._execute_query(
            query,
            (
                log_id,
                execution_id,
                queue_name,
                action
            )
        )

