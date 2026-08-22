import asyncio
from random import randint


async def fetch_price(shop: str, delay: float) -> str:
    await asyncio.sleep(delay)
    price = randint(100, 1000)
    return f"Цена в магазине {shop}: {price} руб."

async def main():
    tasks = [
        asyncio.create_task(fetch_price("Магнит", 0.5)),
        asyncio.create_task(fetch_price("Чижик", 0.8)),
        asyncio.create_task(fetch_price("Spar", 1.2)),
        asyncio.create_task(fetch_price("Пятерочка", 1))
    ]

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    first_task = done.pop()
    print(f"🎉 ПОБЕДИТЕЛЬ: {first_task.result()}")

    for task in pending:
        task.cancel()
        print("❌ Отменили медленный запрос")

if __name__ == "__main__":
    asyncio.run(main())
