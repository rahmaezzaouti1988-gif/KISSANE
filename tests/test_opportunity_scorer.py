import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.models import EvidenceSignal
from processor.opportunity_scorer import score_signal


def make_signal(title, description=""):
    return EvidenceSignal(
        signal_id="score-test-001",
        title=title,
        source_name="Test Source",
        source_url="https://example.com/test",
        discovered_at=datetime(2026, 10, 13, tzinfo=timezone.utc),
        description=description,
    )


class OpportunityScorerTests(unittest.TestCase):
    def test_procurement_keyword_in_title(self):
        result = score_signal(make_signal("Open call for tenders"))
        self.assertEqual(result["category"], "procurement_opportunity")
        self.assertEqual(result["score"], 90)

    def test_funding_keyword(self):
        result = score_signal(make_signal("New grant opportunity"))
        self.assertEqual(result["category"], "funding_opportunity")

    def test_market_signal_in_description(self):
        result = score_signal(make_signal("Water update", "New infrastructure investment"))
        self.assertEqual(result["category"], "market_signal")
        self.assertEqual(result["score"], 55)

    def test_regulatory_signal(self):
        result = score_signal(make_signal("New directive announced"))
        self.assertEqual(result["category"], "regulatory_signal")

    def test_general_news_gets_low_score(self):
        result = score_signal(make_signal("Speech on disaster risk management"))
        self.assertEqual(result["category"], "general_news")
        self.assertEqual(result["score"], 10)

    def test_procurement_takes_priority_over_funding(self):
        result = score_signal(make_signal("Funding call for tenders"))
        self.assertEqual(result["category"], "procurement_opportunity")

    def test_requires_human_review(self):
        result = score_signal(make_signal("Public tender announced"))
        self.assertTrue(result["requires_human_review"])

    def test_rejects_invalid_input(self):
        with self.assertRaises(TypeError):
            score_signal("not a signal")


if __name__ == "__main__":
    unittest.main()
