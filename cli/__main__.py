from helpers.db_manager import DBManager
import sys

class MaestroCli:
  def __init__(self):
     self.db = DBManager()

  def get_queue_list_and_scan_status(self):
    self.db.get_all_scanner_data()

  def stop_scan_by_queue(self, queue):
    self.db.upsert_scanner_status(queue, 0)
    print(f"Scanner on queue: '{queue}' stopped")

  def start_scan_by_queue(self, queue):
    self.db.upsert_scanner_status(queue, 1)
    print(f"Scanner on queue: '{queue}' started")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python3 cli \n - get_queue_list_and_scan_status \n - stop_scan_by_queue <queue> \n - start_scan_by_queue <queue>")
    else:
        method_raw = sys.argv[1]
        method = getattr(MaestroCli, sys.argv[1], None)
        if callable(method):
          maestro = MaestroCli()
          if method_raw == 'get_queue_list_and_scan_status':
            maestro.get_queue_list_and_scan_status()
          elif method_raw == 'stop_scan_by_queue' and len(sys.argv) == 3:
            queue = sys.argv[2]
            maestro.stop_scan_by_queue(queue)
          elif method_raw == 'start_scan_by_queue' and len(sys.argv) == 3:
            queue = sys.argv[2]
            maestro.start_scan_by_queue(queue)
          else:
            print("<queue> param is required")
        else:
            print(f"Error: '{method}' is not a valid method.")
