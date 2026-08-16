import asyncio
import time


async def main() -> list:
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
    tasks = []
    results = []

    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(my_asynk_dev(3))
            t2 = tg.create_task(my_asynk_dev(4))
            t3 = tg.create_task(my_asynk_dev(0))
            t4 = tg.create_task(my_asynk_dev(1))
            t5 = tg.create_task(my_asynk_dev(0))
            t6 = tg.create_task(my_asynk_dev(2))
            tasks = [t1, t2, t3, t4, t5, t6]

    except* Exception as eg:
        print(f"\n[!] В TaskGroup произошла ошибка: {eg.exceptions}")

        for task in tasks:
            if task.done() and not task.cancelled() and task.exception() is None:
                results.append(task.result())

    end = time.time()
    run_time = end - start
    print(f"Время выполнения: {run_time:.2f} сек")
    print(f"Успешно выполнено задач: {completed_tas_count}")
    return results


result = asyncio.run(main())

if result is not None:
    print(f"Результат: {result}")
