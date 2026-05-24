from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Color = Literal["red", "black", "white"]


class Spin(BaseModel):
    color: Color
    source: str = "manual"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Strategy(BaseModel):
    id: str
    name: str
    pattern: list[Color]
    entry_color: Color
    confidence: float = 0.70
    gales: int = 2
    enabled: bool = True
    cover_white: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class Signal(BaseModel):
    strategy_id: str
    strategy_name: str
    pattern: list[Color]
    entry_color: Color
    confidence: float
    gales: int
    cover_white: bool = False
    reason: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SignalResult(BaseModel):
    strategy_id: str
    strategy_name: str
    status: Literal["win", "gale_win", "loss", "white_win"]
    attempts_used: int
    resolved_color: Color
    resolved_at: datetime = Field(default_factory=datetime.utcnow)


class ManualSpinRequest(BaseModel):
    color: str
    source: str = "manual"