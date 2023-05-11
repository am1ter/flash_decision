import sys
from pathlib import Path

# Trick to allow unit tests import packages from backend dir
backend_dir = Path(__file__).parent / "/flash_backend"
sys.path.append(str(backend_dir))
