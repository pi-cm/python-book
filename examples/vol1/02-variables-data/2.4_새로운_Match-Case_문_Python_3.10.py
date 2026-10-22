"""1권 Chapter 2. 변수와 데이터 — 2.4 새로운 Match-Case 문 (Python 3.10+)

원고: manuscript/chapters/02-variables-data.md (651줄부터)
"""

# ---- 원고 651줄 ----
def 데이터_타입_분석(값):
    """Match-Case를 사용한 타입별 처리"""
    match 값:
        # 기본 타입 매칭 (bool은 int의 자식이므로 int보다 먼저 검사)
        case bool():
            return f"불린: {'참' if 값 else '거짓'}"
        case int() if 값 > 0:
            return f"양의 정수: {값}"
        case int() if 값 < 0:
            return f"음의 정수: {값}"
        case int():
            return "영"
        case float():
            return f"실수: {값:.2f}"
        case str() if len(값) == 0:
            return "빈 문자열"
        case str():
            return f"문자열: '{값}' (길이: {len(값)})"
        case list() | tuple() if len(값) == 0:
            return "빈 시퀀스"
        case [단일_요소]:
            return f"단일 요소 리스트: {단일_요소}"
        case [첫번째, *나머지]:
            return f"리스트 - 첫번째: {첫번째}, 나머지 {len(나머지)}개"
        case dict() if not 값:
            return "빈 딕셔너리"
        case {"이름": 이름, "나이": 나이}:
            return f"사람 정보: {이름} ({나이}세)"
        case {"타입": "원", "반지름": r}:
            import math
            return f"원의 넓이: {math.pi * r * r:.2f}"
        case None:
            return "None 값"
        case _:  # 와일드카드 (모든 경우)
            return f"알 수 없는 타입: {type(값).__name__}"

# Match-Case 테스트
테스트_값들 = [
    42, -7, 0, 3.14, "", "안녕하세요", True, False,
    [], [1], [1, 2, 3, 4, 5], {}, 
    {"이름": "김철수", "나이": 30},
    {"타입": "원", "반지름": 5},
    None, complex(1, 2)
]

for 값 in 테스트_값들:
    결과 = 데이터_타입_분석(값)
    print(f"{repr(값):>20} -> {결과}")
