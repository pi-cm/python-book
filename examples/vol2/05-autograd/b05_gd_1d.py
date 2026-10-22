# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.2 손으로 해 보는 경사하강법 · manuscript-vol2/chapters/05-autograd.md:194]
def f(x: float) -> float:
    return (x - 3) ** 2 + 1          # x=3일 때 가장 낮은 1


def 기울기(x: float) -> float:
    return 2 * (x - 3)               # f를 미분한 공식


x = -2.0                             # 아무 데서나 출발
학습률 = 0.1                          # 한 번에 얼마나 크게 걸을지
for 걸음 in range(1, 31):
    x = x - 학습률 * 기울기(x)        # 경사하강법의 전부: 기울기 반대로 조금 이동
    if 걸음 in (1, 2, 3, 5, 10, 20, 30):
        print(f"{걸음:2}걸음: x = {x:.4f}, f(x) = {f(x):.6f}")
