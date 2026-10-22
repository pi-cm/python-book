"""1권 부록 B. 한눈에 보는 파이썬 — B.13 예외 처리 (12장)

원고: manuscript/appendix/B-cheatsheet.md (617줄부터)
"""

# ---- 원고 617줄 ----
def to_int(text):
    try:
        n = int(text)
    except ValueError as e:
        print("변환 실패:", e)
        return None
    else:                         # 예외가 없을 때만
        return n
    finally:                      # 무슨 일이 있어도 마지막에
        print("검사 끝")

print(to_int("42"))
print(to_int("4.2"))

# ---- 원고 652줄 ----
class InsufficientFunds(Exception):
    def __init__(self, need):
        super().__init__(f"{need}원이 부족합니다")
        self.need = need

try:
    raise InsufficientFunds(500)
except InsufficientFunds as e:
    print(e, e.need)    # 500원이 부족합니다 500
