import asyncio


balance = 100
lock = asyncio.Lock()


async def withdraw(amount: int) -> None:
    global balance

    async with lock:
        old_balance = balance
        await asyncio.sleep(0)
        balance = old_balance - amount


async def main() -> None:
    await asyncio.gather(
        withdraw(30),
        withdraw(30),
    )

    print(balance)  # Теперь правильно: 40.


asyncio.run(main())
