from typing import List, Dict
from datetime import datetime, timezone


TAKER_FEE = 0.0006


def format_rate(rate: float) -> str:
    pct = rate * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.4f}%"


def format_profit_after_fees(spread: float, price: float) -> float:
    fees = TAKER_FEE * 2
    net = spread - fees
    return net


def format_arbitrage(item: Dict) -> str:
    symbol = item["symbol"]
    max_info = item["max"]
    min_info = item["min"]
    spread = item["spread"]
    spread_pct = spread * 100
    net_profit = item.get("net_profit", spread)
    net_profit_pct = net_profit * 100

    lines = [
        f"<b>{symbol}</b>",
        f"  {max_info['exchange']}: {format_rate(max_info['funding_rate'])}",
        f"  {min_info['exchange']}: {format_rate(min_info['funding_rate'])}",
        f"  Spread: <b>{spread_pct:.4f}%</b>",
        f"  After fees: <b>{net_profit_pct:.4f}%</b>",
        f"  Long: <b>{min_info['exchange']}</b>",
        f"  Short: <b>{max_info['exchange']}</b>",
    ]
    return "\n".join(lines)


def format_top_list(items: List[Dict], limit: int = 20) -> str:
    if not items:
        return "No arbitrage opportunities found."

    lines = ["<b>Top Funding Arbitrage</b>\n"]
    for i, item in enumerate(items[:limit], 1):
        symbol = item["symbol"]
        spread_pct = item["spread"] * 100
        net_pct = item.get("net_profit", item["spread"]) * 100
        max_ex = item["max"]["exchange"]
        min_ex = item["min"]["exchange"]
        lines.append(
            f"{i}. <b>{symbol}</b> — {spread_pct:.4f}% "
            f"(net: {net_pct:.4f}%)\n"
            f"   Long {min_ex} / Short {max_ex}"
        )
    return "\n".join(lines)


def format_all_list(items: List[Dict]) -> str:
    if not items:
        return "No data available."

    lines = ["<b>All Arbitrage Opportunities</b>\n"]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {format_arbitrage(item)}")
    return "\n\n".join(lines)
