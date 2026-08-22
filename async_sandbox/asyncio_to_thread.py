import asyncio
import time


def blocking_io(name: str) -> str:
    time.sleep(1)  # Имитируем блокирующую операцию.
    return f"{name} готов"


async def main() -> None:
    results = await asyncio.gather(
        asyncio.to_thread(blocking_io, "A"),
        asyncio.to_thread(blocking_io, "B"),
        asyncio.to_thread(blocking_io, "C"),
    )

    print(results)


asyncio.run(main())
