from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, SAVE_DB_HISTORY
import mysql.connector
import ulid

class DBManager:
    def __init__(self):
        if SAVE_DB_HISTORY == 0:
            return
        self.connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        self.cursor = self.connection.cursor()

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
        self.cursor.execute(
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
        self.connection.commit()

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
        self.cursor.execute(
            query,
            (
                log_id,
                execution_id,
                queue_name,
                instance_id,
                status
            )
        )
        self.connection.commit()

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
        self.cursor.execute(
            query,
            (
                log_id,
                execution_id,
                queue_name,
                instance_id,
                action)
            )
        self.connection.commit()

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
        self.cursor.execute(
            query,
            (
                log_id,
                execution_id,
                queue_name,
                action
            )
        )
        self.connection.commit()

    def get_all_scanner_data(
            self
        ):
            self.cursor.execute(
                "SELECT * FROM scanner",
            )
            
            results = self.cursor.fetchall()
            for row in results:
                print(row)

    def get_scanner_status_by_queue(
            self,
            queue
        ):
            query = """
                SELECT status
                FROM scanner
                WHERE queue = %s
                """

            self.cursor.execute(
                query,
                [queue]
            )
            
            result = self.cursor.fetchone()

            if (result):
                return result[0]

            return result

    def upsert_scanner_status(
            self,
            queue,
            status
        ):
            scanner_status = self.get_scanner_status_by_queue(queue)

            if (scanner_status == status):
                return

            query = """
                INSERT INTO
                    scanner (
                        queue,
                        status,
                        created_at
                    )
                VALUES (
                    %s,
                    %s,
                    NOW())
                """
            params = (queue, status)

            if (scanner_status == 0 or scanner_status == 1):
                query = """
                    UPDATE scanner
                    SET status = %s
                    WHERE queue = %s
                    """
                params = (status, queue)

            self.cursor.execute(
                query,
                params
            )

            self.connection.commit()

    def close(self):
        if SAVE_DB_HISTORY == 0:
            return
        self.cursor.close()
        self.connection.close()
