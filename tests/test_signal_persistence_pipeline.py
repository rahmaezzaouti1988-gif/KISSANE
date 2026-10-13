import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.models import EvidenceSignal
from core.signal_engine import run_and_store_signals
from core.signal_store import SignalStore


def make_signal(signal_id="signal-001", title="Demo"):
    return EvidenceSignal(signal_id, title, "Example", "https://example.com", datetime(2026, 10, 13, tzinfo=timezone.utc))


class PersistencePipelineTests(unittest.TestCase):
    def setUp(self):
        self.store = SignalStore(":memory:")

    def tearDown(self):
        self.store.close()

    def test_processes_and_saves_signal(self):
        signal = make_signal()
        result = run_and_store_signals([signal], self.store)
        self.assertEqual(result["count"], 1)
        self.assertEqual(self.store.get(signal.signal_id), signal)

    def test_duplicate_is_saved_once(self):
        signal = make_signal()
        result = run_and_store_signals([signal, signal], self.store)
        self.assertEqual(result["count"], 1)
        self.assertEqual(len(self.store.list_all()), 1)

    def test_database_conflict_does_not_save_other_signals(self):
        self.store.save(make_signal("existing", "Original"))
        new_signal = make_signal("new", "New")
        conflict = make_signal("existing", "Changed")
        with self.assertRaises(ValueError):
            run_and_store_signals([new_signal, conflict], self.store)
        self.assertIsNone(self.store.get("new"))

    def test_invalid_input_is_not_saved(self):
        with self.assertRaises(TypeError):
            run_and_store_signals(["invalid"], self.store)
        self.assertEqual(self.store.list_all(), [])


if __name__ == "__main__":
    unittest.main()
