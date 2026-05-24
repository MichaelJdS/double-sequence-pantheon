from __future__ import annotations

from core.models import Signal, Spin
from core.state import AppState
from core.strategy_loader import StrategyRepository, normalize_color
from services.notifier import TelegramNotifier


class SequenceEngine:
    def __init__(
        self,
        repository: StrategyRepository,
        state: AppState,
        notifier: TelegramNotifier,
    ):
        self.repository = repository
        self.state = state
        self.notifier = notifier

    def _build_signal(self, strategy, history: list[str]) -> Signal | None:
        if len(history) < len(strategy.pattern):
            return None

        tail = history[-len(strategy.pattern):]
        if tail != strategy.pattern:
            return None

        reason = f"Padrão {' > '.join(strategy.pattern)} encontrado; entrada sugerida em {strategy.entry_color}"
        return Signal(
            strategy_id=strategy.id,
            strategy_name=strategy.name,
            pattern=strategy.pattern,
            entry_color=strategy.entry_color,
            confidence=strategy.confidence,
            gales=strategy.gales,
            cover_white=strategy.cover_white,
            reason=reason,
        )

    def evaluate(self) -> Signal | None:
        history = self.state.get_history_colors()
        for strategy in self.repository.all():
            signal = self._build_signal(strategy, history)
            if signal:
                signature = f"{strategy.id}:{'-'.join(history[-len(strategy.pattern):])}:{len(history)}"
                if self.state.should_emit(signature):
                    return signal
        return None

    def handle_color(self, color: str, source: str = "manual") -> dict:
        normalized = normalize_color(color)
        if normalized is None:
            raise ValueError(f"Cor inválida: {color}")

        spin = Spin(color=normalized, source=source)
        self.state.add_spin(spin)

        resolved = self.state.resolve_pending(spin)
        for result in resolved:
            self.notifier.send_result(result)

        signal = self.evaluate()
        if signal:
            self.state.register_signal(signal)
            self.notifier.send_signal(signal)

        return {
            "spin": spin.model_dump(mode="json"),
            "resolved": [item.model_dump(mode="json") for item in resolved],
            "signal": signal.model_dump(mode="json") if signal else None,
        }