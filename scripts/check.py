"""Run the complete local test suite without a package installation."""

import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
env = dict(os.environ)
env["PYTHONPATH"] = str(root / "src")
raise SystemExit(subprocess.call(
    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
    cwd=root, env=env,
))
