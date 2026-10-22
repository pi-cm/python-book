# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.12 실습: 맛집 추천 API 완성하기 · manuscript-vol2/chapters/21-capstone-recommender.md:1445]
"""맛집 추천 서비스: 미리 계산한 사용자·식당 벡터로 추천한다."""
import hashlib
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.recommender import 벡터추천기, 추천기, 추천목록

앱_버전 = "1.0.0"
Area = Literal["강남", "홍대", "성수", "종로", "여의도", "잠실", "이태원", "신촌"]   # catalog.json과 같아야 한다
로그 = logging.getLogger("uvicorn.error")


class Restaurant(BaseModel):
    id: int
    name: str
    area: str
    cuisine: str
    price: int
    score: float


class Recommendations(BaseModel):
    strategy: str                         # personal, new_user, similar
    items: list[Restaurant]


class NewUserRequest(BaseModel):
    home: Area
    visited: list[int] = Field(default=[], max_length=50)
    k: int = Field(default=10, ge=1, le=50)


@asynccontextmanager
async def lifespan(app: FastAPI):
    폴더 = Path(os.environ.get("ARTIFACT_DIR", "artifacts"))
    app.state.추천기 = 벡터추천기(폴더)
    app.state.지문 = hashlib.sha256((폴더 / "vectors.npz").read_bytes()).hexdigest()[:12]
    로그.info("벡터 준비 완료: 사용자 %d명, 식당 %d곳, sha256=%s",
             app.state.추천기.사용자_수(), len(app.state.추천기.식당), app.state.지문)
    yield


app = FastAPI(title="맛집 추천 API", version=앱_버전, lifespan=lifespan)


@app.middleware("http")
async def 처리_시간_기록(request: Request, call_next):
    시작 = time.perf_counter()
    응답 = await call_next(request)
    응답.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - 시작) * 1000:.2f}"
    return 응답


def 추천기_얻기(request: Request) -> 추천기:
    """경로 함수가 쓸 추천기. 테스트에서는 가짜로 바꿔 끼운다."""
    return request.app.state.추천기


def 응답_만들기(추천기_: 추천기, 전략: str, 목록: 추천목록) -> Recommendations:
    식당들 = [Restaurant(**{키: 추천기_.식당[i][키] for 키 in ("id", "name", "area", "cuisine", "price")},
                         score=점수) for i, 점수 in 목록]
    return Recommendations(strategy=전략, items=식당들)


def 식당_번호_확인(추천기_: 추천기, 번호들: list[int]) -> None:
    for 번호 in 번호들:
        if not 0 <= 번호 < len(추천기_.식당):
            raise HTTPException(status_code=404, detail=f"식당 {번호}을(를) 찾을 수 없습니다")


@app.get("/health")
def 살아있나() -> dict:
    return {"status": "ok"}


@app.get("/version")
def 버전(request: Request) -> dict:
    return {"app": 앱_버전, "vectors_sha256": request.app.state.지문}


@app.get("/users/{user_id}/recommendations")
def 사용자_추천(user_id: int, k: Annotated[int, Query(ge=1, le=50)] = 10, area: Area | None = None,
              추천기_: 추천기 = Depends(추천기_얻기)) -> Recommendations:
    if not 0 <= user_id < 추천기_.사용자_수():
        raise HTTPException(status_code=404, detail=f"사용자 {user_id}을(를) 찾을 수 없습니다")
    전략, 목록 = 추천기_.추천(user_id, k, area)
    return 응답_만들기(추천기_, 전략, 목록)


@app.post("/recommendations/new-user")
def 새_사용자_추천(요청: NewUserRequest, 추천기_: 추천기 = Depends(추천기_얻기)) -> Recommendations:
    식당_번호_확인(추천기_, 요청.visited)
    return 응답_만들기(추천기_, "new_user", 추천기_.새_사용자_추천(요청.home, 요청.visited, 요청.k))


@app.get("/restaurants/{restaurant_id}/similar")
def 비슷한_식당(restaurant_id: int, k: Annotated[int, Query(ge=1, le=50)] = 5,
              추천기_: 추천기 = Depends(추천기_얻기)) -> Recommendations:
    식당_번호_확인(추천기_, [restaurant_id])
    return 응답_만들기(추천기_, "similar", 추천기_.비슷한_식당(restaurant_id, k))
