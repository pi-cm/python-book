"""1권 레퍼런스 A. 내장 함수 — 객체, 타입, 속성

원고: manuscript/references/A-builtin-functions.md (97줄부터)
"""

# ---- 원고 97줄 ----
class A:
    def hi(self):
        return 'A'

class B(A):
    def hi(self):
        return 'B+' + super().hi()   # 부모 A의 hi()를 부른다

print(B().hi())   # B+A
