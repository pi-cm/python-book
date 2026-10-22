from contextlib import asynccontextmanager
from typing import Annotated

import torch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from torchvision import datasets
from torchvision.transforms.functional import to_tensor

from 서빙도구 import 모델_불러오기, 클래스_이름

픽셀 = Annotated[float, Field(ge=0.0, le=1.0)]                  # 칸 하나: 0~1 사이 실수
한_줄 = Annotated[list[픽셀], Field(min_length=28, max_length=28)]


class PixelInput(BaseModel):
    pixels: Annotated[list[한_줄], Field(min_length=28, max_length=28)]   # 28줄 × 28칸


class Prediction(BaseModel):
    label: str
    class_id: int
    probability: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.모델 = 모델_불러오기()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/predict")
def 예측(입력: PixelInput, request: Request) -> Prediction:
    x = torch.tensor(입력.pixels).reshape(1, 1, 28, 28)
    with torch.no_grad():
        확률 = request.app.state.모델(x).softmax(dim=1)[0]
    번호 = 확률.argmax().item()
    return Prediction(label=클래스_이름[번호], class_id=번호,
                      probability=round(확률[번호].item(), 4))


사진, 정답 = datasets.FashionMNIST("data", train=False, download=True)[0]
픽셀값 = to_tensor(사진)[0].tolist()                               # 28 × 28 리스트
with TestClient(app) as client:
    응답 = client.post("/predict", json={"pixels": 픽셀값})
    print(응답.status_code, 응답.json(), "정답:", 클래스_이름[정답])

    잘못된_입력 = {"pixels": 픽셀값[:27]}                             # 27줄뿐
    잘못된_입력["pixels"][3][5] = 2.0                                 # 1보다 큰 값
    for 차례 in range(2):
        응답 = client.post("/predict", json=잘못된_입력)
        print(응답.status_code, [(오류["loc"], 오류["msg"]) for 오류 in 응답.json()["detail"]])
        잘못된_입력["pixels"][3][5] = 0.5                             # 값을 고쳐서 다시 보내기
    print(sorted(client.get("/openapi.json").json()["components"]["schemas"]))
