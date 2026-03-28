import asyncio
import logging
from typing import Dict, List, Optional

from exchanges import EXCHANGES
from exchanges.base_exchange import BaseExchange, FundingData
from utils.cache import TTLCache

logger = logging.getLogger(__name__)


class FundingService:
    def __init__(self, cache_ttl: float = 10.0):
        self.exchanges: Dict[str, BaseExchange] = {
            name: cls() for name, cls in EXCHANGES.items()
        }
        self.cache = TTLCache(ttl=cache_ttl)
        self._all_data: List[FundingData] = []

    async def fetch_all(self) -> List[FundingData]:
        cached = await self.cache.get("all_funding")
        if cached is not None:
            self._all_data = cached
            return cached

        tasks = []
        for name, ex in self.exchanges.items():
            tasks.append(self._safe_fetch(name, ex))
        results = await asyncio.gather(*tasks)

        all_data: List[FundingData] = []
        for items in results:
            all_data.extend(items)

        self._all_data = all_data
        await self.cache.set("all_funding", all_data)
        return all_data

    async def _safe_fetch(self, name: str, ex: BaseExchange) -> List[FundingData]:
        try:
            data = await ex.fetch_funding_rates()
            return data
        except Exception as e:
            logger.error(f"{name}: fetch failed: {e}")
            return []

    def get_all(self) -> List[FundingData]:
        return self._all_data

    def get_by_symbol(self, symbol: str) -> List[FundingData]:
        sym = symbol.upper().replace("-", "").replace("/", "")
        return [d for d in self._all_data if d.symbol == sym]

    async def close_all(self):
        for ex in self.exchanges.values():
            await ex.close()
