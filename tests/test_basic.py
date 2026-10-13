from pathlib import Path
import sys
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from core.engine import run


class EngineTests(unittest.TestCase):
    def test_run_returns_three_uppercase_signals(self):
        result = run()
        self.assertEqual(result["count"], 3)
        self.assertEqual(
            result["items"],
            ["SIGNAL 1", "SIGNAL 2", "SIGNAL 3"]
        )


if __name__ == "__main__":
    unittest.main()
