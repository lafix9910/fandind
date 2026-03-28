import time
import logging
from typing import List
from .base_exchange import BaseExchange, FundingData

logger = logging.getLogger(__name__)


class HtxExchange(BaseExchange):
    name = "HTX"
    base_url = "https://api.hbdm.com"

    async def fetch_funding_rates(self) -> List[FundingData]:
        contracts_url = f"{self.base_url}/linear-swap-api/v1/swap_contract_info"
        contracts_data = await self._request(contracts_url)

        if not contracts_data or contracts_data.get("status") != "ok":
            logger.error(f"{self.name}: failed to fetch contracts")
            return []

        symbols = []
        for item in contracts_data.get("data", []):
            sym = item.get("contract_code", "")
            if sym.endswith("-USDT"):
                symbols.append(sym)

        funding_url = f"{self.base_url}/linear-swap-api/v1/swap_batch_funding_rate"
        funding_params = {"contract_code": ",".join(symbols[:200])}
        funding_data = await self._request(funding_url, funding_params)

        tickers_url = f"{self.base_url}/linear-swap-ex-api/v1/swap_batch_tick"
        tickers_data = await self._request(tickers_url)

        price_map = {}
        if tickers_data and tickers_data.get("status") == "ok":
            for item in tickers_data.get("ticks", []):
                code = item.get("contract_code", "")
                try:
                    price_map[code] = float(item.get("close", 0))
                except (ValueError, TypeError):
                    continue

        funding_map = {}
        if funding_data and funding_data.get("status") == "ok":
            for item in funding_data.get("data", []):
                code = item.get("contract_code", "")
                try:
                    rate = float(item.get("funding_rate", 0))
                    next_time = int(item.get("next_funding_time", 0))
                    if next_time < 1e12:
                        next_time *= 1000
                    funding_map[code] = (rate, next_time)
                except (ValueError, TypeError):
                    continue

        result = []
        for code in symbols:
            norm_symbol = code.replace("-", "")
            rate, next_time = funding_map.get(code, (0.0, 0))
            price = price_map.get(code, 0.0)
            result.append(
                FundingData(
                    exchange=self.name,
                    symbol=norm_symbol,
                    funding_rate=rate,
                    next_funding_time=next_time,
                    price=price,
                )
            )
        logger.info(f"{self.name}: fetched {len(result)} funding rates")
        return result
