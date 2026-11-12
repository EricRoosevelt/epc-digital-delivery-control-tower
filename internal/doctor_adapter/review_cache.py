"""An LRU of immutable serialized payloads; hashing/JSON/native work stays outside its lock."""

from __future__ import annotations

from collections import OrderedDict
import threading


class SerializedReviewCache:
    def __init__(self, max_entries: int, max_bytes: int):
        if max_entries < 0 or max_bytes < 0:
            raise ValueError("Cache limits cannot be negative.")
        self.max_entries, self.max_bytes = max_entries, max_bytes
        self.lock = threading.RLock()
        self._entries = OrderedDict()
        self._bytes = 0
        self._hits = self._misses = self._evictions = self._oversized = self._clears = 0

    def get(self, kind, review_id):
        key = (kind, review_id)
        with self.lock:
            entry = self._entries.get(key)
            if entry is None:
                self._misses += 1
                return None
            self._hits += 1
            self._entries.move_to_end(key)
            return entry[0]

    def admit(self, prepared):
        """prepared maps keys to (bytes, precomputed SHA-256); validate atomically."""
        retired = []
        with self.lock:
            for key, (_, checksum) in prepared.items():
                prior = self._entries.get(key)
                if prior is not None and prior[1] != checksum:
                    raise ValueError(
                        "A different review payload already uses this session identity."
                    )
            for key, entry in prepared.items():
                payload = entry[0]
                if key in self._entries:
                    self._entries.move_to_end(key)
                    continue
                if not self.max_entries or len(payload) > self.max_bytes:
                    self._oversized += 1
                    continue
                while self._entries and (
                    len(self._entries) >= self.max_entries
                    or self._bytes + len(payload) > self.max_bytes
                ):
                    _, removed = self._entries.popitem(last=False)
                    self._bytes -= len(removed[0])
                    self._evictions += 1
                    retired.append(removed)
                self._entries[key] = entry
                self._bytes += len(payload)
        # Retire large byte buffers only after releasing the cache lock.
        retired.clear()

    def clear(self, review_id=None):
        retired = []
        with self.lock:
            for key in list(self._entries):
                if review_id is None or key[1] == review_id:
                    entry = self._entries.pop(key)
                    self._bytes -= len(entry[0])
                    retired.append(entry)
            self._clears += 1
        retired.clear()
        return self.stats()

    def stats(self):
        with self.lock:
            report_bytes = sum(
                len(entry[0]) for key, entry in self._entries.items() if key[0] == "report"
            )
            geometry_bytes = self._bytes - report_bytes
            return {
                "entries": len(self._entries),
                "bytes": self._bytes,
                "reports": sum(key[0] == "report" for key in self._entries),
                "geometries": sum(key[0] == "geometry" for key in self._entries),
                "report_bytes": report_bytes,
                "geometry_bytes": geometry_bytes,
                "max_entries": self.max_entries,
                "max_bytes": self.max_bytes,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "oversized": self._oversized,
                "clears": self._clears,
            }
