import asyncio
from concurrent.futures import ProcessPoolExecutor


def calculate(limit: int) -> int:
    return sum(number * number for number in range(limit))


async def main() -> None:
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as pool:
        future_a = loop.run_in_executor(pool, calculate, 1_000_000)
        future_b = loop.run_in_executor(pool, calculate, 1_000_000)

        result_a, result_b = await asyncio.gather(future_a, future_b)

    print(result_a, result_b)


if __name__ == "__main__":
    # Для ProcessPoolExecutor эта проверка особенно важна.
    asyncio.run(main())
