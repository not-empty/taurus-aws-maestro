import json, os

try:
    import fcntl
except ImportError:
    fcntl = None

def write_json_preserve_owner(path: str, data: dict, create_mode: int = 0o664) -> None:
    payload = json.dumps(data, indent=2).encode("utf-8")

    fd = os.open(path, os.O_RDWR | os.O_CREAT, create_mode)
    try:
        if fcntl:
            fcntl.flock(fd, fcntl.LOCK_EX)

        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, payload)
        os.ftruncate(fd, len(payload))
        os.fsync(fd)
    finally:
        if fcntl:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except Exception:
                pass
        os.close(fd)
