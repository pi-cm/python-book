import hashlib
import time
from contextlib import asynccontextmanager
from pathlib import Path

import torch
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from 서빙도구 import 모델_불러오기

앱_버전 = "1.0.0"
모델_경로 = Path("fashion_cnn.pt")


def 파일_지문(경로: Path) -> str:
    """파일 내용의 sha256 해시 앞 12글자: 내용이 한 바이트만 달라도 바뀐다."""
    return hashlib.sha256(경로.read_bytes()).hexdigest()[:12]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.모델 = 모델_불러오기(모델_경로)
    app.state.모델_지문 = 파일_지문(모델_경로)
    yield


app = FastAPI(lifespan=lifespan, version=앱_버전)


@app.middleware("http")
async def 처리_시간_기록(request: Request, call_next):
    시작 = time.perf_counter()
    응답 = await call_next(request)                       # 실제 경로 함수 실행
    응답.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - 시작) * 1000:.2f}"
    응답.headers["X-Model-Version"] = getattr(request.app.state, "모델_지문", "none")
    return 응답


@app.get("/health")
def 살아있나() -> dict:
    return {"status": "ok"}                               # 프로세스가 응답할 수 있는가


@app.get("/ready")
def 준비됐나(request: Request, response: Response) -> dict:
    if not hasattr(request.app.state, "모델"):            # 모델이 올라왔는가
        response.status_code = 503
        return {"ready": False}
    return {"ready": True}


@app.get("/version")
def 버전(request: Request) -> dict:
    return {"app": 앱_버전, "model_file": 모델_경로.name,
            "model_sha256": request.app.state.모델_지문, "torch": torch.__version__}


아직 = TestClient(app)                                   # lifespan 전: 모델이 아직 없다
print("시작 전:", 아직.get("/health").json(), 아직.get("/ready").status_code)
with TestClient(app) as client:
    print("시작 후:", client.get("/health").json(), client.get("/ready").status_code)
    응답 = client.get("/version")
    print(응답.json())
    print({k: v for k, v in 응답.headers.items() if k.startswith("x-")})
