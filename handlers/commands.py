import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from services.funding_service import FundingService
from services.arbitrage_service import ArbitrageService
from utils.formatter import format_top_list, format_all_list, format_arbitrage

logger = logging.getLogger(__name__)
router = Router()

SPREAD_OPTIONS = [0.0002, 0.0005, 0.001, 0.002, 0.005]
EXCHANGE_NAMES = ["Bybit", "Bitget", "MEXC", "LBank", "HTX"]


def get_services() -> tuple:
    from __main__ import funding_service, arbitrage_service
    return funding_service, arbitrage_service


def _spread_keyboard():
    buttons = [
        InlineKeyboardButton(
            text=f"{s * 100:.2f}%",
            callback_data=f"spread_{s}",
        )
        for s in SPREAD_OPTIONS
    ]
    rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _exchange_keyboard():
    buttons = [
        InlineKeyboardButton(text=ex, callback_data=f"toggle_{ex}")
        for ex in EXCHANGE_NAMES
    ]
    rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "<b>Funding Arbitrage Bot</b>\n\n"
        "Commands:\n"
        "/top — Top arbitrage opportunities\n"
        "/all — All opportunities\n"
        "/settings — Configure minimum spread\n"
        "/alerts_on — Enable alerts\n"
        "/alerts_off — Disable alerts\n"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("top"))
async def cmd_top(message: Message):
    funding_svc, arb_svc = get_services()
    try:
        data = await funding_svc.fetch_all()
        opps = arb_svc.find_opportunities(data)
        text = format_top_list(opps, limit=15)
        if len(text) > 4000:
            text = text[:4000] + "\n..."
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"/top error: {e}")
        await message.answer(f"Error fetching data: {e}")


@router.message(Command("all"))
async def cmd_all(message: Message):
    funding_svc, arb_svc = get_services()
    try:
        data = await funding_svc.fetch_all()
        opps = arb_svc.find_opportunities(data)
        text = format_all_list(opps[:30])
        if len(text) > 4000:
            chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                await message.answer(chunk, parse_mode="HTML")
        else:
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"/all error: {e}")
        await message.answer(f"Error: {e}")


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    text = "Choose minimum spread threshold:"
    await message.answer(text, reply_markup=_spread_keyboard())


@router.callback_query(F.data.startswith("spread_"))
async def callback_spread(callback: CallbackQuery):
    _, val = callback.data.split("_", 1)
    spread = float(val)
    from __main__ import arbitrage_service
    arbitrage_service.min_spread = spread
    await callback.answer(f"Min spread set to {spread * 100:.2f}%")
    await callback.message.edit_text(f"Minimum spread: <b>{spread * 100:.2f}%</b>", parse_mode="HTML")


@router.callback_query(F.data.startswith("toggle_"))
async def callback_toggle_exchange(callback: CallbackQuery):
    exchange = callback.data.replace("toggle_", "")
    from __main__ import funding_service
    ex = funding_service.exchanges.get(exchange.lower())
    if ex:
        await callback.answer(f"{exchange} toggled")
    else:
        await callback.answer(f"Unknown exchange: {exchange}")
