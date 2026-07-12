# import asyncio
# import time
#
# async def fetch_one():
#     time.sleep(0.1)
#     await asyncio.sleep(0.1)
#     return 1
#
# async def main():
#     xs = await asyncio.gather(*(fetch_one() for _ in range(3)))
#     print(sum(xs))  # 3
#
# asyncio.run(main())
#
# async def agen():
#     for i in range(3):
#         await asyncio.sleep(0.01)
#         yield i

# async def consume():
#     async for x in agen():
#         print(x)
# asyncio.run(consume())
#
#
#
# def work(name):
#     print(f"{name} started")
#     time.sleep(2)
#     print(f"{name} finished")
#
#
# start = time.time()
#
# work("A")
# work("B")
#
# print(f"Time: {time.time() - start:.2f} sec")
#
#
# import asyncio
# import time
#
# async def work(name):
#     print(f"{name} started")
#     await asyncio.sleep(2)
#     print(f"{name} finished")
#
#
# async def main():
#     start = time.time()
#
#     await asyncio.gather(
#         work("A"),
#         work("B")
#     )
#
#     print(f"Time: {time.time() - start:.2f} sec")
#
#
#
# asyncio.run(main())

# ------------------------------------------------------------------------------------

import asyncio
import random

# async def fetch(i: int) -> int:
#     try:
#         # Имитация IO
#         await asyncio.sleep(random.uniform(0.05, 0.2))
#         if i == 2:
#             raise RuntimeError("boom")
#         return i
#     except asyncio.CancelledError:
#         # Освобождаем ресурсы и пробрасываем дальше
#         print(f"task {i} cancelled")
#         raise
#
# async def main() -> None:
#     tasks = [asyncio.create_task(fetch(i)) for i in range(5)]
#     try:
#         # Ожидаем с таймаутом и сходу отменяем при первой ошибке
#         results = await asyncio.wait_for(
#             asyncio.gather(*tasks),
#             timeout=1.0,
#         )
#         print("results:", results)
#     except (asyncio.TimeoutError, Exception) as e:
#         # Грейсфул-шатдаун: отменяем все и дожидаемся
#         for t in tasks:
#             t.cancel()
#         await asyncio.gather(*tasks, return_exceptions=True)
#         print("failed:", repr(e))
#
# if __name__ == "__main__":
#     asyncio.run(main())

# async def io_imitation(i: int, t: float) -> int:
#     try:
#         print(f"Task {i} started")
#         await asyncio.sleep(t)
#         if t > 1:
#             raise RuntimeError("boom")
#         print(f"Task {i} finished")
#         return i
#     except asyncio.CancelledError:
#         print(f"task {i} cancelled")
#         raise
#
# async def main() -> None:
#     tasks = [
#         asyncio.create_task(io_imitation(1, 0.2)),
#         asyncio.create_task(io_imitation(2, 0.1)),
#         asyncio.create_task(io_imitation(3, 0.5)),
#         asyncio.create_task(io_imitation(4, 1.2)),
#     ]
#     results = await asyncio.gather(*tasks, return_exceptions=True)
#     print(results)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())


def func(from_, to=10, step=1):
    for idx in range(from_, to, step):
        yield idx
        return idx
    return -1

f = func(2, -5, -2)
print(next(f))
print(next(f))
f.close()
print(next(f))
