import io
import statistics
import time
from contextlib import asynccontextmanager

import numpy as np
import torch
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.testclient import TestClient
from PIL import Image
from torchvision import datasets

from 서빙도구 import 모델_불러오기, 클래스_이름

최대_장수 = 32


def 사진_전처리(데이터: bytes) -> np.ndarray:
    사진 = Image.open(io.BytesIO(데이터)).convert("L").resize((28, 28))
    return np.asarray(사진, dtype=np.float32)[None] / 255     # (1, 28, 28)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.모델 = 모델_불러오기()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/predict/image")
def 한_장_예측(request: Request, file: UploadFile = File(...)) -> dict:
    x = torch.from_numpy(사진_전처리(file.file.read())).unsqueeze(0)    # (1, 1, 28, 28)
    with torch.no_grad():
        번호 = request.app.state.모델(x).argmax(dim=1).item()
    return {"label": 클래스_이름[번호]}


@app.post("/predict/batch")
def 여러_장_예측(request: Request, files: list[UploadFile] = File(...)) -> list[dict]:
    if len(files) > 최대_장수:
        raise HTTPException(status_code=413, detail=f"한 번에 {최대_장수}장까지 보낼 수 있습니다")
    x = torch.from_numpy(np.stack([사진_전처리(f.file.read()) for f in files]))   # (N, 1, 28, 28)
    with torch.no_grad():
        번호들 = request.app.state.모델(x).argmax(dim=1).tolist()
    return [{"file": f.filename, "label": 클래스_이름[n]} for f, n in zip(files, 번호들)]


def png_바이트(사진: Image.Image) -> bytes:
    버퍼 = io.BytesIO()
    사진.save(버퍼, format="PNG")
    return 버퍼.getvalue()


시험셋 = datasets.FashionMNIST("data", train=False, download=True)
파일들 = [("files", (f"{i}.png", png_바이트(시험셋[i][0]))) for i in range(32)]
with TestClient(app) as client:
    print(client.post("/predict/batch", files=파일들[:3]).json())
    print(client.post("/predict/batch", files=파일들 * 2).json())          # 64장

    따로, 함께 = [], []
    for _ in range(7):
        시작 = time.perf_counter()
        for _, (이름, 내용) in 파일들:
            client.post("/predict/image", files={"file": (이름, 내용)})
        따로.append(time.perf_counter() - 시작)
        시작 = time.perf_counter()
        client.post("/predict/batch", files=파일들)
        함께.append(time.perf_counter() - 시작)
    print(f"32장을 요청 32번으로: {statistics.median(따로) * 1000:.1f}ms")
    print(f"32장을 요청 1번으로 : {statistics.median(함께) * 1000:.1f}ms")
