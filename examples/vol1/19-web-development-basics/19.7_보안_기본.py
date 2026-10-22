"""1권 Chapter 19: 웹 개발 기초 — 19.7 보안 기본

원고: manuscript/chapters/19-web-development-basics.md (596줄부터)
"""

# ---- 원고 596줄 ----
import hashlib
import hmac
import secrets

반복_횟수 = 600_000  # 반복할수록 무차별 대입이 느려진다


def 비밀번호_해시(비밀번호: str) -> str:
    소금 = secrets.token_bytes(16)  # 사용자마다 다른 무작위 값
    해시 = hashlib.pbkdf2_hmac("sha256", 비밀번호.encode(), 소금, 반복_횟수)
    return f"{소금.hex()}${해시.hex()}"


def 비밀번호_확인(비밀번호: str, 저장된_값: str) -> bool:
    소금_hex, 해시_hex = 저장된_값.split("$")
    소금 = bytes.fromhex(소금_hex)
    해시 = hashlib.pbkdf2_hmac("sha256", 비밀번호.encode(), 소금, 반복_횟수)
    return hmac.compare_digest(해시.hex(), 해시_hex)


저장값_1 = 비밀번호_해시("서울2025!")
저장값_2 = 비밀번호_해시("서울2025!")
print(len(저장값_1), 저장값_1 == 저장값_2)
print(비밀번호_확인("서울2025!", 저장값_1))
print(비밀번호_확인("부산2025!", 저장값_1))

# ---- 원고 646줄 ----
import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

# 비밀 값은 코드가 아니라 환경 변수에서 읽는다
API_KEY = os.environ.get("BLOG_API_KEY", "dev-only-key")
허용_출처 = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=허용_출처,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)


def 관리자_확인(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key is None or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="API 키가 올바르지 않습니다")


@app.get("/api/posts")
def 글_목록():
    return {"글": ["첫 글", "둘째 글"]}


@app.post("/api/posts", status_code=201, dependencies=[Depends(관리자_확인)])
def 글_쓰기():
    return {"결과": "등록되었습니다"}


client = TestClient(app)
print(client.post("/api/posts").status_code, client.post("/api/posts").json())
print(client.post("/api/posts", headers={"X-API-Key": API_KEY}).status_code)

for 출처 in ("http://localhost:3000", "http://evil.example"):
    응답 = client.options(
        "/api/posts",
        headers={"Origin": 출처, "Access-Control-Request-Method": "POST"},
    )
    print(출처, 응답.status_code, 응답.headers.get("access-control-allow-origin"))
