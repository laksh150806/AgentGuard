"""Run AgentGuard from a checkout without installing dependencies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agentguard.cli import main  # noqa: E402

raise SystemExit(main())
