import asyncio
from time import time

next_order_id = 1001

lock = asyncio.Lock()


async def process_order(worker_name: str):
    global next_order_id
    await asyncio.sleep(0.2)
    async with lock:
        assigned_id = next_order_id
        next_order_id += 1
    print(f"[{worker_name}] Заказ обработан! Назначен ID: {assigned_id}")


async def main():
    start = time()

    await asyncio.gather(*[process_order(f"Заказ-{i}") for i in range(1, 11)], return_exceptions=True)

    print(f"Программа отработала за {time() - start:.2f} сек.")


if __name__ == "__main__":
    asyncio.run(main())
