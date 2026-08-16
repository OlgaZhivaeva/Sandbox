import asyncio
import time


async def main(return_exceptions: bool) -> list:
    completed_tas_count = 0

    async def my_asynk_dev(n: int) -> int:
        nonlocal completed_tas_count
        print(f"Задача с параметром {n} начала выполняться")
        k = 3 if n == 0 else 1
        await asyncio.sleep(n + k)
        res = 100 / n  # При n=0 здесь будет ZeroDivisionError
        completed_tas_count += 1
        print(f"Задача с параметром {n} выполнена")
        return int(res)

    start = time.time()

    tasks = [
        asyncio.create_task(my_asynk_dev(3)),
        asyncio.create_task(my_asynk_dev(4)),
        asyncio.create_task(my_asynk_dev(0)),
        asyncio.create_task(my_asynk_dev(1)),
        asyncio.create_task(my_asynk_dev(0)),
        asyncio.create_task(my_asynk_dev(2))
    ]
    cancelled_task_count = 0
    try:
        results = await asyncio.gather(*tasks, return_exceptions=return_exceptions)
    except Exception as e:
        print(f"\n[!] В одной из задач ошибка: {e}")

        results = []

        for task in tasks:
            if not task.done():
                task.cancel() # Если задача еще работает отменяем
                cancelled_task_count += 1
            elif not task.cancelled() and task.exception() is None:
                results.append(task.result()) # Если задача завершилась без ошибок сохраняем результат

    end = time.time()
    run_time = end - start
    print(f"Время выполнения: {run_time:.2f} сек")
    print(f"Выполнено задач: {completed_tas_count}")
    print(f"Отменено задач: {cancelled_task_count}")
    return results

print("return_exceptions = True")
return_exceptions = True
result = asyncio.run(main(return_exceptions))

if result is not None:
    print(f"Результат: {result}")

print("\nreturn_exceptions = False")
return_exceptions = False
result = asyncio.run(main(return_exceptions))

if result is not None:
    print(f"Результат: {result}")