import requests


def get_top_100_excluding_stables():


    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1'
    response = requests.get(url)
    data = response.json()
    coins = []
    stables = {'USDT', 'USDC', 'BUSD', 'DAI', 'FDUSD', 'TUSD', 'USDP', 'GUSD'}  # Исключаем стейблы
    for coin in data:
        if coin['symbol'].upper() not in stables:
            coins.append({'symbol': coin['symbol'].upper() + 'USDT', 'name': coin['name']})  # Для Binance
    return coins[:100]
