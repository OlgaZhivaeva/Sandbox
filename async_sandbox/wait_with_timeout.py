import asyncio
from random import uniform


async def fetch_data(site_name: str, delay) -> str:
    await asyncio.sleep(delay)
    if site_name == "https://example.com/food":
        print(f"Сайт {site_name} упал с ошибкой")
        raise ValueError(f"Сайт {site_name} упал с ошибкой")
    print(f"Скачивание данных с сайта {site_name}...")
    return f"{site_name[20:]}"


async def main(time_out: float):
    sites = [
        "https://example.com/news",
        "https://example.com/sport",
        "https://example.com/food",
        "https://example.com/bisnes",
    ]
    tasks = []
    for site in sites:
        task = asyncio.create_task(fetch_data(site, uniform(0.1, 0.9)))
        tasks.append(task)

    done, pending = await asyncio.wait(tasks, timeout=time_out, return_when=asyncio.FIRST_EXCEPTION)

    for task in done:
        try:
            result = task.result()  # Если была ошибка, здесь вылетит исключение повторно
            print(f"Данные получены: {result}")
        except ValueError as e:
            print(f"Ошибка в выполненной задаче: {e}")

    # Отменяем незавершенные задачи и аккуратно дожидаемся отмены
    if pending:
        for task in pending:
            task.cancel()
        # Гарантируем корректное закрытие отмененных корутин
        await asyncio.gather(*pending, return_exceptions=True)
        print(f"Отменено задач: {len(pending)}")


if __name__ == "__main__":
    print("--- ТЕСТ 1: Большой таймаут (завершится по ошибке) ---")
    asyncio.run(main(time_out=10.0))

    print("\n-----------------------------------------------------------\n")

    print("--- ТЕСТ 2: Маленький таймаут (завершится по времени) ---")
    asyncio.run(main(time_out=0.2))

