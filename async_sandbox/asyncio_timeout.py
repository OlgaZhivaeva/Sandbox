import asyncio
from random import randint


async def fetch_data(delay: int) -> int:
    await asyncio.sleep(delay)
    print(f"  [fetch] Данные получены за {delay} сек.")
    return delay


async def handle_data(data: int) -> int:
    await asyncio.sleep(3.0)
    print("  [handle] Данные обработаны")
    return data


async def main():
    results = []
    for i in range(1, 6):
        print(f"\n--- Итерация {i} ---")
        try:
            # Начальный таймаут 4.5 секунды
            async with asyncio.timeout(4.5) as cm:
                delay = randint(1, 5)
                print(f"Сгенерирована задержка: {delay} сек.")

                data = await fetch_data(delay)

                if data + 3.0 > 4.5:
                    #  ПЕРЕРАСЧЕТ ДЕДЛАЙНА
                    now = asyncio.get_running_loop().time()
                    new_deadline = now + 3.5  # 1.0 секунд от ТЕКУЩЕГО момента

                    print(f"🔄 Установлен новый дедлайн (еще +3.5 сек от текущего момента)")
                    cm.reschedule(new_deadline)

                result = await handle_data(data)
                results.append(result)

        except TimeoutError:
            print(f"⏰ Таймаут превышен! Состояние: {cm.expired()}")

    print("\nИтоговые результаты:", results)


if __name__ == "__main__":
    asyncio.run(main())
