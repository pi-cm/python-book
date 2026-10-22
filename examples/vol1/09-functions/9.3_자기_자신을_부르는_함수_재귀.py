"""1권 Chapter 9: 함수 — 9.3 자기 자신을 부르는 함수: 재귀

원고: manuscript/chapters/09-functions.md (262줄부터)
"""

# ---- 원고 262줄 ----
def factorial(n):
    if n == 1:                       # 종료 부분(base case)
        return 1
    return n * factorial(n - 1)      # 자기 호출 부분

def factorial_loop(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial(5))       # 120
print(factorial_loop(5))  # 120

# ---- 원고 299줄 ----
def hanoi(n, source, target, auxiliary):
    if n == 0:
        return
    hanoi(n - 1, source, auxiliary, target)   # 1. 위의 n-1개를 보조 기둥으로
    print(f"원반 {n}: {source} → {target}")    # 2. 가장 큰 원반을 목표 기둥으로
    hanoi(n - 1, auxiliary, target, source)   # 3. 보조 기둥의 n-1개를 목표 기둥으로

hanoi(3, "A", "C", "B")
