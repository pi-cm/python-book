# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.2 손으로 해 보는 경사하강법 · manuscript-vol2/chapters/05-autograd.md:229]
def f(x: float) -> float:
    return x ** 4 - 3 * x ** 2 + x   # 골짜기가 두 개인 함수


def 수치_미분(함수, x: float, h: float = 1e-5) -> float:
    return (함수(x + h) - 함수(x - h)) / (2 * h)


for 출발 in [2.0, -0.5, -2.0]:
    x = 출발
    for _ in range(200):
        x = x - 0.01 * 수치_미분(f, x)   # 공식 없이, 잰 기울기만으로 내려가기
    print(f"출발 {출발:4}: 도착 x = {x:7.4f}, f(x) = {f(x):8.4f}")
