from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from 서빙도구 import 모델_불러오기, 클래스_이름


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[시작] 모델을 올립니다")
    app.state.모델 = 모델_불러오기()          # 서버가 시작될 때 딱 한 번
    yield                                      # 여기서 요청을 받는다
    print("[종료] 모델을 내립니다")
    del app.state.모델


app = FastAPI(lifespan=lifespan)


@app.get("/predict/blank")
def 빈_사진_예측(request: Request) -> dict:
    모델 = request.app.state.모델              # 시작할 때 올려 둔 모델 꺼내기
    with torch.no_grad():
        점수 = 모델(torch.zeros(1, 1, 28, 28))
    return {"예측": 클래스_이름[점수.argmax().item()]}


with TestClient(app) as client:              # with 블록에 들어갈 때 시작, 나올 때 종료
    print(client.get("/predict/blank").json())
    print(client.get("/predict/blank").json())
print("with 블록 밖")

client = TestClient(app)                     # with 없이 쓰면 lifespan이 돌지 않는다
try:
    client.get("/predict/blank")
except AttributeError as e:
    print("오류:", e)
