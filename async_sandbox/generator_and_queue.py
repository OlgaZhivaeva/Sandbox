import asyncio
from collections.abc import AsyncGenerator
from random import uniform


async def file_generator() -> AsyncGenerator[str, None]:
    for i in range(1, 11):
        await asyncio.sleep(0.8)
        yield f"file number {i}"


async def producer(queue: asyncio.Queue[str | None], num_workers: int) -> None:
    async for file_name in file_generator():
        print(f"[Продюсер] Сгенерирован {file_name}")
        await queue.put(file_name)

    for _ in range(num_workers):
        await queue.put(None)


async def worker(name: str, queue: asyncio.Queue[str | None]) -> None:
    while True:
        file_name = await queue.get()
        try:
            if file_name is None:
                print(f"[{name}] Получил сигнал остановки, завершаю работу.")
                return

            if file_name == "file number 5":
                raise ValueError("Ошибка скачивания.")

            await asyncio.sleep(uniform(0.5, 1.5))
            print(f"[{name}] Скачал {file_name}")

        except Exception as err:
            print(f"[{name}] Ошибка при обработке {file_name}: {err}")
        finally:
            queue.task_done()


async def main() -> None:
    NUM_WORKERS = 6
    queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=1)

    async with asyncio.TaskGroup() as tg:

        tg.create_task(producer(queue, num_workers=NUM_WORKERS)) # Запускаем продюсера

        for i in range(1, NUM_WORKERS + 1): # Запускаем воркеров
            tg.create_task(worker(f"worker-{i}", queue))

        await queue.join() # Ждем, пока все задачи из очереди будут обработаны


if __name__ == "__main__":
    asyncio.run(main())


