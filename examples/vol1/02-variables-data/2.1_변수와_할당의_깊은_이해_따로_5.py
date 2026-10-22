"""1권 Chapter 2. 변수와 데이터 — 2.1 변수와 할당의 깊은 이해

원고: manuscript/chapters/02-variables-data.md (115줄부터)
"""

# ---- 원고 115줄 ----
total = sum([1, 2, 3, 4])   # 10, 내장 함수 sum으로 합계를 구함
sum = 10                    # 그런데 sum이라는 이름에 값을 넣어 버리면
sum([1, 2])                 # TypeError: 'int' object is not callable
