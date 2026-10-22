"""1권 레퍼런스 D. 특수 메서드 — 파이썬 3에서 쓰지 않는 이름

원고: manuscript/references/D-special-methods.md (536줄부터)
"""

# ---- 원고 536줄 ----
class OldWon:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __nonzero__(self) -> bool:            # 파이썬 2의 진릿값 메서드
        return self.amount != 0

    def __div__(self, n: int) -> "OldWon":    # 파이썬 2의 / 메서드
        return OldWon(self.amount // n)

zero = OldWon(0)
print(bool(zero))                             # True (__nonzero__는 무시되고 기본값)
try:
    zero / 2
except TypeError as e:
    print("[X]", e)   # [X] unsupported operand type(s) for /: 'OldWon' and 'int'
