import asyncio
from random import uniform


async def generate_files():
    for i in range(1, 11):
        await asyncio.sleep(0.1)
        print(f"Сгенерирован файл {i}")
        yield f"file number {i}"


async def download_worker(name: str, file_name: str):
    await asyncio.sleep(uniform(0.1, 0.4))
    print(f"[{name}] Скачал {file_name}")
    return name, file_name


async def main():
    tasks = []

    # 1. Читаем генератор по одному файлу
    async for file_name in generate_files():
        worker_name = f"worker-{int(file_name.split()[-1]) % 3 + 1}"

        # ⚡️ СРАЗУ отправляем задачу в Event Loop в фоновом режиме!
        # Скачивание файла 1 начинается ПРЯМО СЕЙЧАС, пока генератор делает файл 2
        task = asyncio.create_task(download_worker(worker_name, file_name))
        tasks.append(task)

    print("\n--- Генератор закончил работу. Дожидаемся результатов ---\n")

    # 2. Забираем результаты по мере готовности
    for coro in asyncio.as_completed(tasks):
        name, fname = await coro
        print(f"[Подтверждено от {name}] Готово: {fname}")

    print("\n🎉 Все задачи успешно завершены.")


if __name__ == "__main__":
    asyncio.run(main())
