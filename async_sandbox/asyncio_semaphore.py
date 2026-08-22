import asyncio
from random import uniform

# Разрешаем максимум 3 параллельных запроса
semaphore = asyncio.Semaphore(3)

async def fetch_url(url_id: int):
    async with semaphore:
        # Внутрь этого блока могут зайти МАКСИМУМ 3 корутины одновременно!
        print(f"🟢 [Запрос #{url_id}] Начал скачивание...")
        await asyncio.sleep(uniform(1.0, 2.0))
        print(f"🔴 [Запрос #{url_id}] Завершил скачивание!")

async def main():
    # Запускаем 10 запросов
    tasks = [fetch_url(i) for i in range(1, 11)]
    await asyncio.gather(*tasks)

asyncio.run(main())
