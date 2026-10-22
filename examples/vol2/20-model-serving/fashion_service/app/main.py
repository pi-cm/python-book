# [2권 Chapter 20. FastAPI로 모델 서빙: 내 모델을 웹 서비스로 · 20.11 실습: 옷 사진 분류 서비스 완성하기 · manuscript-vol2/chapters/20-model-serving.md:1153]
"""옷 사진 분류 서비스: 9장 옷CNN을 HTTP로 내놓는다."""
import hashlib
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from pydantic import BaseModel

from app.backends import 예측기, 예측기_만들기
from app.preprocess import 사진_전처리, 사진오류, 최대_바이트

앱_버전 = "1.0.0"
최대_장수 = 32
클래스_이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트",
          "샌들", "셔츠", "운동화", "가방", "앵클부츠"]
로그 = logging.getLogger("uvicorn.error")            # uvicorn이 찍는 로그에 함께 나오게


class ClassScore(BaseModel):
    label: str
    probability: float


class Prediction(BaseModel):
    file: str
    label: str
    class_id: int
    probability: float
    top3: list[ClassScore]


@asynccontextmanager
async def lifespan(app: FastAPI):
    백엔드 = os.environ.get("MODEL_BACKEND", "onnx")
    폴더 = Path(os.environ.get("MODEL_DIR", "models"))
    app.state.예측기 = 예측기_만들기(백엔드, 폴더)
    app.state.모델_지문 = hashlib.sha256(app.state.예측기.모델_파일.read_bytes()).hexdigest()[:12]
    로그.info("모델 준비 완료: backend=%s, sha256=%s", 백엔드, app.state.모델_지문)
    yield


app = FastAPI(title="옷 사진 분류 API", version=앱_버전, lifespan=lifespan)


@app.middleware("http")
async def 처리_시간_기록(request: Request, call_next):
    시작 = time.perf_counter()
    응답 = await call_next(request)
    응답.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - 시작) * 1000:.2f}"
    return 응답


def 예측기_얻기(request: Request) -> 예측기:
    """경로 함수가 쓸 예측기. 테스트에서는 이 함수를 가짜로 바꿔 끼운다."""
    return request.app.state.예측기


def 파일_읽기(file: UploadFile) -> np.ndarray:
    데이터 = file.file.read(최대_바이트 + 1)
    if len(데이터) > 최대_바이트:
        raise HTTPException(status_code=413, detail=f"{file.filename}: 1MB보다 큽니다")
    try:
        return 사진_전처리(데이터)
    except 사진오류 as e:
        raise HTTPException(status_code=400, detail=f"{file.filename}: {e}")


def 결과_만들기(이름들: list[str], 점수: np.ndarray) -> list[Prediction]:
    확률 = np.exp(점수 - 점수.max(axis=1, keepdims=True))      # 소프트맥스 (6장)
    확률 /= 확률.sum(axis=1, keepdims=True)
    결과 = []
    for 이름, p in zip(이름들, 확률):
        상위 = [ClassScore(label=클래스_이름[i], probability=round(float(p[i]), 4))
                for i in p.argsort()[::-1][:3]]
        결과.append(Prediction(file=이름, label=상위[0].label, class_id=int(p.argmax()),
                               probability=상위[0].probability, top3=상위))
    return 결과


@app.get("/health")
def 살아있나() -> dict:
    return {"status": "ok"}


@app.get("/version")
def 버전(request: Request) -> dict:
    예측기_ = request.app.state.예측기
    return {"app": 앱_버전, "backend": 예측기_.이름, "model_file": 예측기_.모델_파일.name,
            "model_sha256": request.app.state.모델_지문}


@app.post("/predict/image")
def 사진_예측(file: UploadFile = File(...), 예측기_: 예측기 = Depends(예측기_얻기)) -> Prediction:
    x = 파일_읽기(file)[None]                                  # (1, 1, 28, 28)
    return 결과_만들기([file.filename or ""], 예측기_.점수(x))[0]


@app.post("/predict/batch")
def 여러_장_예측(files: list[UploadFile] = File(...),
                예측기_: 예측기 = Depends(예측기_얻기)) -> list[Prediction]:
    if len(files) > 최대_장수:
        raise HTTPException(status_code=413, detail=f"한 번에 {최대_장수}장까지 보낼 수 있습니다")
    x = np.stack([파일_읽기(f) for f in files])                # (N, 1, 28, 28)
    return 결과_만들기([f.filename or "" for f in files], 예측기_.점수(x))
