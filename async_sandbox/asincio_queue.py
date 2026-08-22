import asyncio


async def producer(queue: asyncio.Queue[int | None]) -> None:
    for number in range(1, 6):
        await queue.put(number)
        print(f"Добавили в очередь: {number}")

    # По одному сигналу остановки для каждого обработчика.
    await queue.put(None)
    await queue.put(None)


async def consumer(name: str, queue: asyncio.Queue[int | None]) -> None:
    while True:
        item = await queue.get()

        try:
            if item is None:
                print(f"{name}: заканчиваю работу")
                return

            await asyncio.sleep(0.2)
            print(f"{name} обработал {item}")
        finally:
            queue.task_done()


async def main() -> None:
    queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=2)

    async with asyncio.TaskGroup() as group:
        group.create_task(producer(queue))
        group.create_task(consumer("Работник A", queue))
        group.create_task(consumer("Работник B", queue))

        # Ждём, пока для каждого put() не вызовут task_done().
        await queue.join()


asyncio.run(main())
# -------------------------------------------------------------------------------
import asyncio
from random import uniform


async def async_generate_file(queue: asyncio.Queue[str | None]):
    for i in range(1, 11):
        await asyncio.sleep(0.1)
        print(f"сгенерирован файл {i}")
        file_name = f"file number {i}"
        await queue.put(file_name)

    await queue.put(None)
    await queue.put(None)
    await queue.put(None)


async def async_load_file(name, queue: asyncio.Queue[str | None]):
    while True:
        try:
            file_name = await queue.get()
            if file_name is None:
                print(f"[{name}] Файлы скачаны, работу закончил")
                return
            await asyncio.sleep(uniform(0.1, 0.4))
            print(f"[{name}] Скачал {file_name}")
        finally:
            queue.task_done()

async def main() -> None:
    queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=3)
    await asyncio.gather(
        async_generate_file(queue),
        async_load_file("worker-1", queue),
        async_load_file("worker-2", queue),
        async_load_file("worker-3", queue)
    )
    await queue.join()


if __name__ == "__main__":
    asyncio.run(main())
