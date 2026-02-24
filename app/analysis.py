from __future__ import annotations

from .models import ItemSide, TradeEvaluationResponse


def _effective_value(item: ItemSide) -> float:
    baseline = item.current_lowest_listing
    if item.avg_7d is not None:
        baseline = (baseline * 0.6) + (item.avg_7d * 0.4)
    momentum_factor = 1 + (item.recent_trend_pct / 100.0) * 0.2
    liquidity_factor = 0.8 + (item.liquidity_score / 10.0) * 0.4
    return baseline * momentum_factor * liquidity_factor


def evaluate_trade(giving: list[ItemSide], receiving: list[ItemSide]) -> TradeEvaluationResponse:
    giving_value = sum(_effective_value(i) for i in giving)
    receiving_value = sum(_effective_value(i) for i in receiving)
    delta = receiving_value - giving_value

    all_items = giving + receiving
    avg_liquidity = (sum(i.liquidity_score for i in all_items) / len(all_items)) if all_items else 0.0

    risk = "High" if avg_liquidity < 3.5 else "Medium" if avg_liquidity < 6.5 else "Low"

    if delta > 0 and risk == "Low":
        decision = "ACCEPT"
    elif delta > 0:
        decision = "HOLD"
    else:
        decision = "DECLINE"

    flip = "High" if delta > 0 and avg_liquidity >= 6 else "Moderate" if delta > 0 else "Low"
    hold = "High" if risk == "Low" and delta >= 0 else "Moderate" if delta >= 0 else "Low"

    return TradeEvaluationResponse(
        net_value_delta=round(delta, 2),
        risk_level=risk,
        flip_potential=flip,
        holding_potential=hold,
        decision=decision,
        rationale="Decision balances modeled value delta with liquidity-derived risk.",
    )
