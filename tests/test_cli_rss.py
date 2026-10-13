import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "src" / "main.py"


class CLIRssTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.temp.name) / "test.sqlite3")

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(MAIN), "--database", self.db, *args], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")

    def test_help_lists_fetch_rss(self):
        result = subprocess.run([sys.executable, str(MAIN), "--help"], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("fetch-rss", result.stdout)

    def test_invalid_url_returns_error_without_network(self):
        result = self.run_cli("fetch-rss", "file:///invalid.xml")
        self.assertEqual(result.returncode, 2)
        self.assertIn("HTTP or HTTPS", result.stderr)

    def test_invalid_limit_returns_error_without_network(self):
        result = self.run_cli("fetch-rss", "https://example.com/feed.xml", "--limit", "0")
        self.assertEqual(result.returncode, 2)
        self.assertIn("limit must be between 1 and 100", result.stderr)


if __name__ == "__main__":
    unittest.main()
