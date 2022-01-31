import time
from shutil import copyfile


# ==============================
# == Service functions
# ==============================

def print_log(string: str) -> str:
    """Print formatted string with local time"""
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ': ' + string)