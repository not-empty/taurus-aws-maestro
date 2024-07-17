import redis

class TaurusManager:
    def __init__(
        self,
        redis_host='localhost',
        redis_port=6379,
        redis_db=0
    ):
        self.r = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db
        )

    def get_queue_status(
        self,
        queue_name
    ):
        waiting = self.r.llen(f'bull:{queue_name}:wait')
        active = self.r.llen(f'bull:{queue_name}:active')
        paused = self.r.llen(f'bull:{queue_name}:paused')
        is_paused = bool(
            self.r.exists(f'bull:{queue_name}:meta-paused')
        )
        return waiting, active, paused, is_paused

    def pause_queue(
        self,
        queue_name
    ):
        if not self.r.exists(f'bull:{queue_name}:meta-paused'):
            self.r.set(f'bull:{queue_name}:meta-paused', 1)
            if self.r.exists(f'bull:{queue_name}:wait'):
                self.r.rename(
                    f'bull:{queue_name}:wait',
                    f'bull:{queue_name}:paused'
                )

    def unpause_queue(
        self,
        queue_name
    ):
        if self.r.exists(f'bull:{queue_name}:meta-paused'):
            self.r.delete(f'bull:{queue_name}:meta-paused')
            if self.r.exists(f'bull:{queue_name}:paused'):
                self.r.rename(
                    f'bull:{queue_name}:paused',
                    f'bull:{queue_name}:wait'
                )
