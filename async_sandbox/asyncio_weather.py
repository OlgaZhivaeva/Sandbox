import asyncio
import time

async def fetch_weather(api_name, semafore):
    async with semafore:
        print(f"Запрос к {api_name}")
        await asyncio.sleep(1)
        print(f"Данные от {api_name} получены.")
        return {api_name: "20°C"}


async def get_all_weather_data():
    start_time = time.time()
    sem = asyncio.Semaphore(2)
    tasks = [
        fetch_weather("API_1", sem),
        fetch_weather("API_2", sem),
        fetch_weather("API_3", sem)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()

    print(f"Все данные получены: {results}")
    print(f"Общее время выполнения: {end_time - start_time}")

if __name__ == "__main__":
    asyncio.run(get_all_weather_data())