from typing import Optional, Callable


class _MockQuery:
    def __init__(self, results):
        self._results = results
        self._filters = []

    def filter(self, condition):
        self._filters.append(condition)
        return self

    def first(self):
        return self._results[0] if self._results else None

    def __iter__(self):
        return iter(self._results)


class _MockSession:
    def __init__(self, on_commit: Optional[Callable[[], None]] = None):
        self._added = []
        self.commits = 0
        self.flushes = 0
        self.rollbacks = 0
        self.closed = False
        self._on_commit = on_commit
        self._deletes= []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            self.close()
        return True

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
        self.flushes+= 1
