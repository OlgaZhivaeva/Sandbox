import asyncio
from random import uniform


async def async_generate_file(queue: asyncio.Queue[str | None]):
    for i in range(1, 11):
        await asyncio.sleep(0.1)
        print(f"Сгенерирован файл {i}")
        file_name = f"file number {i}"
        await queue.put(file_name)
        print(f"[put] Незавершено задач: {queue._unfinished_tasks}, Число задач в очереди: {queue.qsize()}")


async def async_load_file(name: str, queue: asyncio.Queue[str | None]):
    while True:
        file_name = await queue.get()
        print(f"[get] Незавершено задач: {queue._unfinished_tasks}, Число задач в очереди: {queue.qsize()}")
        try:
            if file_name == "file number 3":
                raise ValueError(f"Не удалось скачать {file_name}")
            elif file_name == "file number 5":
                raise ZeroDivisionError(f"Загрузчик {name} сломался!")

            await asyncio.sleep(uniform(0.5, 1.5))
            print(f"[{name}] Успешно скачал {file_name}")

        except ValueError as err:
            print(f"[{name}] Ошибка скачивания (пропускаем): {err}")
        except ZeroDivisionError as err:
            print(f"[{name}] КРИТИЧЕСКАЯ ОШИБКА: {err}.")
            return  # Завершаем заботу сломанного воркера
        finally:
            queue.task_done()  # Уменьшаем счетчик и для успехов, и для ошибок
            print(f"[done] Незавершено задач: {queue._unfinished_tasks}, Число задач в очереди: {queue.qsize()}")


async def main() -> None:
    queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=3)

    async with asyncio.TaskGroup() as tg:

        producer_task = tg.create_task(async_generate_file(queue))

        worker_tasks = [
            tg.create_task(async_load_file(f"worker-{i}", queue))
            for i in range(1, 4)
        ]

        await producer_task # Ждем, пока продюсер сгенерирует все 10 файлов

        await queue.join() # Ждем, пока все 10 файлов будут обработаны (внутри TaskGroup)
        print("🎉 Все файлы успешно обработаны (или пропущены с ошибкой)!")

        for task in worker_tasks: # Отменяем оставшихся живых воркеров, так как работа сделана
            task.cancel()


if __name__ == "__main__":
    print("🚀 Запускаем скачивание файлов...")
    asyncio.run(main())
