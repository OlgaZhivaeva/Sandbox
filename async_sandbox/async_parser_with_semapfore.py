import asyncio
from random import uniform
from time import time


async def fetch_url(url: str, sem: asyncio.Semaphore):
    # await asyncio.sleep(uniform(0.1, 1.5))

    async with sem:

        print(f"🟢 [СТАРТ] Скачиваю {url}.\nОсталось свободных слотов: {sem._value}")
        await asyncio.sleep(uniform(0.3, 0.6))
        print(f"🔴 [ФИНИШ] Завершено {url}")


async def main():
    start = time()
    urls = [f"https://api.example.com/item/{i}" for i in range(1, 11)]

    semapfore = asyncio.Semaphore(3)

    await asyncio.gather(
        *[fetch_url(url, semapfore) for url in urls],
        return_exceptions=True
    )

    print(f"Программа отработала за {time() - start:.2f} сек.")

if __name__ == '__main__':
    asyncio.run(main())