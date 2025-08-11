import os
import json
import requests

class SlackNotifier:
    def __init__(self, timeout: float = 3.0):
        self.url = os.getenv("SLACK_WEBHOOK_URL", "")
        self.timeout = timeout

    def post(self, title: str, message: str):
        if not self.url:
            return

        payload = {"title": str(title), "message": str(message)}
        headers = {"Content-Type": "application/json"}

        try:
            requests.post(self.url, data=json.dumps(payload), headers=headers, timeout=self.timeout)
        except requests.RequestException as e:
            return
