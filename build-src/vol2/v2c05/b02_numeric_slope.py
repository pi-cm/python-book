def f(x: float) -> float:
    return x ** 2


x = 3.0
for h in [1.0, 0.1, 0.01, 0.001, 0.0001]:
    기울기 = (f(x + h) - f(x)) / h       # 조금(h) 움직였을 때 변한 양 ÷ 움직인 거리
    print(f"h={h:<7} 기울기 ≈ {기울기:.6f}")

print()
for h in [1e-8, 1e-10, 1e-12, 1e-14]:
    print(f"h={h:<7} 기울기 ≈ {(f(x + h) - f(x)) / h:.6f}")   # 너무 작게 움직이면?
