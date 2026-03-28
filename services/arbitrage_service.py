import logging
from collections import defaultdict
from typing import Dict, List, Optional

from exchanges.base_exchange import FundingData
from utils.formatter import TAKER_FEE

logger = logging.getLogger(__name__)


class ArbitrageService:
    def __init__(self, min_spread: float = 0.0002):
        self.min_spread = min_spread

    def find_opportunities(
        self, data: List[FundingData], min_spread: Optional[float] = None
    ) -> List[Dict]:
        threshold = min_spread if min_spread is not None else self.min_spread

        by_symbol: Dict[str, List[FundingData]] = defaultdict(list)
        for item in data:
            if item.funding_rate != 0:
                by_symbol[item.symbol].append(item)

        opportunities = []
        for symbol, entries in by_symbol.items():
            if len(entries) < 2:
                continue

            max_entry = max(entries, key=lambda x: x.funding_rate)
            min_entry = min(entries, key=lambda x: x.funding_rate)

            spread = max_entry.funding_rate - min_entry.funding_rate
            if spread < threshold:
                continue

            avg_price = 0
            prices = [e.price for e in entries if e.price > 0]
            if prices:
                avg_price = sum(prices) / len(prices)

            fees = TAKER_FEE * 2
            net_profit = spread - fees

            opportunities.append(
                {
                    "symbol": symbol,
                    "spread": spread,
                    "net_profit": net_profit,
                    "avg_price": avg_price,
                    "max": {
                        "exchange": max_entry.exchange,
                        "funding_rate": max_entry.funding_rate,
                    },
                    "min": {
                        "exchange": min_entry.exchange,
                        "funding_rate": min_entry.funding_rate,
                    },
                }
            )

        opportunities.sort(key=lambda x: x["net_profit"], reverse=True)
        return opportunities
