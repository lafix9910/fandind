import asyncio
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

logger = logging.getLogger(__name__)
router = Router()

_alert_tasks: dict[int, asyncio.Task] = {}
_alert_settings: dict[int, float] = {}


async def _alert_loop(chat_id: int, min_spread: float):
    from __main__ import funding_service, arbitrage_service
    while True:
        try:
            data = await funding_service.fetch_all()
            opps = arbitrage_service.find_opportunities(data, min_spread=min_spread)
            if opps:
                from aiogram import Bot
                from __main__ import bot
                from utils.formatter import format_arbitrage
                for opp in opps[:3]:
                    text = format_arbitrage(opp)
                    await bot.send_message(chat_id, text, parse_mode="HTML")
            await asyncio.sleep(15)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Alert loop error for {chat_id}: {e}")
            await asyncio.sleep(5)


@router.message(Command("alerts_on"))
async def cmd_alerts_on(message: Message):
    chat_id = message.chat.id
    min_spread = _alert_settings.get(chat_id, 0.001)

    if chat_id in _alert_tasks:
        await message.answer("Alerts already running. Use /alerts_off first.")
        return

    task = asyncio.create_task(_alert_loop(chat_id, min_spread))
    _alert_tasks[chat_id] = task
    await message.answer(
        f"Alerts ON. Min spread: {min_spread * 100:.2f}%. "
        "Checking every 15s. Use /alerts_off to stop."
    )


@router.message(Command("alerts_off"))
async def cmd_alerts_off(message: Message):
    chat_id = message.chat.id
    task = _alert_tasks.pop(chat_id, None)
    if task:
        task.cancel()
        await message.answer("Alerts stopped.")
    else:
        await message.answer("No active alerts.")
