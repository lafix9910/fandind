import time
import logging
from typing import List
from .base_exchange import BaseExchange, FundingData

logger = logging.getLogger(__name__)


class BitgetExchange(BaseExchange):
    name = "Bitget"
    base_url = "https://api.bitget.com"

    async def fetch_funding_rates(self) -> List[FundingData]:
        tickers_url = f"{self.base_url}/api/v2/mix/market/tickers"
        tickers_params = {"productType": "USDT-FUTURES"}
        tickers_data = await self._request(tickers_url, tickers_params)

        funding_url = f"{self.base_url}/api/v2/mix/market/current-funding-rate"
        funding_params = {"productType": "USDT-FUTURES"}
        funding_data = await self._request(funding_url, funding_params)

        if not tickers_data or tickers_data.get("code") != "00000":
            logger.error(f"{self.name}: failed to fetch tickers")
            return []

        price_map = {}
        for item in tickers_data.get("data", []):
            symbol = item.get("symbol", "")
            try:
                price_map[symbol] = float(item.get("lastPr", 0))
            except (ValueError, TypeError):
                continue

        funding_map = {}
        if funding_data and funding_data.get("code") == "00000":
            for item in funding_data.get("data", []):
                symbol = item.get("symbol", "")
                try:
                    rate = float(item.get("fundingRate", 0))
                    next_time = int(item.get("nextUpdate", 0))
                    funding_map[symbol] = (rate, next_time)
                except (ValueError, TypeError):
                    continue

        result = []
        for symbol, price in price_map.items():
            if not symbol.endswith("USDT"):
                continue
            if symbol in funding_map:
                rate, next_time = funding_map[symbol]
            else:
                rate, next_time = 0.0, 0
            result.append(
                FundingData(
                    exchange=self.name,
                    symbol=symbol,
                    funding_rate=rate,
                    next_funding_time=next_time,
                    price=price,
                )
            )
        logger.info(f"{self.name}: fetched {len(result)} funding rates")
        return result
