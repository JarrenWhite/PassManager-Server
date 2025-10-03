import os
import sys
from typing import Optional, Callable

from sqlalchemy.exc import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database_setup import DatabaseSetup


class _FakeQuery:
    def __init__(self, results):
        self._results = results

    def filter(self, condition):
        return self

    def first(self):
        return self._results[0] if self._results else None


class _FakeSession:
    def __init__(self, on_commit: Optional[Callable[[], None]] = None):
        self._added = []
        self.commits = 0
        self.rollbacks = 0
        self.closed = False
        self._on_commit = on_commit
        self._deletes= []

    def add(self, obj):
        self._added.append(obj)

    def commit(self):
        self.commits += 1
        if self._on_commit:
            self._on_commit()

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True

    def query(self):
        pass

    def delete(self, obj):
        self._deletes.append(obj)

    def flush(self):
        pass


def _prepare_fake_session(test_class, monkeypatch, exception_message : Optional[str] = None):
    """Prepare a Fake Session with the given exception on commit"""
    if exception_message:
        def raise_exception():
            raise IntegrityError(exception_message, params=None, orig=Exception("Fake exception"))
        test_class._fake_session = _FakeSession(on_commit=raise_exception)
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: test_class._fake_session))
    else:
        test_class._fake_session = _FakeSession()
        monkeypatch.setattr(DatabaseSetup, "get_session", lambda: (lambda: test_class._fake_session))

def _prepare_db_not_initialised_error(monkeypatch):
    def _raise_runtime_error():
        raise RuntimeError("Database not initialised.")
    monkeypatch.setattr(DatabaseSetup, "get_session", lambda: _raise_runtime_error)


def _fake_query_response(monkeypatch, response_list):
    def fake_query(self, model):
        return _FakeQuery(response_list)
    monkeypatch.setattr(_FakeSession, "query", fake_query)