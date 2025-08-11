import os
import config

def build_ec2_manager():
    driver = os.getenv("MAESTRO_EC2_DRIVER", "aws").lower()
    if driver == "file":
        from .ec2_fake_manager import EC2FakeManager
        return EC2FakeManager()
    else:
        from .ec2_manager import EC2Manager
        return EC2Manager()

def build_taurus_manager():
    driver = os.getenv("MAESTRO_TAURUS_DRIVER", "redis").lower()
    if driver == "file":
        from .taurus_fake_manager import TaurusFakeManager
        return TaurusFakeManager()
    else:
        from .taurus_manager import TaurusManager
        return TaurusManager(
            redis_host=config.REDIS_HOST,
            redis_port=config.REDIS_PORT,
            redis_db=config.REDIS_DB,
        )

def build_request_manager():
    driver = os.getenv("MAESTRO_REQUEST_DRIVER", "http").lower()
    if driver == "file":
        from .request_fake_manager import RequestFakeManager
        return RequestFakeManager()
    else:
        from .request_manager import RequestManager
        return RequestManager()