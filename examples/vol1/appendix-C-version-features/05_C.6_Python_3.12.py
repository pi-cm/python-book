"""1권 부록 C. 버전별 새 기능 (3.8~3.14) — C.6 Python 3.12

원고: manuscript/appendix/C-version-features.md (222줄부터)
"""

# ---- 원고 222줄 ----
# Python 3.12 이상
songs = ["봄", "여름"]
info = {"title": "계절"}
print(f"{info["title"]}: {", ".join(songs)}")  # 계절: 봄, 여름
print(f"{"\n".join(songs)!r}")                 # '봄\n여름'

type Point = tuple[float, float]
type Pair[T] = tuple[T, T]
print(Point.__value__)            # tuple[float, float]

def first[T](items: list[T]) -> T:
    return items[0]

class Box[T]:
    def __init__(self, value: T):
        self.value = value

print(first([10, 20]), Box("상자").value)  # 10 상자

from itertools import batched
print(list(batched("abcde", 2)))  # [('a', 'b'), ('c', 'd'), ('e',)]
