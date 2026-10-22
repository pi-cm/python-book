"""1권 Chapter 19: 웹 개발 기초 — 연습문제

원고: manuscript/chapters/19-web-development-basics.md (983줄부터)
"""

# ---- 원고 983줄 ----
# 다음 상황에 적합한 HTTP 메서드를 고르세요
상황들 = [
    "한국 맛집 목록을 가져올 때",
    "새로운 리뷰를 작성할 때",
    "기존 맛집 정보를 완전히 수정할 때",
    "맛집의 평점만 업데이트할 때",
    "리뷰를 삭제할 때"
]

# 정답을 작성해보세요
답안 = {
    "맛집 목록 가져오기": "?",
    "리뷰 작성": "?",
    "맛집 정보 완전 수정": "?",
    "평점만 업데이트": "?",
    "리뷰 삭제": "?"
}

# ---- 원고 1004줄 ----
from fastapi import FastAPI

app = FastAPI()

# TODO: 다음 주소들을 처리하는 경로 함수를 작성하세요
# /users/123                                    -> 사용자 ID 123의 정보 조회
# /search/서울/카페                              -> 서울의 카페 검색
# /api/products?category=전자제품&min_price=10000 -> 조건에 맞는 상품 조회


@app.get("/users/{user_id}")
def 사용자_정보(user_id: int):
    # TODO: {"사용자_id": user_id} 를 돌려주세요
    pass

# 나머지 경로 함수들을 작성해보세요

# ---- 원고 1024줄 ----
from datetime import datetime

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """
    표준화된 API 응답

    {
        "상태": "성공" 또는 "실패",
        "메시지": 설명 문장,
        "데이터": 실제 데이터 (없으면 None),
        "시간": 응답을 만든 시각
    }
    """
    # TODO: 위 형식에 맞게 필드를 정의하세요
    # 힌트: 시간은 Field(default_factory=datetime.now)
    pass


def 응답_생성(데이터=None, 메시지: str = "성공") -> ApiResponse:
    # TODO: ApiResponse 객체를 만들어 돌려주세요
    pass

# ---- 원고 1052줄 ----
import re

def 한국_휴대폰번호_검증(번호: str) -> bool:
    """한국 휴대폰 번호 형식 검증 (010-0000-0000)"""
    # TODO: 정규식을 사용하여 검증하세요
    pass

def 한국어_이름_검증(이름: str) -> bool:
    """한국어 이름 검증 (2-10자, 한글만)"""
    # TODO: 한글 2-10자 검증하세요
    pass

def 이메일_검증(이메일: str) -> bool:
    """이메일 형식 검증"""
    # TODO: 기본적인 이메일 형식을 검증하세요
    pass

# 테스트
print(한국_휴대폰번호_검증("010-1234-5678"))  # True
print(한국어_이름_검증("김철수"))  # True
print(이메일_검증("test@example.com"))  # True

# ---- 원고 1077줄 ----
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class SignUpIn(BaseModel):
    # TODO: 아이디(4-20자), 이름(2-10자), 비밀번호(8자 이상) 필드를 정의하세요
    pass


class UserOut(BaseModel):
    # TODO: 응답에 내보낼 필드만 정의하세요 (비밀번호 제외)
    pass


@app.post("/api/users", status_code=201)
def 회원_가입(입력: SignUpIn) -> UserOut:
    # TODO: 18.7절의 비밀번호_해시()로 해시를 만들어 저장하고 UserOut을 돌려주세요
    pass

# ---- 원고 1103줄 ----
"""
한국 도서관 시스템을 위한 RESTful API를 설계하세요.

요구사항:
- 도서 목록 조회, 등록, 수정, 삭제
- 사용자 목록 조회, 등록
- 도서 대출/반납 기능
- 대출 현황 조회

다음 엔드포인트들을 설계하고 구현하세요:
1. GET /api/books - 도서 목록 조회
2. POST /api/books - 새 도서 등록
3. GET /api/books/{book_id} - 도서 상세 조회
4. PUT /api/books/{book_id} - 도서 정보 수정
5. POST /api/books/{book_id}/borrow - 도서 대출 (이미 대출 중이면 409)
6. POST /api/books/{book_id}/return - 도서 반납
7. GET /api/users/{user_id}/borrowed - 사용자 대출 현황
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="한국 도서관 API")

# TODO: 위의 요구사항에 맞는 모델과 API를 구현하세요

# ---- 원고 1132줄 ----
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile

app = FastAPI()

# 허용되는 파일 확장자
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


def 허용된_파일인가(filename: str) -> bool:
    """파일 확장자 검증"""
    # TODO: Path(filename).suffix를 이용해 확장자가 허용되는지 검증하세요
    pass


@app.post("/api/upload", status_code=201)
async def 파일_업로드(file: UploadFile):
    """
    파일 업로드 처리
    - 확장자 검사 (허용되지 않으면 400)
    - 파일 크기 제한 5MB (넘으면 413)
    - 한글 파일명 지원, 경로 문자(../) 제거
    - 저장한 파일 이름과 크기를 응답
    """
    # TODO: 내용은 await file.read()로 읽습니다
    pass

# ---- 원고 1164줄 ----
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()

토큰_저장소: dict[str, str] = {}  # 토큰 -> 사용자 아이디


@app.post("/api/login")
def 로그인(아이디: str, 비밀번호: str):
    """
    - 비밀번호를 확인하고 secrets.token_urlsafe()로 토큰 발급
    - 토큰_저장소에 기록하고 토큰을 응답
    - 틀리면 401
    """
    # TODO
    pass


def 로그인_사용자(authorization: str | None = Header(default=None)) -> str:
    """'Bearer 토큰' 형식의 헤더를 확인해 사용자 아이디를 돌려주는 의존성"""
    # TODO: 없거나 모르는 토큰이면 401
    pass


@app.get("/api/profile")
def 프로필(사용자: str = Depends(로그인_사용자)):
    # TODO: 로그인한 사용자의 정보를 돌려주세요
    pass


@app.post("/api/logout")
def 로그아웃(authorization: str | None = Header(default=None)):
    # TODO: 토큰_저장소에서 토큰을 지우세요
    pass

# ---- 원고 1204줄 ----
import math

from fastapi import FastAPI, Query

app = FastAPI()

# 샘플 데이터 (한국 도시 100개)
한국_도시들 = [f"도시_{i}" for i in range(1, 101)]


def 페이지네이션(데이터_리스트: list, 페이지: int = 1, 페이지_크기: int = 10) -> dict:
    """
    Returns:
        {
            "데이터": 현재 페이지 데이터,
            "페이지정보": {
                "현재_페이지": 페이지,
                "총_페이지수": 총 페이지 수,
                "총_항목수": 전체 항목 수,
                "페이지_크기": 페이지 크기,
                "이전_페이지": 이전 페이지 번호 (없으면 None),
                "다음_페이지": 다음 페이지 번호 (없으면 None)
            }
        }
    """
    # TODO: 페이지네이션 로직을 구현하세요 (math.ceil 활용)
    pass


@app.get("/api/cities")
def 도시_목록(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
):
    # TODO: 페이지네이션을 적용한 결과를 돌려주세요
    pass

# ---- 원고 1244줄 ----
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
logger = logging.getLogger("korean_api")


class 재고부족오류(Exception):
    def __init__(self, 상품명: str):
        self.상품명 = 상품명


@app.exception_handler(재고부족오류)
async def 재고부족_처리(request: Request, exc: 재고부족오류) -> JSONResponse:
    # TODO: 409 상태 코드와 {"detail": "○○ 재고가 부족합니다"}를 돌려주고
    #       경고 로그를 남기세요
    pass


@app.exception_handler(Exception)
async def 예상못한_오류_처리(request: Request, exc: Exception) -> JSONResponse:
    # TODO: 500 상태 코드와 내부 정보가 드러나지 않는 메시지를 돌려주고,
    #       로그에는 자세히 남기세요
    pass


@app.post("/api/orders")
def 주문():
    raise 재고부족오류("무선 이어폰")
