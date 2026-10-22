# [2권 Chapter 20. FastAPI로 모델 서빙: 내 모델을 웹 서비스로 · 20.11 실습: 옷 사진 분류 서비스 완성하기 · manuscript-vol2/chapters/20-model-serving.md:1489]
"""서버에 동시에 요청을 보내 처리량과 지연 시간을 잰다. 인자: 주소 [동시 손님 수] [총 요청 수]"""
import asyncio
import statistics
import sys
import time
from pathlib import Path

import httpx2


async def 부하_주기(주소: str, 동시: int, 총: int) -> None:
    사진 = Path("tests/data/ankle_boot.png").read_bytes()
    걸린_시간: list[float] = []
    남은_번호 = iter(range(총))

    async def 손님(client: httpx2.AsyncClient) -> None:
        for _ in 남은_번호:                          # 번호표가 떨어질 때까지 계속 요청
            시작 = time.perf_counter()
            응답 = await client.post("/predict/image", files={"file": ("x.png", 사진)})
            응답.raise_for_status()
            걸린_시간.append((time.perf_counter() - 시작) * 1000)

    async with httpx2.AsyncClient(base_url=주소, timeout=10) as client:
        시작 = time.perf_counter()
        await asyncio.gather(*[손님(client) for _ in range(동시)])
        전체 = time.perf_counter() - 시작
    백분위 = statistics.quantiles(걸린_시간, n=100)
    print(f"동시 {동시}명, 요청 {총}개: 초당 {총 / 전체:,.0f}개, "
          f"p50 {백분위[49]:.1f}ms, p95 {백분위[94]:.1f}ms, p99 {백분위[98]:.1f}ms")


if __name__ == "__main__":
    주소 = sys.argv[1]
    동시 = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    총 = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    asyncio.run(부하_주기(주소, 동시, 총))
