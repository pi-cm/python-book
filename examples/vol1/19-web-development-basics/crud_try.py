# [1권 Chapter 19: 웹 개발 기초 · 19.6 RESTful API 설계와 구현 · manuscript/chapters/19-web-development-basics.md:537]
# crud_try.py
from fastapi.testclient import TestClient

from crud import app

client = TestClient(app)


def 요청(메서드: str, 주소: str, **옵션) -> None:
    응답 = client.request(메서드, 주소, **옵션)
    본문 = 응답.json() if 응답.content else "(본문 없음)"
    print(f"{메서드:6} {주소:18} -> {응답.status_code} {본문}")


요청("POST", "/api/products", json={"이름": "무선 이어폰", "가격": 89000, "재고": 30})
요청("POST", "/api/products", json={"이름": "보조배터리", "가격": 25000})
요청("GET", "/api/products")
요청("PUT", "/api/products/2", json={"이름": "보조배터리", "가격": 23000, "재고": 5})
요청("DELETE", "/api/products/1")
요청("GET", "/api/products/1")
요청("DELETE", "/api/products/1")
