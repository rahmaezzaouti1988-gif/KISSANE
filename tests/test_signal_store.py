import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.models import EvidenceSignal
from core.signal_store import SignalStore

def make_signal(signal_id="signal-001", title="Demo"):
    return EvidenceSignal(signal_id, title, "Example", "https://example.com", datetime(2026, 10, 13, tzinfo=timezone.utc))

class SignalStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.db_path = str(Path(self.temp.name) / "signals.sqlite")
        self.store = SignalStore(self.db_path)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_save_and_get(self):
        signal = make_signal()
        self.assertTrue(self.store.save(signal))
        self.assertEqual(self.store.get(signal.signal_id), signal)

    def test_identical_duplicate_is_ignored(self):
        signal = make_signal()
        self.assertTrue(self.store.save(signal))
        self.assertFalse(self.store.save(signal))
        self.assertEqual(len(self.store.list_all()), 1)

    def test_conflicting_id_is_rejected(self):
        self.store.save(make_signal())
        with self.assertRaises(ValueError):
            self.store.save(make_signal(title="Different"))

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(TypeError):
            self.store.save("not a signal")

    def test_data_survives_reopen(self):
        signal = make_signal()
        self.store.save(signal)
        self.store.close()
        self.store = SignalStore(self.db_path)
        self.assertEqual(self.store.get(signal.signal_id), signal)

if __name__ == "__main__":
    unittest.main()
