import asyncio
import time
from collections import defaultdict


class RateLimiter:
    def __init__(self):
        self._last_call = defaultdict(float)
        self._lock = asyncio.Lock()

    async def wait(self, key, min_interval):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call[key]
            wait_time = max(0, min_interval - elapsed)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self._last_call[key] = time.monotonic()


limiter = RateLimiter()
