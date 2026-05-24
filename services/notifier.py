from __future__ import annotations

import requests


class TelegramNotifier:
    def __init__(self, bot_token: str = "", chat_id: str = ""):
        self.bot_token = bot_token
        self.chat_id = chat_id

    @property
    def enabled(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def _send(self, text: str) -> None:
        if not self.enabled:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        try:
            requests.post(
                url,
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                },
                timeout=10,
            )
        except Exception:
            pass

    def send_signal(self, signal) -> None:
        text = (
            f"🎯 SINAL\n"
            f"Estratégia: {signal.strategy_name}\n"
            f"Padrão: {' > '.join(signal.pattern)}\n"
            f"Entrada: {signal.entry_color}\n"
            f"Gales: {signal.gales}\n"
            f"Confiança: {round(signal.confidence * 100, 1)}%"
        )
        self._send(text)

    def send_result(self, result) -> None:
        icon = {
            "win": "✅",
            "gale_win": "🟡",
            "white_win": "⚪",
            "loss": "❌",
        }.get(result.status, "ℹ️")

        text = (
            f"{icon} RESULTADO\n"
            f"Estratégia: {result.strategy_name}\n"
            f"Status: {result.status}\n"
            f"Tentativas: {result.attempts_used}\n"
            f"Cor saída: {result.resolved_color}"
        )
        self._send(text)