"""Record reproducibility metadata without collecting environment secrets."""

from datetime import datetime, timezone
import hashlib
from importlib.metadata import distributions
import platform
import subprocess


def capture_provenance(root):
    """Fingerprint executable sources, including uncommitted experiment revisions."""
    paths = sorted((root / "src").rglob("*.py"))
    paths += sorted((root / "scripts").glob("*.py"))
    paths.append(root / "pyproject.toml")
    hashes = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in paths if path.is_file()}
    commit = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    dirty = bool(subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain"], text=True).strip())
    return {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "agentguard_commit": commit,
        "working_tree_dirty": dirty,
        "source_sha256": hashes,
        "python_version": platform.python_version(),
        "platform": {"system": platform.system(), "machine": platform.machine()},
        "dependencies": dict(sorted((dist.metadata["Name"], dist.version)
                                    for dist in distributions() if dist.metadata["Name"])),
    }
