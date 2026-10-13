from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class EvidenceSignal:
    """A traceable observation collected from an external source."""

    signal_id: str
    title: str
    source_name: str
    source_url: str
    discovered_at: datetime
    description: str = ""
    country_code: str | None = None

    def __post_init__(self):
        for field_name in ("signal_id", "title", "source_name"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

        if not isinstance(self.source_url, str):
            raise ValueError("source_url must be a string")

        url = self.source_url.strip()
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("source_url must be a valid HTTP or HTTPS URL")

        object.__setattr__(self, "source_url", url)

        if (
            not isinstance(self.discovered_at, datetime)
            or self.discovered_at.tzinfo is None
            or self.discovered_at.utcoffset() is None
        ):
            raise ValueError("discovered_at must include a timezone")

        if not isinstance(self.description, str):
            raise ValueError("description must be a string")

        if self.country_code is not None:
            if not isinstance(self.country_code, str):
                raise ValueError("country_code must be a two-letter code")

            code = self.country_code.strip().upper()

            if len(code) != 2 or not code.isascii() or not code.isalpha():
                raise ValueError("country_code must be a two-letter code")

            object.__setattr__(self, "country_code", code)
