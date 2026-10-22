# [1권 Chapter 19: 웹 개발 기초 · 19.2 FastAPI 프레임워크 기초 · manuscript/chapters/19-web-development-basics.md:175]
# try_main.py - 서버를 띄우지 않고 main.py의 API 호출하기
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

응답 = client.get("/")
print(응답.status_code, 응답.json())
print(응답.headers["content-type"])

응답 = client.get("/cities")
print(응답.json()["총개수"], 응답.json()["데이터"][0])

응답 = client.get("/없는-주소")
print(응답.status_code, 응답.json())
