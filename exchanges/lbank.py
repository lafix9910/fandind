import time
import logging
from typing import List
from .base_exchange import BaseExchange, FundingData

logger = logging.getLogger(__name__)


class LbankExchange(BaseExchange):
    name = "LBank"
    base_url = "https://lbk.com"

    async def fetch_funding_rates(self) -> List[FundingData]:
        url = f"{self.base_url}/api/v1/futureUsdt/v2/marketFundingRate"
        data = await self._request(url)
        if not data or not data.get("data"):
            logger.error(f"{self.name}: failed to fetch data: {data}")
            return []

        result = []
        items = data.get("data", [])
        for item in items:
            symbol = item.get("symbol", "").upper().replace("-", "")
            if not symbol.endswith("USDT"):
                continue
            try:
                rate = float(item.get("fundingRate", 0))
                next_time = int(item.get("nextSettleTime", 0))
                if next_time < 1e12:
                    next_time *= 1000
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
