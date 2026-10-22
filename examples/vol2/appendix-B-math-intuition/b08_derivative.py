# [2권 부록 B. 꼭 필요한 수학 직관 · B.3 미분과 기울기 · manuscript-vol2/appendix/B-math-intuition.md:239]
def f(x: float) -> float:
    return x ** 2

# 기울기 = 높이 변화 / 움직인 거리. 움직이는 거리를 점점 줄여 본다
x = 3.0
for h in [1.0, 0.1, 0.01, 0.001]:
    print(f"h={h:<6} 기울기 ≈ {(f(x + h) - f(x)) / h:.4f}")
print("x ** 2의 기울기 공식 2 * x =", 2 * x)
