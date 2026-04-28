import os
import random
from itertools import cycle


class ProxyRotator:
    def __init__(self):
        proxies_env = os.getenv("PROXIES", "")
        self._proxies = [p.strip() for p in proxies_env.split(",") if p.strip()]
        self._cycle = cycle(self._proxies) if self._proxies else None

    def get_proxy(self):
        if not self._cycle:
            return None
        return next(self._cycle)

    def get_random(self):
        if not self._proxies:
            return None
        return random.choice(self._proxies)

    @property
    def has_proxies(self):
        return bool(self._proxies)


rotator = ProxyRotator()
