import os
import sys

# Trick to allow unit tests import packages from backend dir
work_dir = os.getenv("WORK_DIR", default="./flash_backend")
sys.path.append(work_dir)
