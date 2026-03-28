# Funding Arbitrage Bot

## Setup

1. Copy `.env.example` to `.env` and fill in your Telegram bot token
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Commands

- `/start` — Help
- `/top` — Top 15 arbitrage opportunities sorted by net profit
- `/all` — All opportunities (up to 30)
- `/settings` — Choose minimum spread threshold
- `/alerts_on` — Start automatic alerts every 15s
- `/alerts_off` — Stop alerts

## Configuration (.env)

- `BOT_TOKEN` — Telegram bot token from @BotFather
- `MIN_SPREAD` — Minimum spread threshold (default: 0.0002 = 0.02%)
- `CACHE_TTL` — Cache lifetime in seconds (default: 10)

## Supported Exchanges

- Bybit
- Bitget
- MEXC
- LBank
- HTX (Huobi)

## Strategy

For each coin with funding spread above threshold:
- **Long** on exchange with lower (or negative) funding
- **Short** on exchange with higher funding
- Profit = spread - 2× taker fees (~0.12%)
