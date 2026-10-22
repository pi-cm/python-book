"""1권 레퍼런스 D. 특수 메서드 — 숫자: 단항 연산과 변환

원고: manuscript/references/D-special-methods.md (376줄부터)
"""

# ---- 원고 376줄 ----
class Won:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __add__(self, other: "Won") -> "Won":     # won + won
        if not isinstance(other, Won):
            return NotImplemented
        return Won(self.amount + other.amount)

    def __mul__(self, n: int) -> "Won":           # won * 3
        if not isinstance(n, int):
            return NotImplemented
        return Won(self.amount * n)

    __rmul__ = __mul__                            # 3 * won (왼쪽이 int라 반사 메서드)

    def __radd__(self, other: int) -> "Won":      # sum()은 0 + won부터 시작
        return self if other == 0 else NotImplemented

    def __iadd__(self, other: "Won") -> "Won":    # won += won (제자리)
        self.amount += other.amount
        return self

    def __neg__(self) -> "Won":
        return Won(-self.amount)

    def __index__(self) -> int:                   # hex(), 인덱스, int()의 대안
        return self.amount

    def __repr__(self) -> str:
        return f"Won({self.amount})"

a = Won(1000)
print(a + Won(500), 3 * a, a * 2, -a, sum([Won(100), Won(200)]))
# Won(1500) Won(3000) Won(2000) Won(-1000) Won(300)
a += Won(1)
print(a, hex(Won(255)), int(Won(7)), [10, 20, 30][Won(1)])
# Won(1001) 0xff 7 20
