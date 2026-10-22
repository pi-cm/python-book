"""1권 Chapter 19: 웹 개발 기초 — 19.3 라우팅과 경로·쿼리 매개변수

원고: manuscript/chapters/19-web-development-basics.md (214줄부터)
"""

# ---- 원고 214줄 ----
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

맛집들 = {
    1: {"이름": "명동교자", "지역": "서울", "종류": "한식", "평점": 4.5},
    2: {"이름": "해운대 암소갈비", "지역": "부산", "종류": "한식", "평점": 4.7},
    3: {"이름": "성심당", "지역": "대전", "종류": "빵집", "평점": 4.8},
}


# 경로 매개변수: 주소의 일부가 곧 값이 된다
@app.get("/restaurants/{restaurant_id}")
def 맛집_상세(restaurant_id: int):
    return 맛집들.get(restaurant_id, {"오류": "없는 맛집입니다"})


# 쿼리 매개변수: 함수 인자 중 경로에 없는 것은 ?뒤에서 찾는다
@app.get("/restaurants")
def 맛집_검색(지역: str | None = None, 최소_평점: float = 0.0):
    결과 = [
        맛집 for 맛집 in 맛집들.values()
        if (지역 is None or 맛집["지역"] == 지역) and 맛집["평점"] >= 최소_평점
    ]
    return {"개수": len(결과), "결과": [맛집["이름"] for 맛집 in 결과]}


client = TestClient(app)
print(client.get("/restaurants/3").json())

응답 = client.get("/restaurants/99")
print(응답.status_code, 응답.json())
print(client.get("/restaurants", params={"최소_평점": 4.6}).json())
print(client.get("/restaurants?지역=서울").json())

응답 = client.get("/restaurants/세번째")
print(응답.status_code)
print(응답.json())
