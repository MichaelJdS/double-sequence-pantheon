from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any

from core.models import Signal, SignalResult, Spin


@dataclass
class PendingSignal:
    signal: Signal
    attempts_used: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


class AppState:
    def __init__(self, max_history: int = 200, max_signals: int = 100):
        self._lock = Lock()
        self.spins: deque[Spin] = deque(maxlen=max_history)
        self.signals: deque[dict[str, Any]] = deque(maxlen=max_signals)
        self.pending_signals: list[PendingSignal] = []
        self.last_emitted_signature: str | None = None
        self.stats = {
            "signals_total": 0,
            "wins": 0,
            "gale_wins": 0,
            "white_wins": 0,
            "losses": 0,
        }

    def add_spin(self, spin: Spin) -> None:
        with self._lock:
            self.spins.append(spin)

    def get_history_colors(self) -> list[str]:
        with self._lock:
            return [spin.color for spin in self.spins]

    def should_emit(self, signature: str) -> bool:
        with self._lock:
            if self.last_emitted_signature == signature:
                return False
            self.last_emitted_signature = signature
            return True

    def register_signal(self, signal: Signal) -> None:
        with self._lock:
            self.pending_signals.append(PendingSignal(signal=signal))
            self.signals.appendleft(
                {
                    "type": "signal",
                    "payload": signal.model_dump(mode="json"),
                }
            )
            self.stats["signals_total"] += 1

    def resolve_pending(self, spin: Spin) -> list[SignalResult]:
        results: list[SignalResult] = []
        remaining: list[PendingSignal] = []

        with self._lock:
            for pending in self.pending_signals:
                signal = pending.signal
                hit_main_color = spin.color == signal.entry_color
                hit_white = spin.color == "white" and signal.cover_white

                if hit_white:
                    result = SignalResult(
                        strategy_id=signal.strategy_id,
                        strategy_name=signal.strategy_name,
                        status="white_win",
                        attempts_used=pending.attempts_used,
                        resolved_color=spin.color,
                    )
                    results.append(result)
                    self.signals.appendleft({"type": "result", "payload": result.model_dump(mode="json")})
                    self.stats["white_wins"] += 1
                    continue

                if hit_main_color:
                    status = "win" if pending.attempts_used == 0 else "gale_win"
                    result = SignalResult(
                        strategy_id=signal.strategy_id,
                        strategy_name=signal.strategy_name,
                        status=status,
                        attempts_used=pending.attempts_used,
                        resolved_color=spin.color,
                    )
                    results.append(result)
                    self.signals.appendleft({"type": "result", "payload": result.model_dump(mode="json")})
                    if status == "win":
                        self.stats["wins"] += 1
                    else:
                        self.stats["gale_wins"] += 1
                    continue

                if pending.attempts_used < signal.gales:
                    pending.attempts_used += 1
                    remaining.append(pending)
                    continue

                result = SignalResult(
                    strategy_id=signal.strategy_id,
                    strategy_name=signal.strategy_name,
                    status="loss",
                    attempts_used=pending.attempts_used,
                    resolved_color=spin.color,
                )
                results.append(result)
                self.signals.appendleft({"type": "result", "payload": result.model_dump(mode="json")})
                self.stats["losses"] += 1

            self.pending_signals = remaining

        return results

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            total_closed = (
                self.stats["wins"]
                + self.stats["gale_wins"]
                + self.stats["white_wins"]
                + self.stats["losses"]
            )
            accuracy = 0.0
            if total_closed > 0:
                accuracy = (
                    self.stats["wins"]
                    + self.stats["gale_wins"]
                    + self.stats["white_wins"]
                ) / total_closed * 100.0

            return {
                "stats": {
                    **self.stats,
                    "accuracy": round(accuracy, 2),
                    "pending": len(self.pending_signals),
                    "spins_total": len(self.spins),
                },
                "spins": [s.model_dump(mode="json") for s in list(self.spins)][-30:][::-1],
                "events": list(self.signals)[:30],
            }