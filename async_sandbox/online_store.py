import asyncio
import random
import time
from datetime import date, timedelta


class PaymentError(ValueError):
    pass


class StockError(ValueError):
    pass


async def process_order(client_id):
    delay = random.uniform(0.5, 3.0)
    await asyncio.sleep(delay)
    start_time = time.time()
    print(f"=== [Клиент {client_id}] Начало обработки заказа (задержка {delay:.2f} сек) ===")

    try:
        async with asyncio.TaskGroup() as tg:
            payment_task = tg.create_task(pay_money(client_id))
            stock_task = tg.create_task(reserve_stock(client_id))
        tasks = [payment_task, stock_task]

        run_time = time.time() - start_time
        print(f"  [Система] [Клиент {client_id}] Все проверки пройдены! Время от старта: {run_time:.2f} сек")
        delivery_date = date.today() + timedelta(days=5)

        await send_notifications(
            client_id,
            f"Заказ подтвержден. Дата получения: {delivery_date}"
        )

        run_time = time.time() - start_time
        print(f"===✅ [УСПЕХ] [Клиент {client_id}] Заказ успешно обработан за: {run_time:.2f} сек) ===")

    except* Exception as eg:
        errors_to_report = []
        payment_error = any(isinstance(e, PaymentError) for e in eg.exceptions)
        stock_error = any(isinstance(e, StockError) for e in eg.exceptions)

        if payment_error:
            errors_to_report.append("Ошибка оплаты")
        if stock_error:
            errors_to_report.append("Товар закончился")

        if payment_error and not stock_task.cancelled() and stock_task.result():
            print(f"  [Склад] [Клиент {client_id}] ⚠️ Бронирование отменено!")
            await unreserve_stock(client_id)

        if stock_error and not payment_task.cancelled() and payment_task.result():
            print(f"  [Оплата] [Клиент {client_id}] ⚠️ Процесс оплаты отменен!")
            await refund_money(client_id)

        await send_notifications(
            client_id,
            f"Заказ отменен. Причины: {', '.join(errors_to_report)}"
        )

        run_time = time.time() - start_time
        print(f"===❌ [ОШИБКА ЗАКАЗА] [Клиент {client_id}] Время выполнения: {run_time:.2f} сек ===")

async def pay_money(client_id):
    await asyncio.sleep(random.uniform(0.5, 0.8))
    if random.choice([True, True, False]):
        print(f"  [Оплата] [Клиент {client_id}] Деньги списаны")
        return True
    else:
        print(f"  [Оплата] [Клиент {client_id}] Ошибка! Недостаточно средств")
        raise PaymentError()


async def reserve_stock(client_id):
    await asyncio.sleep(random.uniform(0.5, 0.8))
    if random.choice([True, True, False]):
        print(f"  [Склад] [Клиент {client_id}] Товар забронирован")
        return True
    else:
        print(f"  [Склад] [Клиент {client_id}] Товар закончился на складе")
        raise StockError()


async def refund_money(client_id):
    await asyncio.sleep(0.5)
    print(f"  [Откат] [Клиент {client_id}] 🔄 Возврат денег...")


async def unreserve_stock(client_id):
    await asyncio.sleep(0.5)
    print(f"  [Откат] [Клиент {client_id}] 🔄 Снятие брони со склада...")


async def send_notifications(client_id, text):
    print(f"  [Уведомления] [Клиент {client_id}] 📨 {text}")
    n_start = time.time()

    results = await asyncio.gather(
        send_telegram(),
        send_email(),
        send_sms(),
        return_exceptions=True,
    )

    n_time = time.time() - n_start
    print(
        f"  [Уведомления] [Клиент {client_id}] ✅ Все 3 канала ответили за {n_time:.2f} сек. Результаты: {results}"
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

async def main():
    main_start = time.time()
    task_1 = asyncio.create_task(process_order(1))
    task_2 = asyncio.create_task(process_order(2))
    task_3 = asyncio.create_task(process_order(3))

    await asyncio.gather(task_1, task_2, task_3, return_exceptions=True)

    main_end = time.time()
    print(f" Программа отработала за {main_end - main_start:.2f} сек")
if __name__ == "__main__":
    asyncio.run(main())
