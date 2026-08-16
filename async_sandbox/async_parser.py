import asyncio
import time
from random import randint

async def download_page(url):
    print(f"[Скачивание] Начали качать {url}...")
    time_delay = randint(1, 5)
    await asyncio.sleep(time_delay)
    print(f"[Скачивание] Закончили качать {url}! Время скачивания {time_delay}")
    return f"<html>контент для {url}</html>"

async def parse_page(html):
    print(f"[Парсинг] Начали анализ контента...{html}")
    await asyncio.sleep(0.5)
    print(f"[Парсинг] Заголовок: {html[38: -7]}")
    return html[38: -7]

async def maim():
    urls = [
        "https://example.com/news",
        "https://example.com/sports",
        "https://example.com/weather",
        "https://example.com/finance",
        "https://example.com/tech"
    ]
    start = time.perf_counter()

    pages_to_parse = await asyncio.gather(*[download_page(url) for url in urls])

    headers = await asyncio.gather(*[parse_page(page) for page in pages_to_parse], return_exceptions=True)

    end = time.perf_counter()
    run_time = end - start
    print(f"Время выполнения: {run_time:.2f}")
    return headers

if __name__ == "__main__":
    headers = asyncio.run(maim())
    print(headers)


