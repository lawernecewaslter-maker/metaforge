from app.analysis import evaluate_trade
from app.models import ItemSide


def test_profitable_trade_low_risk_accept() -> None:
    giving = [ItemSide(name="A", current_lowest_listing=100, avg_7d=98, liquidity_score=8)]
    receiving = [ItemSide(name="B", current_lowest_listing=120, avg_7d=119, liquidity_score=8)]
    result = evaluate_trade(giving, receiving)
    assert result.net_value_delta > 0
    assert result.risk_level == "Low"
    assert result.decision == "ACCEPT"


def test_negative_delta_decline() -> None:
    giving = [ItemSide(name="A", current_lowest_listing=150, liquidity_score=7)]
    receiving = [ItemSide(name="B", current_lowest_listing=100, liquidity_score=7)]
    result = evaluate_trade(giving, receiving)
    assert result.net_value_delta < 0
    assert result.decision == "DECLINE"
