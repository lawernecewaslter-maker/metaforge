from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ItemSide:
    name: str
    current_lowest_listing: float
    avg_7d: float | None = None
    recent_trend_pct: float = 0.0
    liquidity_score: float = 5.0


@dataclass
class TradeEvaluationResponse:
    net_value_delta: float
    risk_level: str
    flip_potential: str
    holding_potential: str
    decision: str
    rationale: str
