import time
import asyncio
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl: float = 10.0):
        self._ttl = ttl
        self._data: dict[str, tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key in self._data:
                value, expires = self._data[key]
                if time.monotonic() < expires:
                    return value
                del self._data[key]
            return None

    async def set(self, key: str, value: Any):
        async with self._lock:
            self._data[key] = (value, time.monotonic() + self._ttl)

    async def delete(self, key: str):
        async with self._lock:
            self._data.pop(key, None)

    async def clear(self):
        async with self._lock:
            self._data.clear()
