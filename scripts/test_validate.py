"""Exercise validation failures through the standalone command."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parent.parent


class ValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        (self.root / "scripts").mkdir()
        shutil.copyfile(SOURCE / "scripts/validate.py", self.root / "scripts/validate.py")
        brand = self.root / "assets/brand"
        brand.mkdir(parents=True)
        for name in ["avatar.png", "social-preview.png"]:
            shutil.copyfile(SOURCE / "assets/brand" / name, brand / name)
        (self.root / "README.md").write_text("# Profile\n")
        self.git("init", "-b", "main")
        self.commit()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")

    def git(self, *args):
        return subprocess.run(
            ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
            cwd=self.root, env=self.env, check=True, capture_output=True, text=True,
        )

    def commit(self):
        message = self.root / ".git/test-message"
        message.write_text("test: prepare validation fixture\n")
        self.git("add", ".")
        self.git("commit", "-F", str(message))

    def validate(self):
        return subprocess.run(
            [sys.executable, "scripts/validate.py"], cwd=self.root,
            env=self.env, capture_output=True, text=True,
        )

    def test_clean_profile_passes(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_nested_svg_external_dependency_fails(self):
        directory = self.root / "assets/brand/technology"
        directory.mkdir()
        (directory / "broken.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><image href="missing.png"/></svg>'
        )
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("external SVG dependency", result.stderr)

    def test_committed_trailing_whitespace_fails(self):
        (self.root / "README.md").write_text("# Profile \n")
        self.commit()
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("trailing whitespace", result.stdout + result.stderr)

    def test_local_trailing_whitespace_fails(self):
        (self.root / "README.md").write_text("# Profile \n")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("trailing whitespace", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
