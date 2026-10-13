import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from core.models import EvidenceSignal


class EvidenceSignalTests(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            "signal_id": "test-001",
            "title": "Example opportunity",
            "source_name": "Example Source",
            "source_url": "https://example.com/opportunity",
            "discovered_at": datetime.now(timezone.utc),
            "description": "Test evidence",
            "country_code": "ma",
        }

    def test_valid_signal(self):
        signal = EvidenceSignal(**self.valid_data)
        self.assertEqual(signal.country_code, "MA")
        self.assertEqual(signal.signal_id, "test-001")

    def test_rejects_blank_title(self):
        data = {**self.valid_data, "title": "  "}
        with self.assertRaises(ValueError):
            EvidenceSignal(**data)

    def test_rejects_invalid_url(self):
        data = {**self.valid_data, "source_url": "file:///example"}
        with self.assertRaises(ValueError):
            EvidenceSignal(**data)

    def test_rejects_datetime_without_timezone(self):
        data = {
            **self.valid_data,
            "discovered_at": datetime(2026, 1, 1),
        }
        with self.assertRaises(ValueError):
            EvidenceSignal(**data)

    def test_rejects_invalid_country_code(self):
        data = {**self.valid_data, "country_code": "MOR"}
        with self.assertRaises(ValueError):
            EvidenceSignal(**data)


if __name__ == "__main__":
    unittest.main()
