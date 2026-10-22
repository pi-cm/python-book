# [2권 Chapter 20. FastAPI로 모델 서빙: 내 모델을 웹 서비스로 · 20.6 오래 걸리는 계산과 async · manuscript-vol2/chapters/20-model-serving.md:608]
import asyncio
import time

import httpx2
import torch
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

from 서빙도구 import 모델_불러오기

모델 = 모델_불러오기()
사진들 = torch.rand(3000, 1, 28, 28)       # 요청 하나에 계산이 꽤 걸리게 3,000장


def 무거운_추론() -> int:
    with torch.no_grad():
        return 모델(사진들).argmax(dim=1)[0].item()


def 앱_만들기(방식: str) -> FastAPI:
    app = FastAPI()

    if 방식 == "async def에서 바로":
        @app.get("/predict")
        async def 예측() -> dict:
            return {"label": 무거운_추론()}           # 이벤트 루프 위에서 계산
    elif 방식 == "그냥 def":
        @app.get("/predict")
        def 예측() -> dict:
            return {"label": 무거운_추론()}           # FastAPI가 스레드에서 실행
    else:
        @app.get("/predict")
        async def 예측() -> dict:
            return {"label": await run_in_threadpool(무거운_추론)}   # 계산만 스레드로

    @app.get("/health")
    async def 상태() -> dict:
        return {"status": "ok"}

    return app


async def 시험하기(방식: str) -> None:
    전송 = httpx2.ASGITransport(app=앱_만들기(방식))
    async with httpx2.AsyncClient(transport=전송, base_url="http://test") as client:
        async def 상태_확인() -> float:
            await asyncio.sleep(0.01)                  # 예측 요청들이 먼저 시작하게
            await client.get("/health")
            return time.perf_counter() - 시작          # 처음부터 /health 답을 받기까지

        시작 = time.perf_counter()
        예측들 = [client.get("/predict") for _ in range(4)]
        *_, 상태_시각 = await asyncio.gather(*예측들, 상태_확인())
        끝 = time.perf_counter() - 시작
        print(f"{방식:18}: 예측 4개 끝 {끝:.2f}초, /health 답 {상태_시각:.2f}초")


무거운_추론()                                        # 준비 운동
for 방식 in ["async def에서 바로", "그냥 def", "run_in_threadpool"]:
    asyncio.run(시험하기(방식))
