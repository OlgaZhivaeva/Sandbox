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
