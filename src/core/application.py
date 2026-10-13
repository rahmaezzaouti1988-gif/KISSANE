from pathlib import Path
from core.signal_engine import run_and_store_signals
from core.signal_store import SignalStore

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "data" / "kissane.sqlite3"


class KissaneApplication:
    def __init__(self, database_path=None):
        path = DEFAULT_DATABASE_PATH if database_path is None else database_path
        self.database_path = str(path)
        self.store = SignalStore(self.database_path)
        self._closed = False

    def _ensure_open(self):
        if self._closed:
            raise RuntimeError("application is closed")

    def process_signals(self, signals):
        self._ensure_open()
        return run_and_store_signals(signals, self.store)

    def list_signals(self):
        self._ensure_open()
        return self.store.list_all()

    def close(self):
        if not self._closed:
            self.store.close()
            self._closed = True

    def __enter__(self):
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
