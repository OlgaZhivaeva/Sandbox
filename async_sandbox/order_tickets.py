import asyncio

tickets_available = 5
lock = asyncio.Lock()


async def order_tickets(buyer_name: str) -> None:
    global tickets_available

    async with lock:
        if tickets_available > 0:
            await asyncio.sleep(0.1)
            tickets_available -= 1
            print(f"[{buyer_name}] Успешно купил билет! Осталось: {tickets_available}")
            return

        print(f"[{buyer_name}] Билеты кончились :(")


async def main() -> None:
    await asyncio.gather(*[order_tickets(f"buyer_{i}") for i in range(1, 11)], return_exceptions=True)


asyncio.run(main())