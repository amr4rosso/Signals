import requests
import logging
from fetch_data import fetch_ohlcv
from indicator import calculate_signals
from get_top_coins import get_top_100_excluding_stables
from config import NTFY_TOPIC

logger = logging.getLogger(__name__)


def scan_and_send(mode='One per Trend'):
    coins = get_top_100_excluding_stables()
    signals = []

    for coin in coins:
        try:
            df = fetch_ohlcv(coin['symbol'])
            if len(df) < 200:
                continue

            df = calculate_signals(df, mode=mode)
            last_row = df.iloc[-1]

            if last_row['long_signal']:
                message = (
                    f"🟢 LONG сигнал\n"
                    f"Монета: {coin['symbol']} ({coin['name']})\n"
                    f"💵 Цена: {last_row['close']:.2f} USD"
                )
                signals.append(message)
                send_ntfy(message, coin['symbol'])

            elif last_row['short_signal']:
                message = (
                    f"🔴 SHORT сигнал\n"
                    f"Монета: {coin['symbol']} ({coin['name']})\n"
                    f"💵 Цена: {last_row['close']:.2f} USD"
                )
                signals.append(message)
                send_ntfy(message, coin['symbol'])

        except Exception as e:
            logger.error(f"Ошибка для {coin['symbol']}: {e}")

    if signals:
        summary = "📢 Сигналы сегодня:\n\n" + "\n\n".join(signals)
    else:
        summary = "✅ Сегодня сигналов нет"

    send_ntfy(summary)  # summary без кнопки



def send_ntfy(message, symbol=None):
    url = NTFY_TOPIC
    headers = {
        "Title": "Crypto Signal",
        "Content-Type": "text/plain; charset=utf-8"
    }

    if symbol:
        tv_url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
        # ⚡ строка должна быть идентична curl
        headers["Actions"] = "view, 📊 Открыть TradingView, " + tv_url

    # проверим, какие заголовки реально уходят
    print("DEBUG headers:", headers)

    response = requests.post(url, data=message.encode("utf-8"), headers=headers)
    if response.status_code != 200:
        print(f"Ошибка ntfy: {response.text}")
    else:
        print(f"Отправлено: {message[:50]}...")

