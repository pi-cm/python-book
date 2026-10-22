"""1권 부록 B. 한눈에 보는 파이썬 — B.9 고급 자료 구조 (8장)

원고: manuscript/appendix/B-cheatsheet.md (373줄부터)
"""

# ---- 원고 373줄 ----
from collections import Counter, defaultdict, deque, namedtuple
from dataclasses import dataclass, field
from enum import Enum

print(Counter("hello").most_common(2))   # [('l', 2), ('h', 1)]

groups = defaultdict(list)
for word in ["apple", "avocado", "banana"]:
    groups[word[0]].append(word)
print(dict(groups))                      # {'a': ['apple', 'avocado'], 'b': ['banana']}

q = deque([1, 2, 3], maxlen=3)
q.append(4)                              # 꽉 차서 반대쪽 1이 밀려남
print(q)                                 # deque([2, 3, 4], maxlen=3)
print(q.popleft(), q)                    # 2 deque([3, 4], maxlen=3)

Point = namedtuple("Point", "x y")
print(Point(1, 2).x)                     # 1

@dataclass
class Item:
    name: str
    price: int = 0
    tags: list[str] = field(default_factory=list)

print(Item("펜", 1000))                   # Item(name='펜', price=1000, tags=[])

class Color(Enum):
    RED = 1
    GREEN = 2
print(Color.RED, Color(2).name)          # Color.RED GREEN
