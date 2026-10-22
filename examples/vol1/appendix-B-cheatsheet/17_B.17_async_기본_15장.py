"""1권 부록 B. 한눈에 보는 파이썬 — B.17 async 기본 (15장)

원고: manuscript/appendix/B-cheatsheet.md (798줄부터)
"""

# ---- 원고 798줄 ----
import asyncio

async def fetch(name, delay):
    await asyncio.sleep(delay)        # 기다리는 동안 다른 작업에 양보
    return f"{name} 완료"

async def main():
    results = await asyncio.gather(fetch("A", 0.2), fetch("B", 0.1))
    print(results)                    # ['A 완료', 'B 완료']

    async with asyncio.TaskGroup() as tg:     # 3.11 이상
        t1 = tg.create_task(fetch("C", 0.1))
        t2 = tg.create_task(fetch("D", 0.1))
    print(t1.result(), t2.result())   # C 완료 D 완료

asyncio.run(main())
