# This file used only because of the bug in VSCode, that disallow use unittest discovery correctly:
# https://github.com/microsoft/vscode-python/issues/21267#issuecomment-1553718705

import sys
from pathlib import Path

# Trick to allow unit tests import packages from backend dir
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))
