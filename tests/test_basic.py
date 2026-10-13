from pathlib import Path
import sys
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from core.engine import run
from processor.processor import process_data


class EngineTests(unittest.TestCase):
    def test_default_pipeline(self):
        result = run()
        self.assertEqual(result["count"], 3)
        self.assertEqual(
            result["items"],
            ["SIGNAL 1", "SIGNAL 2", "SIGNAL 3"]
        )

    def test_normalizes_and_removes_duplicates(self):
        result = run([" Alpha  Beta ", "alpha beta", "", "Gamma"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["items"], ["ALPHA BETA", "GAMMA"])

    def test_rejects_non_list_input(self):
        with self.assertRaises(TypeError):
            process_data("signal")

    def test_rejects_non_string_items(self):
        with self.assertRaises(TypeError):
            process_data(["signal", 123])


if __name__ == "__main__":
    unittest.main()
