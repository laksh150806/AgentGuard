import hashlib
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from agentguard.provenance import capture_provenance


class ProvenanceTests(unittest.TestCase):
    def test_source_fingerprint_detects_uncommitted_revisions_and_excludes_secrets(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "example.py"
            source.parent.mkdir()
            source.write_text("original = True\n")
            subprocess.run(["git", "init", "-q", directory], check=True)
            subprocess.run(["git", "-C", directory, "add", "src"], check=True)
            subprocess.run(["git", "-C", directory, "-c", "user.name=Test", "-c",
                            "user.email=test@example.invalid", "commit", "-qm", "fixture"], check=True)
            first = capture_provenance(root)
            self.assertFalse(first["working_tree_dirty"])
            source.write_text("original = False\n")
            (root / ".env").write_text("SECRET=do-not-collect\n")
            second = capture_provenance(root)
            self.assertEqual(first["agentguard_commit"], second["agentguard_commit"])
            self.assertTrue(second["working_tree_dirty"])
            self.assertNotEqual(first["source_sha256"], second["source_sha256"])
            self.assertEqual(second["source_sha256"], {
                "src/example.py": hashlib.sha256(source.read_bytes()).hexdigest()})
            self.assertNotIn("do-not-collect", str(second))
