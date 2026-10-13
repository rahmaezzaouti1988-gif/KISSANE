import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.models import EvidenceSignal
from core.signal_engine import run_signals

def make_signal(title="Demo"):
    return EvidenceSignal("signal-001", title, "Example", "https://example.com", datetime.now(timezone.utc))

class SignalEngineTests(unittest.TestCase):
    def test_accepts_signal(self):
        self.assertEqual(run_signals([make_signal()])["count"], 1)

    def test_removes_duplicate(self):
        signal = make_signal()
        self.assertEqual(run_signals([signal, signal])["count"], 1)

    def test_rejects_non_list(self):
        with self.assertRaises(TypeError):
            run_signals("invalid")

    def test_rejects_invalid_item(self):
        with self.assertRaises(TypeError):
            run_signals(["invalid"])

    def test_rejects_conflicting_id(self):
        with self.assertRaises(ValueError):
            run_signals([make_signal("A"), make_signal("B")])

if __name__ == "__main__":
    unittest.main()
