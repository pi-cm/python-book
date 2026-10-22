import os
import statistics
import time
from contextlib import asynccontextmanager
from typing import Protocol

import numpy as np
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel
from torchvision import datasets


class 예측기(Protocol):
    """백엔드가 지켜야 할 약속: (N, 1, 28, 28) 배열을 받아 (N, 10) 점수를 돌려준다."""
    이름: str

    def 점수(self, x: np.ndarray) -> np.ndarray: ...


class 파이토치_예측기:
    이름 = "torch"

    def __init__(self, 경로: str = "fashion_cnn.pt") -> None:
        import torch                                   # 이 백엔드를 고를 때만 불러온다
        from 서빙도구 import 모델_불러오기
        self.torch, self.모델 = torch, 모델_불러오기(경로)

    def 점수(self, x: np.ndarray) -> np.ndarray:
        with self.torch.no_grad():
            return self.모델(self.torch.from_numpy(x)).numpy()


class ONNX_예측기:
    이름 = "onnx"

    def __init__(self, 경로: str = "fashion_cnn.onnx") -> None:
        import onnxruntime as ort
        self.세션 = ort.InferenceSession(경로, providers=["CPUExecutionProvider"])

    def 점수(self, x: np.ndarray) -> np.ndarray:
        return self.세션.run(["logits"], {"image": x})[0]


def 예측기_고르기() -> 예측기:
    백엔드 = os.environ.get("MODEL_BACKEND", "onnx")       # 코드는 그대로, 설정으로 바꾼다
    return {"torch": 파이토치_예측기, "onnx": ONNX_예측기}[백엔드]()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.예측기 = 예측기_고르기()
    yield


app = FastAPI(lifespan=lifespan)


class PixelBatch(BaseModel):
    pixels: list[list[list[float]]]                   # (N, 28, 28)


@app.post("/predict")
def 예측(입력: PixelBatch, request: Request) -> dict:
    x = np.asarray(입력.pixels, dtype=np.float32)[:, None]      # (N, 1, 28, 28)
    예측기_ = request.app.state.예측기
    return {"backend": 예측기_.이름, "class_ids": 예측기_.점수(x).argmax(axis=1).tolist()}


시험셋 = datasets.FashionMNIST("data", train=False, download=True)
사진들 = (시험셋.data[:200].numpy() / 255).astype(np.float32)
결과 = {}
for 백엔드 in ["torch", "onnx"]:
    os.environ["MODEL_BACKEND"] = 백엔드
    with TestClient(app) as client:
        응답 = client.post("/predict", json={"pixels": 사진들.tolist()}).json()
        결과[백엔드] = 응답["class_ids"]
        정확도 = np.mean(np.array(응답["class_ids"]) == 시험셋.targets[:200].numpy())
        print(f"백엔드 {응답['backend']:5}: 200장 정확도 {정확도:.1%}")
print("두 백엔드의 예측이 모두 같은가:", 결과["torch"] == 결과["onnx"])

print("모델 계산 시간(중앙값):")
for 장수 in [1, 64]:
    x = 사진들[:장수, None]
    줄 = []
    for 예측기_ in [파이토치_예측기(), ONNX_예측기()]:
        예측기_.점수(x)                                      # 준비 운동
        기록 = []
        for _ in range(200):
            시작 = time.perf_counter()
            예측기_.점수(x)
            기록.append((time.perf_counter() - 시작) * 1000)
        줄.append(statistics.median(기록))
    print(f"  {장수:2}장: torch {줄[0]:.3f}ms, onnx {줄[1]:.3f}ms → {줄[0] / 줄[1]:.1f}배")
