import yfinance as yf
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import MACD
from telegram import Bot
from telegram.constants import ParseMode
import asyncio
import schedule
import time
import datetime

# === CONFIG ===
TELEGRAM_TOKEN = '7693497851:AAFgO1OfgavzpQI1oeDKYUOewqXVKz4OXv0'
CHAT_ID = '8009939666'  # Final confirmed Telegram user ID
TICKER = 'CPRX'
bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(message, image_path=None):
    if image_path:
        with open(image_path, 'rb') as img:
            await bot.send_photo(chat_id=CHAT_ID, photo=img, caption=message, parse_mode=ParseMode.MARKDOWN)
    else:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)

def generate_chart(data, save_path="/tmp/cprx_chart.png"):
    plt.figure(figsize=(10, 4))
    plt.plot(data['Close'][-50:], label='CPRX Price')
    plt.title("CPRX Price - Last 50 Candles")
    plt.grid()
    plt.legend()
    plt.savefig(save_path)
    plt.close()
    return save_path

async def send_cprx_update():
    try:
        data = yf.download(TICKER, period="7d", interval="15m")
        if data.empty:
            raise Exception("No data found for CPRX — check the ticker or your internet connection.")

        close = data['Close']
        rsi = RSIIndicator(close.squeeze()).rsi()
        macd = MACD(close.squeeze())
        macd_line = macd.macd()
        signal_line = macd.macd_signal()

        latest_price = float(close.iloc[-1])
        latest_rsi = rsi.iloc[-1]
        latest_macd = macd_line.iloc[-1]
        latest_signal = signal_line.iloc[-1]

        if latest_rsi < 30 and latest_macd > latest_signal:
            signal = "🔁 *BUY signal* (RSI < 30 & MACD Bullish)"
        elif latest_rsi > 70 and latest_macd < latest_signal:
            signal = "📤 *SELL signal* (RSI > 70 & MACD Bearish)"
        else:
            signal = "⚠️ *Neutral* (No strong signal)"

        msg = (
            f"📊 *CPRX Stock Update*\n\n"
            f"*Price:* ${latest_price:.2f}\n"
            f"*RSI:* {latest_rsi:.2f}\n"
            f"*MACD:* {latest_macd:.2f}\n"
            f"*Signal Line:* {latest_signal:.2f}\n\n"
            f"{signal}\n\n"
            f"_As of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}_"
        )

        chart_path = generate_chart(data)
        await send_telegram_message(msg, chart_path)

    except Exception as e:
        await send_telegram_message(f"⚠️ Bot error: {str(e)}")

def run_bot():
    asyncio.run(send_cprx_update())

schedule.every(15).minutes.do(run_bot)

print("✅ CPRX Telegram Bot is running...")
run_bot()

while True:
    schedule.run_pending()
    time.sleep(5)
