import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class FundingData:
    __slots__ = ("exchange", "symbol", "funding_rate", "next_funding_time", "price")

    def __init__(
        self,
        exchange: str,
        symbol: str,
        funding_rate: float,
        next_funding_time: int,
        price: float = 0.0,
    ):
        self.exchange = exchange
        self.symbol = symbol
        self.funding_rate = funding_rate
        self.next_funding_time = next_funding_time
        self.price = price

    def to_dict(self) -> dict:
        return {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "funding_rate": self.funding_rate,
            "next_funding_time": self.next_funding_time,
            "price": self.price,
        }

    def __repr__(self):
        return f"FundingData({self.exchange}, {self.symbol}, {self.funding_rate})"


class BaseExchange(ABC):
    name: str = ""
    rate_limit_delay: float = 0.2
    max_retries: int = 3

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=15)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, url: str, params: Optional[dict] = None) -> Optional[dict]:
        session = await self.get_session()
        for attempt in range(1, self.max_retries + 1):
            try:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 429:
                        wait = float(resp.headers.get("Retry-After", 2))
                        logger.warning(f"{self.name}: rate limited, waiting {wait}s")
                        await asyncio.sleep(wait)
                    else:
                        logger.warning(f"{self.name}: HTTP {resp.status} for {url}")
                        return None
            except Exception as e:
                logger.error(f"{self.name}: request error (attempt {attempt}): {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(1 * attempt)
        return None

    @abstractmethod
    async def fetch_funding_rates(self) -> List[FundingData]:
        ...

    def normalize_symbol(self, symbol: str) -> str:
        s = symbol.upper().replace("-", "").replace("/", "").replace("_", "")
        if not s.endswith("USDT"):
            s = s.replace("USDT", "") + "USDT"
        return s
