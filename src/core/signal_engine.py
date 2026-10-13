from core.models import EvidenceSignal
from output.reporter import make_report

def run_signals(signals):
    if not isinstance(signals, list):
        raise TypeError("signals must be a list")
    unique = {}
    for signal in signals:
        if not isinstance(signal, EvidenceSignal):
            raise TypeError("expected EvidenceSignal")
        key = signal.signal_id
        if key in unique and unique[key] != signal:
            raise ValueError("conflicting signal ID: " + key)
        unique[key] = signal
    items = []
    for signal in unique.values():
        items.append({"signal_id": signal.signal_id, "title": signal.title.strip(), "source_name": signal.source_name, "source_url": signal.source_url, "discovered_at": signal.discovered_at.isoformat(), "description": signal.description, "country_code": signal.country_code})
    return make_report(items)
