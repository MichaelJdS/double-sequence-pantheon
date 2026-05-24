from __future__ import annotations

import random
import threading
import time
from collections.abc import Callable


class DemoFeed:
    def __init__(self, on_spin: Callable[[str, str], None], interval_seconds: float = 3.0):
        self.on_spin = on_spin
        self.interval_seconds = interval_seconds
        self._running = False
        self._thread = None

    def _next_color(self) -> str:
        roll = random.random()
        if roll < 0.46:
            return "red"
        if roll < 0.92:
            return "black"
        return "white"

    def _loop(self):
        while self._running:
            color = self._next_color()
            try:
                self.on_spin(color, "demo")
            except Exception:
                pass
            time.sleep(self.interval_seconds)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def status(self) -> dict:
        return {
            "running": self._running,
            "interval_seconds": self.interval_seconds,
        }