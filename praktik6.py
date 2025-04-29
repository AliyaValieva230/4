import asyncio
import aiohttp


API_KEY = "VpzmN7hTyP909++zzxP7vg==4IOnIcpSznUFRSEC"


API_ENDPOINTS = {'API_NINJAS': "https://api.api-ninjas.com/v1/cryptoprice"}


async def fetch_api(session, url, symbol, api_name):
    headers = {
        "X-Api-Key": API_KEY
    }
    params = {"symbol": symbol}
    try:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                print(f"[{api_name}] Цена {symbol}: {data}")
            else:
                print(f"[{api_name}] Ошибка {response.status} для {symbol}")
    except Exception as e:
        print(f"[{api_name}] Исключение для {symbol}: {e}")

async def main():
    symbols = ["BTC", "ETH", "LTC"]
    async with aiohttp.ClientSession() as session:
        tasks = []
        for api_name, url in API_ENDPOINTS.items():
            for symbol in symbols:
                tasks.append(fetch_api(session, url, symbol, api_name))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
