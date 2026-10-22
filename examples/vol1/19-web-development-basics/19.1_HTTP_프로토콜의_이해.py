"""1권 Chapter 19: 웹 개발 기초 — 19.1 HTTP 프로토콜의 이해

원고: manuscript/chapters/19-web-development-basics.md (77줄부터)
"""

# ---- 원고 77줄 ----
from http import HTTPStatus

# 이 장에서 자주 만날 상태 코드
for code in (200, 201, 204, 400, 401, 404, 422, 500):
    status = HTTPStatus(code)
    print(code, status.phrase)

print(HTTPStatus.NOT_FOUND == 404)
