import io
import statistics
import time
from contextlib import asynccontextmanager

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.testclient import TestClient
from PIL import Image

from 서빙도구 import 시험_사진_파일


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/predict/image")
def 사진_예측(request: Request, response: Response, file: UploadFile = File(...)) -> dict:
    t0 = time.perf_counter()
    사진 = Image.open(io.BytesIO(file.file.read())).convert("L").resize((28, 28))
    x = np.asarray(사진, dtype=np.float32)[None, None] / 255
    t1 = time.perf_counter()
    점수 = request.app.state.세션.run(["logits"], {"image": x})[0]
    t2 = time.perf_counter()
    # 서버 안에서 단계별로 걸린 시간을 표준 헤더(Server-Timing)로 알려 준다
    전처리_ms, 모델_ms = (t1 - t0) * 1000, (t2 - t1) * 1000
    response.headers["Server-Timing"] = f"pre;dur={전처리_ms:.3f}, model;dur={모델_ms:.3f}"
    return {"class_id": int(점수.argmax())}


전체, 전처리, 모델 = [], [], []
with TestClient(app) as client:
    for 내용, _ in 시험_사진_파일(500):
        시작 = time.perf_counter()
        응답 = client.post("/predict/image", files={"file": ("x.png", 내용)})
        전체.append((time.perf_counter() - 시작) * 1000)
        단계 = dict(p.split(";dur=") for p in 응답.headers["server-timing"].split(", "))
        전처리.append(float(단계["pre"]))
        모델.append(float(단계["model"]))

print(f"첫 요청: {전체[0]:.2f}ms")
나머지 = 전체[1:]
백분위 = statistics.quantiles(나머지, n=100)                  # 1~99번째 백분위수
print(f"나머지 {len(나머지)}개: 평균 {statistics.mean(나머지):.2f}ms, p50 {백분위[49]:.2f}ms, "
      f"p95 {백분위[94]:.2f}ms, p99 {백분위[98]:.2f}ms, 최대 {max(나머지):.2f}ms")
print(f"그중 서버 안 (중앙값): 전처리 {statistics.median(전처리):.3f}ms, "
      f"모델 {statistics.median(모델):.3f}ms")
