"""1권 레퍼런스 D. 특수 메서드 — 비교

원고: manuscript/references/D-special-methods.md (98줄부터)
"""

# ---- 원고 98줄 ----
from functools import total_ordering

@total_ordering                               # __eq__와 __lt__만 있으면 나머지를 채워 줌
class Won:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Won):
            return NotImplemented             # 모르는 타입이면 상대에게 넘김
        return self.amount == other.amount

    def __lt__(self, other: "Won") -> bool:
        if not isinstance(other, Won):
            return NotImplemented
        return self.amount < other.amount

print(Won(1000) < Won(2000), Won(3000) >= Won(2000), Won(1000) == 1000)   # True True False
print(max(Won(1000), Won(5000), Won(3000)).amount)                        # 5000
