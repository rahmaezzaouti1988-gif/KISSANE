import hashlib
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import urlparse, urljoin
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from core.models import EvidenceSignal

MAX_FEED_BYTES = 5 * 1024 * 1024


class _HTMLText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def _plain_text(value):
    parser = _HTMLText()
    parser.feed(unescape(value or ""))
    parser.close()
    return " ".join(" ".join(parser.parts).split())


def _local_name(tag):
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(element, names):
    for child in list(element):
        if _local_name(child.tag) in names:
            return "".join(child.itertext()).strip()
    return ""


def _valid_http_url(value):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme.lower() in ("http", "https") and bool(parsed.netloc)


def _item_link(entry, feed_url):
    for child in list(entry):
        if _local_name(child.tag) != "link":
            continue
        relation = child.attrib.get("rel", "alternate")
        if relation not in ("", "alternate"):
            continue
        candidate = child.attrib.get("href") or "".join(child.itertext()).strip()
        if candidate:
            candidate = urljoin(feed_url, candidate)
            if _valid_http_url(candidate):
                return candidate
    for name in ("guid", "id"):
        candidate = _child_text(entry, (name,))
        if _valid_http_url(candidate):
            return candidate
    return ""


def parse_rss(xml_data, feed_url, limit=20, discovered_at=None):
    if not _valid_http_url(feed_url):
        raise ValueError("feed_url must be an HTTP or HTTPS URL")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise ValueError("limit must be an integer between 1 and 100")
    if isinstance(xml_data, str):
        xml_data = xml_data.encode("utf-8")
    if not isinstance(xml_data, bytes):
        raise TypeError("xml_data must be bytes or a string")
    if len(xml_data) > MAX_FEED_BYTES:
        raise ValueError("RSS feed exceeds the 5 MB limit")
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as exc:
        raise ValueError("Invalid RSS or Atom XML") from exc

    root_name = _local_name(root.tag)
    if root_name == "rss":
        channel = next((child for child in list(root) if _local_name(child.tag) == "channel"), None)
        if channel is None:
            raise ValueError("RSS channel is missing")
        feed_element = channel
        entries = [child for child in list(channel) if _local_name(child.tag) == "item"]
    elif root_name == "feed":
        feed_element = root
        entries = [child for child in list(root) if _local_name(child.tag) == "entry"]
    else:
        raise ValueError("Unsupported feed format; expected RSS or Atom")

    source_name = _plain_text(_child_text(feed_element, ("title",)))
    if not source_name:
        source_name = urlparse(feed_url).hostname or "RSS source"
    timestamp = discovered_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("discovered_at must include a timezone")

    signals = []
    for entry in entries:
        title = _plain_text(_child_text(entry, ("title",)))
        link = _item_link(entry, feed_url)
        if not title or not link:
            continue
        identity = _child_text(entry, ("guid", "id")) or link
        signal_id = "rss-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
        description = _plain_text(_child_text(entry, ("description", "summary", "content")))
        signals.append(EvidenceSignal(
            signal_id=signal_id,
            title=title,
            source_name=source_name,
            source_url=link,
            discovered_at=timestamp,
            description=description,
        ))
        if len(signals) >= limit:
            break
    return signals


def fetch_rss(feed_url, limit=20, timeout=15):
    if not _valid_http_url(feed_url):
        raise ValueError("feed_url must be an HTTP or HTTPS URL")
    request = Request(feed_url, headers={
        "User-Agent": "KISSANE-RSS-Collector/1.0",
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
    })
    try:
        with urlopen(request, timeout=timeout) as response:
            content = response.read(MAX_FEED_BYTES + 1)
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("Could not fetch RSS feed: {}".format(exc)) from exc
    if len(content) > MAX_FEED_BYTES:
        raise ValueError("RSS feed exceeds the 5 MB limit")
    return parse_rss(content, feed_url, limit=limit)
