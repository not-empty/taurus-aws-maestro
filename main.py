from colorama import init, Fore
from config import DEBUG_MODE, SAVE_DB_HISTORY
from helpers.core import initialize_scheduler

init(autoreset=True)

if __name__ == "__main__":
    print(Fore.WHITE + 'Taurus-AWS-Maestro :>>>')
    print(Fore.WHITE + f"Debug Mode: {DEBUG_MODE}")
    print(Fore.WHITE + f"Saving DB History: {SAVE_DB_HISTORY}")
    initialize_scheduler()
