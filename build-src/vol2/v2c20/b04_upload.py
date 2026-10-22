import io
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.testclient import TestClient
from PIL import Image, UnidentifiedImageError
from torchvision import datasets
from torchvision.transforms.functional import to_tensor

from 서빙도구 import 모델_불러오기, 클래스_이름

최대_바이트 = 1_000_000                       # 사진 한 장은 1MB까지만 받는다


def 사진_전처리(데이터: bytes) -> torch.Tensor:
    """올라온 사진 파일을 학습 때와 같은 (1, 1, 28, 28) 텐서로 바꾼다."""
    try:
        사진 = Image.open(io.BytesIO(데이터))
        사진 = 사진.convert("L").resize((28, 28))          # 흑백, 28 × 28
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="사진 파일이 아닙니다")
    return to_tensor(사진).unsqueeze(0)                    # 0~1 실수, 배치 차원 추가


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.모델 = 모델_불러오기()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/predict/image")
def 사진_예측(request: Request, file: UploadFile = File(...)) -> dict:
    데이터 = file.file.read(최대_바이트 + 1)           # 한도보다 1바이트만 더 읽어 본다
    if len(데이터) > 최대_바이트:
        raise HTTPException(status_code=413, detail="파일이 너무 큽니다")
    with torch.no_grad():
        확률 = request.app.state.모델(사진_전처리(데이터)).softmax(dim=1)[0]
    return {"파일": file.filename, "예측": 클래스_이름[확률.argmax().item()],
            "확률": round(확률.max().item(), 4)}


def png_바이트(사진: Image.Image) -> bytes:
    버퍼 = io.BytesIO()
    사진.save(버퍼, format="PNG")
    return 버퍼.getvalue()


시험셋 = datasets.FashionMNIST("data", train=False, download=True)
사진, 정답 = 시험셋[1]
큰_컬러 = 사진.convert("RGB").resize((280, 280))               # 열 배 크게, 컬러로 바꾼 사진
보낼_것들 = {
    "옷.png": png_바이트(사진),
    "큰_컬러.png": png_바이트(큰_컬러),
    "메모.txt": "사진이 아니에요".encode(),
    "큰_파일.png": bytes(2_000_000),
}
with TestClient(app) as client:
    print("정답:", 클래스_이름[정답])
    for 이름, 내용 in 보낼_것들.items():
        응답 = client.post("/predict/image", files={"file": (이름, 내용)})
        print(f"{이름:10} {len(내용):>9,}바이트 → {응답.status_code} {응답.json()}")
