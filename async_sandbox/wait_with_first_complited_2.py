import asyncio
from random import uniform
from time import time

from django.core.files.locks import unlock


async def download(file_id: int):
    global all_time
    load_time = uniform(0.5, 10.5)
    all_time += load_time
    await asyncio.sleep(load_time)
    print(f"Скачан файл {file_id} за {load_time:.2f} сек.")
    return load_time


async def main():
    max_parallel_tasks = 3
    file_ids = list(range(1, 10))  # 9 файлов

    pending_tasks = set()

    # Сначала заполняем пул до лимита (3 задачи)
    while file_ids and len(pending_tasks) < max_parallel_tasks:
        task = asyncio.create_task(download(file_ids.pop(0)))
        pending_tasks.add(task)
    print(f"задач в обработке {len(pending_tasks)} ")

    # Пока есть работа
    while pending_tasks:
        # Ждем финиша ХОТЯ БЫ ОДНОЙ задачи из трех
        done, pending_tasks = await asyncio.wait(
            pending_tasks, return_when=asyncio.FIRST_COMPLETED
        )
        print(f"Задач в обработке {len(pending_tasks)} ")

        # Как только одна завершилась, освободилось место — добавляем новую!
        while file_ids and len(pending_tasks) < max_parallel_tasks:
            new_task = asyncio.create_task(download(file_ids.pop(0)))
            pending_tasks.add(new_task)
            print(f"Добавлена задача в обработку, задач в обработке {len(pending_tasks)}")

if __name__ == "__main__":
    all_time = 0
    start = time()
    asyncio.run(main())
    print(f"Все задачи отработали за {time() - start:.2f} сек")
    print(f"Полное время скачиваний {all_time:.2f} сек.")
