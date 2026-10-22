"""1권 Chapter 19: 웹 개발 기초 — 19.5 요청 본문 검증: Pydantic 모델

원고: manuscript/chapters/19-web-development-basics.md (373줄부터)
"""

# ---- 원고 373줄 ----
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI()


class ReviewCreate(BaseModel):
    작성자: str = Field(min_length=2, max_length=10)
    평점: int = Field(ge=1, le=5)
    내용: str = Field(min_length=10)
    재방문: bool = False


리뷰들: list[dict] = []


@app.post("/restaurants/{restaurant_id}/reviews", status_code=201)
def 리뷰_작성(restaurant_id: int, 리뷰: ReviewCreate):
    저장할_리뷰 = {
        "id": len(리뷰들) + 1,
        "restaurant_id": restaurant_id,
        **리뷰.model_dump(),
    }
    리뷰들.append(저장할_리뷰)
    return 저장할_리뷰


client = TestClient(app)

응답 = client.post(
    "/restaurants/3/reviews",
    json={"작성자": "김철수", "평점": "5", "내용": "튀김소보로가 정말 맛있어요!"},
)
print(응답.status_code, 응답.json())

응답 = client.post(
    "/restaurants/3/reviews",
    json={"작성자": "김", "평점": 7, "내용": "맛있어요"},
)
print(응답.status_code)
for 오류 in 응답.json()["detail"]:
    print(오류["loc"], 오류["msg"])
