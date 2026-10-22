"""1권 레퍼런스 D. 특수 메서드 — 비동기

원고: manuscript/references/D-special-methods.md (456줄부터)
"""

# ---- 원고 456줄 ----
import asyncio

class Countdown:
    def __init__(self, n: int) -> None:
        self.n = n

    def __aiter__(self) -> "Countdown":       # async for
        return self

    async def __anext__(self) -> int:
        if self.n == 0:
            raise StopAsyncIteration
        await asyncio.sleep(0)
        self.n -= 1
        return self.n + 1

class Session:
    async def __aenter__(self) -> "Session":  # async with
        print("접속")
        return self

    async def __aexit__(self, *exc: object) -> None:
        print("종료")

class Ready:
    def __await__(self):                      # await Ready()
        yield from asyncio.sleep(0).__await__()
        return "준비 완료"

async def main() -> None:
    async with Session():
        print([n async for n in Countdown(3)])
        print(await Ready())

asyncio.run(main())
# 접속 / [3, 2, 1] / 준비 완료 / 종료 (한 줄씩 출력)
