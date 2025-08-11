import json, os, threading, time
from typing import Dict, Any
from helpers.fileio import write_json_preserve_owner

_ALLOWED_KEYS = {"fails_before_success", "latency_ms", "fail_count"}

def _ensure_dir(path: str):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

class RequestFakeManager:
    def __init__(self, state_file: str = "fake_data/requests_state.json", auto_create: bool = True, validate_on_load: bool = True):
        self.state_file = state_file
        self._lock = threading.Lock()
        _ensure_dir(self.state_file)
        if auto_create and not os.path.exists(self.state_file):
            self._write_state({"endpoints": {}})

        if validate_on_load:
            self._validate_state(self._read_state())

    def _read_state(self) -> Dict[str, Any]:
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"endpoints": {}}

    def _write_state(self, state: Dict[str, Any]) -> None:
        write_json_preserve_owner(self.state_file, state)

    def _validate_entry(self, ep: str, entry: Dict[str, Any]) -> None:
        unknown = set(entry.keys()) - _ALLOWED_KEYS
        if unknown:
            raise ValueError(f"[requests fake] Endpoint '{ep}' contains unsupported keys: {sorted(list(unknown))}. "
                             f"Allowed keys: {sorted(list(_ALLOWED_KEYS))}")

        if "fails_before_success" in entry and not isinstance(entry["fails_before_success"], int):
            raise ValueError(f"[requests fake] Endpoint '{ep}': 'fails_before_success' must be int")
        if "latency_ms" in entry and not isinstance(entry["latency_ms"], int):
            raise ValueError(f"[requests fake] Endpoint '{ep}': 'latency_ms' must be int")
        if "fail_count" in entry and not isinstance(entry["fail_count"], int):
            raise ValueError(f"[requests fake] Endpoint '{ep}': 'fail_count' must be int")

    def _validate_state(self, state: Dict[str, Any]) -> None:
        eps = state.get("endpoints", {})
        if not isinstance(eps, dict):
            raise ValueError("[requests fake] 'endpoints' must be an object")
        for ep, entry in eps.items():
            if not isinstance(entry, dict):
                raise ValueError(f"[requests fake] Endpoint '{ep}' must be an object")
            self._validate_entry(ep, entry)

    def _resolve_endpoint_entry(self, ep: str, state: Dict[str, Any]) -> Dict[str, Any]:
        eps = state.setdefault("endpoints", {})
        entry = eps.get(ep)
        if entry is None:
            return {"code": 503, "error": "not configured"}

        self._validate_entry(ep, entry)

        fails_needed = int(entry.get("fails_before_success", 0))
        count = int(entry.get("fail_count", 0))

        if count < fails_needed:
            entry["fail_count"] = count + 1
            self._write_state(state)
            return {"code": 503}
        else:
            return {"code": 200}

    def check_endpoint(self, endpoint: str, timeout: int = 2):
        """
        Returns (ok: bool, message: str)
        """
        with self._lock:
            state = self._read_state()
            data  = self._resolve_endpoint_entry(endpoint, state)

        latency_ms = int(state.get("endpoints", {}).get(endpoint, {}).get("latency_ms", 0))
        if latency_ms > 0:
            time.sleep(min(latency_ms / 1000.0, float(timeout)))

        code = int(data.get("code", 503))
        if code == 200:
            return True,  f"Healthcheck passed for endpoint {endpoint}"
        if "error" in data:
            return False, f"Healthcheck failed for endpoint {endpoint} with error: {data['error']}"
        return False,     f"Healthcheck failed for endpoint {endpoint} with status code {code}"

    def set_fails_before_success(self, endpoint: str, n: int, latency_ms: int = 0):
        with self._lock:
            state = self._read_state()
            eps = state.setdefault("endpoints", {})
            eps[endpoint] = {"fails_before_success": int(n), "fail_count": 0}
            if latency_ms:
                eps[endpoint]["latency_ms"] = int(latency_ms)
            self._validate_entry(endpoint, eps[endpoint])
            self._write_state(state)

    def reset_endpoint(self, endpoint: str):
        """Reset fail_count to 0 (useful for reruns)."""
        with self._lock:
            state = self._read_state()
            ep = state.get("endpoints", {}).get(endpoint)
            if ep and "fail_count" in ep:
                ep["fail_count"] = 0
                self._write_state(state)
