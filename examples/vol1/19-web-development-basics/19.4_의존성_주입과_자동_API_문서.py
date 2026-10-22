"""1권 Chapter 19: 웹 개발 기초 — 19.4 의존성 주입과 자동 API 문서

원고: manuscript/chapters/19-web-development-basics.md (288줄부터)
"""

# ---- 원고 288줄 ----
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI(title="맛집 API", version="1.0.0")

맛집_이름들 = [f"맛집_{번호}" for 번호 in range(1, 26)]


# 여러 경로가 함께 쓰는 '페이지 나누기' 규칙
def 페이지_정보(page: int = 1, size: int = 10) -> dict:
    return {"시작": (page - 1) * size, "끝": page * size, "page": page}


# 요청마다 자원을 열고, 응답이 끝나면 닫는 의존성
def 저장소_연결():
    print("  [저장소 열기]")
    yield 맛집_이름들
    print("  [저장소 닫기]")


@app.get("/restaurants")
def 맛집_목록(
    페이지: dict = Depends(페이지_정보),
    저장소: list = Depends(저장소_연결),
):
    print("  [경로 함수 실행]")
    return {"page": 페이지["page"], "결과": 저장소[페이지["시작"]:페이지["끝"]]}


client = TestClient(app)
print(client.get("/restaurants", params={"page": 3, "size": 4}).json())

# ---- 원고 339줄 ----
스키마 = client.get("/openapi.json").json()
print(스키마["openapi"], 스키마["info"])
for 경로, 메서드들 in 스키마["paths"].items():
    for 메서드, 정보 in 메서드들.items():
        이름들 = [매개변수["name"] for 매개변수 in 정보["parameters"]]
        print(메서드.upper(), 경로, 정보["summary"], 이름들)

화면 = client.get("/docs")
print(화면.status_code, 화면.headers["content-type"])
