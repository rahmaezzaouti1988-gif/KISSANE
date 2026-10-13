from datetime import datetime
from pathlib import Path
import sqlite3
from core.models import EvidenceSignal


class SignalStore:
    def __init__(self, database_path):
        if database_path != ":memory:":
            path = Path(database_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            database_path = str(path)
        self._connection = sqlite3.connect(database_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("CREATE TABLE IF NOT EXISTS signals (signal_id TEXT PRIMARY KEY, title TEXT NOT NULL, source_name TEXT NOT NULL, source_url TEXT NOT NULL, discovered_at TEXT NOT NULL, description TEXT NOT NULL, country_code TEXT)")
        self._connection.commit()

    @staticmethod
    def _values(signal):
        if not isinstance(signal, EvidenceSignal):
            raise TypeError("signal must be an EvidenceSignal")
        return (signal.signal_id, signal.title, signal.source_name, signal.source_url, signal.discovered_at.isoformat(), signal.description, signal.country_code)

    def save(self, signal):
        values = self._values(signal)
        existing = self._connection.execute("SELECT signal_id, title, source_name, source_url, discovered_at, description, country_code FROM signals WHERE signal_id = ?", (signal.signal_id,)).fetchone()
        if existing is not None:
            if tuple(existing) != values:
                raise ValueError("conflicting signal ID: " + signal.signal_id)
            return False
        self._connection.execute("INSERT INTO signals VALUES (?, ?, ?, ?, ?, ?, ?)", values)
        self._connection.commit()
        return True

    @staticmethod
    def _from_row(row):
        return EvidenceSignal(signal_id=row["signal_id"], title=row["title"], source_name=row["source_name"], source_url=row["source_url"], discovered_at=datetime.fromisoformat(row["discovered_at"]), description=row["description"], country_code=row["country_code"])

    def get(self, signal_id):
        row = self._connection.execute("SELECT * FROM signals WHERE signal_id = ?", (signal_id,)).fetchone()
        return None if row is None else self._from_row(row)

    def list_all(self):
        rows = self._connection.execute("SELECT * FROM signals ORDER BY discovered_at, signal_id").fetchall()
        return [self._from_row(row) for row in rows]

    def close(self):
        self._connection.close()
