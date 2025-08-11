import json, os, threading
from typing import Dict, List
from helpers.fileio import write_json_preserve_owner

def _ensure_dir(path: str):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

class EC2FakeManager:
    def __init__(self, state_file: str = "fake_data/ec2_state.json", auto_create: bool = True):
        self.state_file = state_file
        self._lock = threading.Lock()
        _ensure_dir(self.state_file)
        if auto_create and not os.path.exists(self.state_file):
            self._write_state({"instances": {}})

    def _read_state(self) -> Dict:
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"instances": {}}

    def _write_state(self, state: Dict) -> None:
        write_json_preserve_owner(self.state_file, state)

    def get_instance_status(self, instance_ids: List[str], desired_status: str = "running") -> Dict[str, str]:
        with self._lock:
            state = self._read_state()
            inst = state.setdefault("instances", {})
            out = {}
            for iid in instance_ids:
                out[iid] = inst.get(iid, "stopped")
            return out

    def start_instances(self, instance_ids: List[str]) -> None:
        with self._lock:
            state = self._read_state()
            inst = state.setdefault("instances", {})
            for iid in instance_ids:
                inst[iid] = "running"
            self._write_state(state)

    def stop_instances(self, instance_ids: List[str]) -> None:
        with self._lock:
            state = self._read_state()
            inst = state.setdefault("instances", {})
            for iid in instance_ids:
                inst[iid] = "stopped"
            self._write_state(state)
