"""1권 레퍼런스 D. 특수 메서드 — 문자열 표현

원고: manuscript/references/D-special-methods.md (64줄부터)
"""

# ---- 원고 64줄 ----
class Won:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __repr__(self) -> str:                # 개발자용: repr(), 대화형 창
        return f"Won({self.amount})"

    def __str__(self) -> str:                 # 사용자용: print(), str()
        return f"{self.amount:,}원"

    def __format__(self, spec: str) -> str:   # format(), f-문자열의 :spec
        if spec == "만":
            return f"{self.amount / 10000:g}만 원"
        return format(self.amount, spec)

w = Won(35000)
print(repr(w), str(w))       # Won(35000) 35,000원
print(f"{w:만} / {w:>8,}")   # 3.5만 원 /   35,000
