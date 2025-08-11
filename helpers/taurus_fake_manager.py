import json, os, threading
from typing import Dict
from helpers.fileio import write_json_preserve_owner

def _ensure_dir(path: str):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

_DEFAULT_Q = {"waiting": 0, "active": 0, "paused": 0, "is_paused": False}

class TaurusFakeManager:
    def __init__(self, state_file: str = "fake_data/taurus_state.json", auto_create: bool = True):
        self.state_file = state_file
        self._lock = threading.Lock()
        _ensure_dir(self.state_file)
        if auto_create and not os.path.exists(self.state_file):
            self._write_state({"queues": {}})

    def _read_state(self) -> Dict:
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"queues": {}}

    def _write_state(self, state: Dict) -> None:
        write_json_preserve_owner(self.state_file, state)

    def _ensure_queue(self, name: str, state: Dict) -> Dict:
        qs = state.setdefault("queues", {})
        if name not in qs:
            qs[name] = dict(_DEFAULT_Q)
        return qs[name]

    def get_queue_status(self, queue_name):
        with self._lock:
            state = self._read_state()
            q = self._ensure_queue(queue_name, state)
            return q["waiting"], q["active"], q["paused"], q["is_paused"]

    def pause_queue(self, queue_name):
        with self._lock:
            state = self._read_state()
            q = self._ensure_queue(queue_name, state)
            if not q["is_paused"]:
                q["paused"] += q["waiting"]
                q["waiting"] = 0
                q["is_paused"] = True
                self._write_state(state)

    def unpause_queue(self, queue_name):
        with self._lock:
            state = self._read_state()
            q = self._ensure_queue(queue_name, state)
            if q["is_paused"]:
                q["waiting"] += q["paused"]
                q["paused"] = 0
                q["is_paused"] = False
                self._write_state(state)

    def set_queue_counts(self, queue_name, *, waiting=None, active=None, paused=None, is_paused=None):
        with self._lock:
            state = self._read_state()
            q = self._ensure_queue(queue_name, state)
            if waiting is not None: q["waiting"] = int(waiting)
            if active  is not None: q["active"]  = int(active)
            if paused  is not None: q["paused"]  = int(paused)
            if is_paused is not None: q["is_paused"] = bool(is_paused)
            self._write_state(state)
