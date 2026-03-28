import time
import logging
from typing import List
from .base_exchange import BaseExchange, FundingData

logger = logging.getLogger(__name__)


class MexcExchange(BaseExchange):
    name = "MEXC"
    base_url = "https://contract.mexc.com"

    async def fetch_funding_rates(self) -> List[FundingData]:
        url = f"{self.base_url}/api/v1/contract/ticker"
        data = await self._request(url)
        if not data or data.get("code") != 0:
            logger.error(f"{self.name}: failed to fetch data: {data}")
            return []

        result = []
        items = data.get("data", [])
        if isinstance(items, dict):
            items = items.get("data", items.get("ticker", []))

        for item in items:
            if isinstance(item, dict):
                symbol = item.get("symbol", "")
            else:
                continue
            if not symbol.endswith("_USDT"):
                continue
            try:
                rate = float(item.get("fundingRate", 0))
                next_time = int(item.get("nextFundingTime", 0))
                price = float(item.get("lastPrice", 0))
                norm_symbol = symbol.replace("_", "")
                result.append(
                    FundingData(
                        exchange=self.name,
                        symbol=norm_symbol,
                        funding_rate=rate,
                        next_funding_time=next_time,
                        price=price,
                    )
                )
            except (ValueError, TypeError):
                continue
        logger.info(f"{self.name}: fetched {len(result)} funding rates")
        return result
