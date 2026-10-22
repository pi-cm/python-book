"""1권 레퍼런스 A. 내장 함수 — 클래스를 꾸미는 데코레이터

원고: manuscript/references/A-builtin-functions.md (119줄부터)
"""

# ---- 원고 119줄 ----
class Circle:
    PI = 3.14

    def __init__(self, r):
        self.r = r

    @classmethod
    def unit(cls):            # cls == Circle, 대체 생성자
        return cls(1)

    @staticmethod
    def is_valid(r):          # self도 cls도 없다, 그냥 함수
        return r > 0

    @property
    def area(self):           # 괄호 없이 c.area로 읽는다
        return self.PI * self.r ** 2

c = Circle.unit()
print(c.r, Circle.is_valid(-1), c.area)   # 1 False 3.14
