import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "src" / "main.py"

class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.db = self.base / "test.sqlite3"
        self.json_file = self.base / "signals.json"

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(MAIN), "--database", str(self.db), *args], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")

    def payload(self):
        return {"signal_id": "cli-001", "title": "CLI opportunity", "source_name": "Test source", "source_url": "https://example.com/opportunity", "discovered_at": "2026-10-13T12:00:00+00:00", "description": "CLI test", "country_code": "MA"}

    def write_signals(self, signals):
        self.json_file.write_text(json.dumps(signals), encoding="utf-8")

    def test_status_command(self):
        result = self.run_cli("status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("KISSANE status: OK", result.stdout)
        self.assertIn("Stored signals: 0", result.stdout)

    def test_import_and_list_commands(self):
        self.write_signals([self.payload()])
        imported = self.run_cli("ingest-json", str(self.json_file))
        self.assertEqual(imported.returncode, 0, imported.stderr)
        self.assertIn("Stored total: 1", imported.stdout)
        listed = self.run_cli("list")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("cli-001 | CLI opportunity", listed.stdout)

    def test_reimport_does_not_duplicate(self):
        self.write_signals([self.payload()])
        first = self.run_cli("ingest-json", str(self.json_file))
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.run_cli("ingest-json", str(self.json_file))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("Stored total: 1", second.stdout)
        listed = self.run_cli("list")
        self.assertEqual(listed.stdout.count("cli-001"), 1)

    def test_invalid_json_returns_error(self):
        self.json_file.write_text("{ invalid", encoding="utf-8")
        result = self.run_cli("ingest-json", str(self.json_file))
        self.assertEqual(result.returncode, 2)
        self.assertIn("Error:", result.stderr)

if __name__ == "__main__":
    unittest.main()
