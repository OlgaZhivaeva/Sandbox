import asyncio


async def fetch_data():
    await asyncio.sleep(5.0)  # Очень долгий запрос (5 секунд)
    return "Данные получены!"


async def main():
    try:
        # Ждем выполнения fetch_data, но не дольше 2 секунд
        result = await asyncio.wait_for(fetch_data(), timeout=2.0)
        print(result)
    except TimeoutError:
        print("⏰ Время вышло! Запрос был автоматически отменен.")


asyncio.run(main())
