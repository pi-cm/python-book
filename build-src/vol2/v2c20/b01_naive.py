import statistics
import time

import torch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from torchvision import datasets
from torchvision.transforms.functional import to_tensor

from 서빙도구 import 모델_불러오기, 클래스_이름

시험셋 = datasets.FashionMNIST("data", train=False, download=True)
app = FastAPI()
미리_올린_모델 = 모델_불러오기()             # 프로그램이 시작될 때 한 번


def 예측(모델: torch.nn.Module, index: int) -> dict:
    사진, 정답 = 시험셋[index]
    with torch.no_grad():
        점수 = 모델(to_tensor(사진).unsqueeze(0))
    return {"예측": 클래스_이름[점수.argmax().item()], "정답": 클래스_이름[정답]}


@app.get("/slow/{index}")
def 느린_예측(index: int) -> dict:
    return 예측(모델_불러오기(), index)       # 요청이 올 때마다 파일에서 다시 불러온다


@app.get("/fast/{index}")
def 빠른_예측(index: int) -> dict:
    return 예측(미리_올린_모델, index)         # 이미 올려 둔 모델을 쓴다


client = TestClient(app)
print(client.get("/fast/0").json())
for 주소 in ["/slow", "/fast"]:
    걸린_시간 = []
    for i in range(50):
        시작 = time.perf_counter()
        client.get(f"{주소}/{i}")
        걸린_시간.append((time.perf_counter() - 시작) * 1000)
    print(f"{주소:5}: 요청 하나에 {statistics.median(걸린_시간):.2f}ms (중앙값)")

