# [1권 Chapter 19: 웹 개발 기초 · 19.2 FastAPI 프레임워크 기초 · manuscript/chapters/19-web-development-basics.md:124]
# main.py - 첫 번째 FastAPI 애플리케이션
from fastapi import FastAPI

app = FastAPI(title="한국 도시 정보 API")

# 한국 도시 데이터 (실제로는 데이터베이스에서 가져올 것)
한국_도시들 = [
    {"id": 1, "이름": "서울", "지역": "수도권"},
    {"id": 2, "이름": "부산", "지역": "영남권"},
    {"id": 3, "이름": "인천", "지역": "수도권"},
    {"id": 4, "이름": "대구", "지역": "영남권"},
]


@app.get("/")
def 홈():
    return {"메시지": "한국 도시 정보 API에 오신 것을 환영합니다"}


@app.get("/cities")
async def 도시_목록():
    return {"데이터": 한국_도시들, "총개수": len(한국_도시들)}
