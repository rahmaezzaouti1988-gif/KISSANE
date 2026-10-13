import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input.rss_collector import parse_rss

FEED_URL = "https://example.com/feed.xml"
RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Example Feed</title>
<item><title>Opportunity &amp; Update</title>
<link>https://example.com/items/1</link>
<guid>item-001</guid>
<description>Useful &lt;b&gt;details&lt;/b&gt;</description>
</item></channel></rss>"""

ATOM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>Atom Example</title>
<entry><title>New Market Update</title>
<link href="https://example.com/atom/1" rel="alternate"/>
<id>atom-001</id></entry></feed>"""

class RSSCollectorTests(unittest.TestCase):
    def test_parses_rss_item(self):
        signals = parse_rss(RSS_XML, FEED_URL, discovered_at=datetime(2026, 10, 13, tzinfo=timezone.utc))
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].title, "Opportunity & Update")
        self.assertEqual(signals[0].source_name, "Example Feed")
        self.assertEqual(signals[0].description, "Useful details")
        self.assertEqual(signals[0].source_url, "https://example.com/items/1")

    def test_parses_atom_item(self):
        signals = parse_rss(ATOM_XML, FEED_URL)
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].title, "New Market Update")
        self.assertEqual(signals[0].source_name, "Atom Example")
        self.assertEqual(signals[0].source_url, "https://example.com/atom/1")

    def test_signal_id_is_deterministic(self):
        first = parse_rss(RSS_XML, FEED_URL)
        second = parse_rss(RSS_XML, FEED_URL)
        self.assertEqual(first[0].signal_id, second[0].signal_id)

    def test_rejects_malformed_xml(self):
        with self.assertRaises(ValueError):
            parse_rss("<rss><channel>", FEED_URL)

    def test_rejects_unsupported_xml(self):
        with self.assertRaises(ValueError):
            parse_rss("<html />", FEED_URL)

    def test_rejects_invalid_feed_url(self):
        with self.assertRaises(ValueError):
            parse_rss(RSS_XML, "file:///feed.xml")

    def test_rejects_invalid_limit(self):
        with self.assertRaises(ValueError):
            parse_rss(RSS_XML, FEED_URL, limit=0)

if __name__ == "__main__":
    unittest.main()
