"""1권 레퍼런스 D. 특수 메서드 — 컨테이너와 반복

원고: manuscript/references/D-special-methods.md (296줄부터)
"""

# ---- 원고 296줄 ----
class Wallet:
    def __init__(self) -> None:
        self._bills: list[int] = []

    def __len__(self) -> int:                 # len()
        return len(self._bills)

    def __getitem__(self, i: int) -> int:     # w[i], 슬라이스, for의 마지막 수단
        return self._bills[i]

    def __setitem__(self, i: int, value: int) -> None:
        self._bills[i] = value

    def __delitem__(self, i: int) -> None:
        del self._bills[i]

    def __iter__(self):                       # for, list()
        return iter(self._bills)

    def __reversed__(self):                   # reversed()
        return reversed(self._bills)

    def __contains__(self, bill: int) -> bool:  # in
        return bill in self._bills

w = Wallet()
w._bills += [1000, 5000, 10000, 50000]
w[0] = 50000
del w[1]
print(len(w), w[0], w[-1], 10000 in w, list(reversed(w)))
# 3 50000 50000 True [50000, 10000, 50000]

class Prices(dict):
    def __missing__(self, key: str) -> int:   # dict 하위 클래스에서 없는 키
        return 0

print(Prices(아메리카노=4500)["라테"])   # 0
