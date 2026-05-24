from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from config import ALLOW_WHITE_PROTECTION, DEFAULT_CONFIDENCE, DEFAULT_GALES
from core.models import Strategy


def normalize_color(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip().lower()

    mapping = {
        "red": "red",
        "r": "red",
        "v": "red",
        "vermelho": "red",
        "black": "black",
        "preto": "black",
        "p": "black",
        "white": "white",
        "branco": "white",
        "b": "white",
        "0": "white",
    }
    return mapping.get(text)


def normalize_pattern(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        items = value
    else:
        text = str(value)
        for token in ["->", ">", "|", ";", "/", ","]:
            text = text.replace(token, " ")
        items = [chunk for chunk in text.split() if chunk]

    result = []
    for item in items:
        color = normalize_color(item)
        if color:
            result.append(color)
    return result


def find_first(data: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return default


def extract_strategy_items(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]

    if isinstance(raw, dict):
        for key in ["strategies", "sequence_strategies", "items", "data"]:
            if isinstance(raw.get(key), list):
                return [item for item in raw[key] if isinstance(item, dict)]

        values = list(raw.values())
        if values and all(isinstance(v, dict) for v in values):
            merged = []
            for key, value in raw.items():
                item = dict(value)
                item.setdefault("id", key)
                item.setdefault("name", key)
                merged.append(item)
            return merged

    return []


class StrategyRepository:
    def __init__(self, path: Path, strategies: list[Strategy]):
        self.path = Path(path)
        self._strategies = strategies

    @classmethod
    def from_file(cls, path: Path) -> "StrategyRepository":
        path = Path(path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("[]", encoding="utf-8")
        raw = json.loads(path.read_text(encoding="utf-8"))
        strategies = cls._parse(raw)
        return cls(path=path, strategies=strategies)

    @staticmethod
    def _parse(raw: Any) -> list[Strategy]:
        items = extract_strategy_items(raw)
        parsed: list[Strategy] = []

        for index, item in enumerate(items, start=1):
            pattern = normalize_pattern(
                find_first(item, ["pattern", "sequence", "sequencia", "trigger", "trigger_pattern"])
            )
            entry_color = normalize_color(
                find_first(item, ["entry_color", "prediction", "next_color", "saida", "cor_entrada"])
            )

            if not pattern or not entry_color:
                continue

            confidence = find_first(item, ["confidence", "score", "assertividade"], DEFAULT_CONFIDENCE)
            gales = find_first(item, ["gales", "martingale", "gale"], DEFAULT_GALES)
            enabled = bool(find_first(item, ["enabled", "active", "ativo"], True))
            cover_white = bool(find_first(item, ["cover_white", "white_protection", "proteger_branco"], ALLOW_WHITE_PROTECTION))

            strategy = Strategy(
                id=str(find_first(item, ["id"], f"seq_{index}")),
                name=str(find_first(item, ["name", "nome"], f"Estratégia {index}")),
                pattern=pattern,
                entry_color=entry_color,
                confidence=float(confidence),
                gales=int(gales),
                enabled=enabled,
                cover_white=cover_white,
                metadata=item,
            )
            parsed.append(strategy)

        return parsed

    def all(self) -> list[Strategy]:
        return sorted(
            [s for s in self._strategies if s.enabled],
            key=lambda s: (len(s.pattern), s.confidence),
            reverse=True,
        )

    def count(self) -> int:
        return len(self._strategies)

    def reload(self) -> int:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self._strategies = self._parse(raw)
        return len(self._strategies)