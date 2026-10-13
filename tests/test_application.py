import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.application import KissaneApplication
from core.models import EvidenceSignal


def make_signal(signal_id="signal-001", title="Demo"):
    return EvidenceSignal(signal_id, title, "Example", "https://example.com", datetime(2026, 10, 13, tzinfo=timezone.utc))


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.db_path = str(Path(self.temp.name) / "data" / "signals.sqlite")

    def tearDown(self):
        self.temp.cleanup()

    def test_process_and_list_signals(self):
        signal = make_signal()
        with KissaneApplication(self.db_path) as app:
            result = app.process_signals([signal])
            self.assertEqual(result["count"], 1)
            self.assertEqual(app.list_signals(), [signal])

    def test_signals_persist_after_reopening_app(self):
        signal = make_signal()
        with KissaneApplication(self.db_path) as app:
            app.process_signals([signal])
        with KissaneApplication(self.db_path) as app:
            self.assertEqual(app.list_signals(), [signal])

    def test_duplicate_is_stored_once(self):
        signal = make_signal()
        with KissaneApplication(self.db_path) as app:
            result = app.process_signals([signal, signal])
            self.assertEqual(result["count"], 1)
            self.assertEqual(len(app.list_signals()), 1)

    def test_conflict_does_not_partially_save_batch(self):
        with KissaneApplication(self.db_path) as app:
            app.process_signals([make_signal("existing", "Original")])
            batch = [make_signal("new", "New"), make_signal("existing", "Changed")]
            with self.assertRaises(ValueError):
                app.process_signals(batch)
            self.assertEqual([s.signal_id for s in app.list_signals()], ["existing"])

if __name__ == "__main__":
    unittest.main()
