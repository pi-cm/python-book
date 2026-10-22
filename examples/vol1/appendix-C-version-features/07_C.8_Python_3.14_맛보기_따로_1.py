"""1권 부록 C. 버전별 새 기능 (3.8~3.14) — C.8 Python 3.14 (맛보기)

원고: manuscript/appendix/C-version-features.md (337줄부터)
"""

# ---- 원고 337줄 ----
# Python 3.14 이상
name = "민수"
t = t"안녕, {name}!"
print(type(t).__name__, t.strings, t.values)   # Template ('안녕, ', '!') ('민수',)

try:
    int("x")
except ValueError, TypeError:
    print("둘 중 하나를 잡음")                   # 둘 중 하나를 잡음

class Node:
    def link(self, other: Node) -> Node:       # 3.13까지는 NameError
        return other
print("정의 OK")                                # 정의 OK
