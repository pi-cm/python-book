"""1권 레퍼런스 D. 특수 메서드 — 해시와 진릿값

원고: manuscript/references/D-special-methods.md (129줄부터)
"""

# ---- 원고 129줄 ----
class Won:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Won) and self.amount == other.amount

    def __hash__(self) -> int:                # 같으면 해시도 같아야 함
        return hash(self.amount)

    def __bool__(self) -> bool:               # if 문, bool()
        return self.amount != 0

print(len({Won(1000), Won(1000), Won(2000)}))   # 2
print(bool(Won(0)), bool(Won(500)))             # False True

class NoHash:
    def __eq__(self, other: object) -> bool:
        return True

print(NoHash.__hash__)                          # None (__eq__만 정의하면 해시가 꺼짐)
