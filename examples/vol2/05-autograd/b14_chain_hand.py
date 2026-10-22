# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.6 연쇄 법칙: 기울기가 거꾸로 흐르는 이유 · manuscript-vol2/chapters/05-autograd.md:576]
import torch

# y = (3x + 1)^2 를 두 단계로 나눠 보기: u = 3x + 1, y = u^2
x값 = 2.0
u값 = 3 * x값 + 1
du_dx = 3.0                 # u = 3x + 1 에서 x가 1 움직이면 u는 3 움직인다
dy_du = 2 * u값             # y = u^2 에서 u가 1 움직이면 y는 2u 움직인다
print(f"연쇄 법칙(손): dy/dx = {dy_du} × {du_dx} = {dy_du * du_dx}")

x = torch.tensor(x값, requires_grad=True)
y = (3 * x + 1) ** 2
y.backward()
print(f"PyTorch      : dy/dx = {x.grad.item()}")

h = 1e-4
f = lambda t: (3 * t + 1) ** 2
print(f"수치 미분    : dy/dx = {(f(x값 + h) - f(x값 - h)) / (2 * h):.4f}")
