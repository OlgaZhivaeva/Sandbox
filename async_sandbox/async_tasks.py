import asyncio
import time
from random import randint


async def download_page(url: str) -> str:
    print(f"[Скачивание] Начали качать {url}...")
    time_delay = randint(1, 5)
    await asyncio.sleep(time_delay)
    print(f"[Скачивание] Закончили качать {url}! Время скачивания {time_delay}")
    return f"<html>контент для {url}</html>"


async def main():
    start = time.perf_counter()
    urls = [
        "https://example.com/news",
        "https://example.com/sports",
        "https://example.com/weather",
        "https://example.com/finance",
        "https://example.com/tech"
    ]

    async with asyncio.TaskGroup() as tg:
        # Создаём задачи с помощью tg.create_task()
        tasks = [tg.create_task(download_page(url)) for url in urls]

    # 2. При выходе из блока `async with` ВСЕ задачи ГАРАНТИРОВАННО завершены!
    # Нам НЕ НУЖНО писать await!

    # 3. Забираем результаты через .result()
    results = [task.result() for task in tasks]

    print(f"\nУспешно скачано страниц: {len(results)}")

    end = time.perf_counter()
    print(f"Время выполнения: {end - start:.2f} сек.")


if __name__ == "__main__":
    asyncio.run(main())
