import asyncio
import io
from contextlib import asynccontextmanager

import httpx2
import numpy as np
import torch
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image

from 서빙도구 import 모델_불러오기, 시험_사진_파일, 클래스_이름


class 배치_모으기:
    """따로 온 요청을 잠깐 모았다가 모델을 한 번만 부른다."""

    def __init__(self, 모델: torch.nn.Module, 최대_장수: int = 32,
                 최대_대기: float = 0.005) -> None:
        self.모델, self.최대_장수, self.최대_대기 = 모델, 최대_장수, 최대_대기
        self.큐: asyncio.Queue = asyncio.Queue()
        self.배치_기록: list[int] = []

    async def 예측(self, x: np.ndarray) -> int:
        결과_자리 = asyncio.get_running_loop().create_future()   # 나중에 답이 들어올 빈자리
        await self.큐.put((x, 결과_자리))
        return await 결과_자리                                   # 답이 채워질 때까지 기다린다

    async def 계속_돌리기(self) -> None:
        루프 = asyncio.get_running_loop()
        while True:
            묶음 = [await self.큐.get()]                         # 첫 요청이 올 때까지 기다리고
            마감 = 루프.time() + self.최대_대기                   # 그때부터 잠깐만 더 모은다
            while len(묶음) < self.최대_장수 and (남은 := 마감 - 루프.time()) > 0:
                try:
                    묶음.append(await asyncio.wait_for(self.큐.get(), 남은))
                except TimeoutError:
                    break
            x = torch.from_numpy(np.stack([x for x, _ in 묶음]))
            번호들 = await run_in_threadpool(self.계산, x)       # 계산은 스레드에서 (20.6절)
            for (_, 결과_자리), 번호 in zip(묶음, 번호들):
                결과_자리.set_result(번호)
            self.배치_기록.append(len(묶음))

    def 계산(self, x: torch.Tensor) -> list[int]:
        with torch.no_grad():
            return self.모델(x).argmax(dim=1).tolist()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.모으기 = 배치_모으기(모델_불러오기())
    일꾼 = asyncio.create_task(app.state.모으기.계속_돌리기())   # 뒤에서 계속 도는 작업
    yield
    일꾼.cancel()


app = FastAPI(lifespan=lifespan)


@app.post("/predict/image")
async def 사진_예측(request: Request, file: UploadFile = File(...)) -> dict:
    # 28 × 28짜리 작은 사진이라 이벤트 루프에서 바로 전처리했다. 무거운 전처리라면 20.6절처럼 스레드로 넘긴다
    사진 = Image.open(io.BytesIO(await file.read())).convert("L").resize((28, 28))
    x = np.asarray(사진, dtype=np.float32)[None] / 255
    return {"label": 클래스_이름[await request.app.state.모으기.예측(x)]}


async def 손님_64명() -> None:
    파일들 = 시험_사진_파일(64)
    async with lifespan(app):                                   # TestClient 대신 직접 시작·종료
        전송 = httpx2.ASGITransport(app=app)
        async with httpx2.AsyncClient(transport=전송, base_url="http://test") as client:
            요청들 = [client.post("/predict/image", files={"file": ("x.png", 내용)})
                      for 내용, _ in 파일들]
            응답들 = await asyncio.gather(*요청들)
        맞힘 = sum(r.json()["label"] == 클래스_이름[답] for r, (_, 답) in zip(응답들, 파일들))
        기록 = app.state.모으기.배치_기록
        print(f"요청 {len(응답들)}개 → 모델 호출 {len(기록)}번, 배치 크기 {기록}")
        print(f"64장 중 {맞힘}장 정답")


asyncio.run(손님_64명())
