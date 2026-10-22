# [1권 Chapter 19: 웹 개발 기초 · 실습 프로젝트: 한국형 블로그 시스템 · manuscript/chapters/19-web-development-basics.md:912]
# try_blog.py - 서버를 띄우지 않고 블로그 API 확인하기
import os
import tempfile
from pathlib import Path

os.environ["BLOG_DB"] = str(Path(tempfile.mkdtemp()) / "blog.db")  # 연습용 새 DB

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)

새_글들 = [
    {"title": "부산 돼지국밥 투어", "content": "서면에서 시작해 남포동까지 걸었어요.",
     "author": "김부산", "category": "맛집", "tags": ["부산", "국밥"]},
    {"title": "FastAPI 첫걸음", "content": "타입 힌트만으로 검증이 되다니 놀랍네요.",
     "author": "이개발", "category": "개발", "tags": ["파이썬"]},
    {"title": "제주 올레길 7코스", "content": "외돌개에서 시작하는 바닷길입니다.",
     "author": "박제주", "category": "여행"},
]
for 글 in 새_글들:
    응답 = client.post("/api/posts", json=글)
    print(응답.status_code, 응답.json()["id"], 응답.json()["title"])

목록 = client.get("/api/posts", params={"size": 2}).json()
print("최신 2개:", [글["title"] for 글 in 목록])
print("맛집:", [글["title"] for 글 in client.get("/api/posts?category=맛집").json()])
print("검색:", [글["title"] for 글 in client.get("/api/posts?q=바닷길").json()])

client.get("/api/posts/1")
글 = client.get("/api/posts/1").json()
print("조회수:", 글["views"], "태그:", 글["tags"])

글 = client.patch("/api/posts/2", json={"title": "FastAPI 두 번째 걸음"}).json()
print("수정:", 글["title"], "/", 글["content"])

print("삭제:", client.delete("/api/posts/3").status_code)
print("다시 조회:", client.get("/api/posts/3").json())

응답 = client.post("/api/posts", json={"title": "짧", "content": "짧아요",
                                        "author": "최", "category": "운동"})
print(응답.status_code, [오류["loc"][-1] for 오류 in 응답.json()["detail"]])
