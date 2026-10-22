"""1권 부록 B. 한눈에 보는 파이썬 — B.6 반복문 (5장)

원고: manuscript/appendix/B-cheatsheet.md (244줄부터)
"""

# ---- 원고 244줄 ----
print(list(range(3)), list(range(2, 8, 2)))  # [0, 1, 2] [2, 4, 6]
print(list(range(10, 0, -3)))                 # [10, 7, 4, 1]

fruits = ["사과", "배"]
for i, f in enumerate(fruits, start=1):
    print(i, f)                      # 1 사과 / 2 배
for name, price in zip(["사과", "배"], [1000, 2000]):
    print(name, price)               # 사과 1000 / 배 2000

# ---- 원고 266줄 ----
for n in [3, 5, 7]:
    if n % 2 == 0:
        print("짝수 발견")
        break
else:
    print("짝수 없음")     # 짝수 없음

count = 0
while True:
    count += 1
    if count == 3:
        break
print(count)               # 3
