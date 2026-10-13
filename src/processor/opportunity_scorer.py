import re
from core.models import EvidenceSignal

RULES = (
    ("procurement_opportunity", 80, ("invitation to tender", "call for tenders", "request for proposals", "call for proposals", "contract notice", "public contract", "procurement", "tender", "bidding")),
    ("funding_opportunity", 75, ("funding opportunity", "financial support", "grant", "funding", "subsidy")),
    ("market_signal", 55, ("commercial partnership", "market entry", "supply chain", "investment", "investments", "expansion", "infrastructure", "new market")),
    ("regulatory_signal", 45, ("regulation", "directive", "compliance", "consultation", "legislation", "regulatory")),
)


def _contains_term(text, term):
    pattern = r"(?<!\\w)" + re.escape(term) + r"(?!\\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def score_signal(signal):
    if not isinstance(signal, EvidenceSignal):
        raise TypeError("signal must be an EvidenceSignal")

    title = " ".join(signal.title.split()).casefold()
    description = " ".join(signal.description.split()).casefold()
    matches = []

    for category, base_score, terms in RULES:
        for term in terms:
            in_title = _contains_term(title, term)
            in_description = _contains_term(description, term)
            if in_title or in_description:
                score = base_score + (10 if in_title else 0)
                matches.append((score, category, term, in_title))

    if not matches:
        return {
            "signal_id": signal.signal_id,
            "title": signal.title,
            "category": "general_news",
            "score": 10,
            "reasons": ["No configured commercial keywords matched."],
            "requires_human_review": True,
        }

    score, category, term, in_title = max(
        matches, key=lambda item: (item[0], len(item[2]))
    )
    return {
        "signal_id": signal.signal_id,
        "title": signal.title,
        "category": category,
        "score": score,
        "reasons": ["Matched keyword: {}".format(term)],
        "requires_human_review": True,
    }
