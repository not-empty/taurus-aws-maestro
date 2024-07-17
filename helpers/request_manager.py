import requests
from config import DEBUG_MODE

class RequestManager:
    def check_endpoint(self, endpoint, timeout=2):
        if DEBUG_MODE == 1:
            print(f"Debug Mode: Pretending to check endpoint {endpoint}")
            return True, f"Healthcheck passed for endpoint {endpoint}"

        try:
            response = requests.get(endpoint, timeout=timeout)
            if response.status_code == 200:
                return True, f"Healthcheck passed for endpoint {endpoint}"
            else:
                return False, f"Healthcheck failed for endpoint {endpoint} with status code {response.status_code}"
        except requests.RequestException as e:
            return False, f"Healthcheck failed for endpoint {endpoint} with error: {str(e)}"
