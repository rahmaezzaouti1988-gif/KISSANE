import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "src" / "main.py"

class CLIRankTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.db = self.base / "rank.sqlite3"
        self.json_file = self.base / "signals.json"

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(MAIN), "--database", str(self.db), *args], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")

    def test_rank_orders_signals_by_score(self):
        signals = [
            {"signal_id": "general", "title": "Speech on disaster risk management", "source_name": "Test", "source_url": "https://example.com/1", "discovered_at": "2026-10-13T12:00:00+00:00"},
            {"signal_id": "funding", "title": "New grant opportunity", "source_name": "Test", "source_url": "https://example.com/2", "discovered_at": "2026-10-13T12:01:00+00:00"},
            {"signal_id": "tender", "title": "Open call for tenders", "source_name": "Test", "source_url": "https://example.com/3", "discovered_at": "2026-10-13T12:02:00+00:00"}
        ]
        self.json_file.write_text(json.dumps(signals), encoding="utf-8")
        imported = self.run_cli("ingest-json", str(self.json_file))
        self.assertEqual(imported.returncode, 0, imported.stderr)
        result = self.run_cli("rank")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(result.stdout.index("procurement_opportunity"), result.stdout.index("funding_opportunity"))
        self.assertLess(result.stdout.index("funding_opportunity"), result.stdout.index("general_news"))
        self.assertIn("Matched keyword:", result.stdout)

    def test_rank_empty_database(self):
        result = self.run_cli("rank")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No signals stored yet.", result.stdout)

if __name__ == "__main__":
    unittest.main()
