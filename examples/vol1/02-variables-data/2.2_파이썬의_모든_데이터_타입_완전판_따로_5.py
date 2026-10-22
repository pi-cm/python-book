"""1권 Chapter 2. 변수와 데이터 — 2.2 파이썬의 모든 데이터 타입 (완전판)

원고: manuscript/chapters/02-variables-data.md (298줄부터)
"""

# ---- 원고 298줄 ----
s = "Life is too short, You need Python"
print(s[0], s[-1])    # L n
print(s[0:4])         # Life  (0, 1, 2, 3번 글자)
print(s[19:])         # You need Python  (끝을 생략하면 마지막까지)
print(s[:17])         # Life is too short  (시작을 생략하면 처음부터)
print(s[19:-7])       # You need
print(s[999:])        # 빈 문자열: 슬라이싱은 범위를 넘어도 에러가 나지 않음
# print(s[999])       # IndexError: 인덱스 하나는 범위를 넘으면 에러

print("Py" + "thon", "하" * 3)   # Python 하하하
s[0] = "l"            # TypeError: 'str' object does not support item assignment
