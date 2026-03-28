from .bybit import BybitExchange
from .bitget import BitgetExchange
from .mexc import MexcExchange
from .lbank import LbankExchange
from .htx import HtxExchange

EXCHANGES = {
    "bybit": BybitExchange,
    "bitget": BitgetExchange,
    "mexc": MexcExchange,
    "lbank": LbankExchange,
    "htx": HtxExchange,
}
