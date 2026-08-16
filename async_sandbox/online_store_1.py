import asyncio
import random
import time
from datetime import date, timedelta


async def process_order():
    start_time = time.time()
    print("=== Начало обработки заказа ===")
    completed_steps = asyncio.Queue()

    try:
        # Критический этап: Оплата (0.5 сек) и Склад (0.8 сек)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(pay_money(completed_steps))
            tg.create_task(reserve_stock(completed_steps))

        run_time = time.time() - start_time
        print(f"\n  [Система] Все проверки пройдены! Время от старта: {run_time:.2f} сек")
        delivery_date = date.today() + timedelta(days=5)

        await send_notifications(f"Заказ подтвержден. Дата получения: {delivery_date}")

        run_time = time.time() - start_time
        print(f"\n=== Заказ успешно обработан (Всего за: {run_time:.2f} сек) ===")

    except* ValueError as eg:
        # Откатываем транзакции
        await rollback(completed_steps)
        # Отправляем уведомление об отмене
        for err in eg.exceptions:
            await send_notifications(f"Заказ отменен. Причина: {err}")

        run_time = time.time() - start_time
        print(f"\n❌ [ОШИБКА ЗАКАЗА] Время выполнения: {run_time:.2f} сек")

async def pay_money(queue: asyncio.Queue):
    try:
        await asyncio.sleep(0.5)  # Имитация запроса к банку
        if random.choice([True, False]):
            print("  [Оплата] Деньги списаны")
            await queue.put("PAYMENT_SUCCESS")
        else:
            print("  [Оплата] Ошибка! Недостаточно средств")
            raise ValueError("Недостаточно средств на карте")
    except asyncio.CancelledError:
        print("  [Оплата] ⚠️ Процесс оплаты отменен!")
        raise


async def reserve_stock(queue: asyncio.Queue):
    try:
        await asyncio.sleep(0.8)  # Имитация проверки БД склада
        if random.choice([True, False]):
            print("  [Склад] Товар забронирован")
            await queue.put("STOCK_SUCCESS")
        else:
            print("  [Склад] Товар закончился на складе")
            raise ValueError("Товар закончился на складе")
    except asyncio.CancelledError:
        print("  [Склад] ⚠️ Бронирование отменено!")
        raise


async def rollback(queue: asyncio.Queue):
    if not queue.empty():
        step = await queue.get()
        if step == "PAYMENT_SUCCESS":
            await refund_money()
        elif step == "STOCK_SUCCESS":
            await unreserve_stock()


async def refund_money():
    await asyncio.sleep(0.5)
    print("  [Откат] 🔄 Возврат денег...")


async def unreserve_stock():
    await asyncio.sleep(0.5)
    print("  [Откат] 🔄 Снятие брони со склада...")


async def send_notifications(text):
    print(f"\n  [Уведомления] 📨 {text}")
    n_start = time.time()

    results = await asyncio.gather(
        send_telegram(),
        send_email(),
        send_sms(),
        return_exceptions=True,
    )

    n_time = time.time() - n_start
    print(
        f"  [Уведомления] ✅ Все 3 канала ответили за {n_time:.2f} сек! Результаты: {results}"
    )


async def send_telegram():
    await asyncio.sleep(0.3)  # Запрос к Telegram API
    return "Telegram OK"


async def send_email():
    await asyncio.sleep(0.7)  # Запрос к почтовому серверу
    return "Email OK"


async def send_sms():
    await asyncio.sleep(1.2)  # Запрос к SMS-шлюзу
    if random.choice([True, False]):
        return "SMS OK"
    raise ConnectionError("SMS-шлюз недоступен")


asyncio.run(process_order())
