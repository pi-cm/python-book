"""1권 레퍼런스 D. 특수 메서드 — 먼저 알아 둘 규칙

원고: manuscript/references/D-special-methods.md (13줄부터)
"""

# ---- 원고 13줄 ----
class Box:
    pass

b = Box()
b.__len__ = lambda: 5                         # 인스턴스에 붙이면
print(b.__len__())                            # 5 (직접 부르면 되지만)
try:
    len(b)                                    # len()은 타입(클래스)에서만 찾음
except TypeError as e:
    print("[X]", e)                           # [X] object of type 'Box' has no len()

Box.__len__ = lambda self: 5                  # 클래스에 붙여야 동작
print(len(b))                                 # 5
