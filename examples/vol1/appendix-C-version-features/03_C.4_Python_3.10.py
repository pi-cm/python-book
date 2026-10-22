"""1권 부록 C. 버전별 새 기능 (3.8~3.14) — C.4 Python 3.10

원고: manuscript/appendix/C-version-features.md (108줄부터)
"""

# ---- 원고 108줄 ----
# Python 3.10 이상
def http_status(code: int | None) -> str:
    match code:
        case 200 | 201:
            return "성공"
        case 404:
            return "없음"
        case int(c) if 500 <= c < 600:
            return "서버 오류"
        case None:
            return "응답 없음"
        case _:
            return "기타"

print(http_status(201), http_status(503), http_status(None))  # 성공 서버 오류 응답 없음

import io
with (
    io.StringIO("첫째") as a,
    io.StringIO("둘째") as b,
):
    print(a.read(), b.read())     # 첫째 둘째

print(list(zip("ab", [1, 2], strict=True)))  # [('a', 1), ('b', 2)]
