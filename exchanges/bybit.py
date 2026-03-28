import time
import logging
from typing import List
from .base_exchange import BaseExchange, FundingData

logger = logging.getLogger(__name__)


class BybitExchange(BaseExchange):
    name = "Bybit"
    base_url = "https://api.bybit.com"

    async def fetch_funding_rates(self) -> List[FundingData]:
        url = f"{self.base_url}/v5/market/tickers"
        params = {"category": "linear"}
        data = await self._request(url, params)
        if not data or data.get("retCode") != 0:
            logger.error(f"{self.name}: failed to fetch data: {data}")
            return []

        result = []
        items = data.get("result", {}).get("list", [])
        for item in items:
            symbol = item.get("symbol", "")
            if not symbol.endswith("USDT"):
                continue
            try:
                rate = float(item.get("fundingRate", 0))
                next_time = int(item.get("nextFundingTime", 0))
                price = float(item.get("lastPrice", 0))
                result.append(
                    FundingData(
                        exchange=self.name,
                        symbol=symbol,
                        funding_rate=rate,
                        next_funding_time=next_time,
                        price=price,
                    )
                )
            except (ValueError, TypeError):
                continue
        logger.info(f"{self.name}: fetched {len(result)} funding rates")
        return result
