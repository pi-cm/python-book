# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.1 기울기: 조금 움직였을 때 얼마나 변하나 · manuscript-vol2/chapters/05-autograd.md:106]
def f(x: float) -> float:
    return x ** 2


def 수치_미분(함수, x: float, h: float = 1e-5) -> float:
    """x 양쪽으로 h만큼 움직여 본 높이 차이로 기울기를 잰다(중앙 차분)."""
    return (함수(x + h) - 함수(x - h)) / (2 * h)


print(f"한쪽만 움직이기 (h=0.01): {(f(3.0 + 0.01) - f(3.0)) / 0.01:.6f}")
print(f"양쪽 움직이기   (h=0.01): {수치_미분(f, 3.0, h=0.01):.6f}")
print()
for x in [-2.0, 0.0, 1.0, 3.0, 5.0]:
    print(f"x={x:4}: 잰 기울기 {수치_미분(f, x):8.4f}, 공식 2x = {2 * x:5.1f}")
