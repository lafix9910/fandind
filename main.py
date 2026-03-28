import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

from services.funding_service import FundingService
from services.arbitrage_service import ArbitrageService

MIN_SPREAD = float(os.getenv("MIN_SPREAD", "0.0002"))
CACHE_TTL = float(os.getenv("CACHE_TTL", "10"))

funding_service = FundingService(cache_ttl=CACHE_TTL)
arbitrage_service = ArbitrageService(min_spread=MIN_SPREAD)

from handlers.commands import router as commands_router
from handlers.alerts import router as alerts_router

dp.include_router(commands_router)
dp.include_router(alerts_router)


async def main():
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await funding_service.close_all()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
