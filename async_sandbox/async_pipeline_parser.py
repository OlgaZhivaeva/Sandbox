import asyncio
import time
from random import randint

async def download_page(url: str) -> str:
    print(f"[Скачивание] Начали качать {url}...")
    time_delay = randint(1, 5)
    await asyncio.sleep(time_delay)
    print(f"[Скачивание] Закончили качать {url} за {time_delay} сек!")
    return f"<html>контент для {url}</html>"

async def parse_page(html: str) -> str:
    print(f"[Парсинг] Начали анализ контента...{html}")
    await asyncio.sleep(0.5)
    print(f"[Парсинг] Заголовок: {html[38: -7]}")
    return html[38: -7]


async def process_url(url: str) -> str:
    html = await download_page(url)
    parsed_data = await parse_page(html)
    return parsed_data

async def main():
    urls = [
        "https://example.com/news",
        "https://example.com/sports",
        "https://example.com/weather",
        "https://example.com/finance",
        "https://example.com/tech"
    ]
    start = time.perf_counter()

    headers = await asyncio.gather(*[process_url(url) for url in urls], return_exceptions=True)

    end = time.perf_counter()
    print(f"\nВсе задачи выполнены за: {end - start:.2f} сек.")
    return headers

if __name__ == "__main__":
    headers = asyncio.run(main())
    print(headers)
