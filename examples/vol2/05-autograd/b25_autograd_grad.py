# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.12 torch.autograd.grad: 기울기를 직접 받기 · manuscript-vol2/chapters/05-autograd.md:1082]
import torch

x = torch.tensor(3.0, requires_grad=True)
y = x ** 3

# backward()와 달리 x.grad에 쌓지 않고, 기울기를 결과로 돌려준다
(dy_dx,) = torch.autograd.grad(y, x, create_graph=True)   # 기울기 계산도 기록해 둔다
print("1번 미분 3x^2 :", dy_dx)          # 3 × 9 = 27
(d2y_dx2,) = torch.autograd.grad(dy_dx, x)                # 기울기의 기울기
print("2번 미분 6x   :", d2y_dx2)        # 6 × 3 = 18
print("x.grad        :", x.grad)                          # 건드리지 않았다

# 여러 텐서에 대한 기울기를 한꺼번에
w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(1.0, requires_grad=True)
손실 = (w * 3.0 + b - 10.0) ** 2
기울기_w, 기울기_b = torch.autograd.grad(손실, [w, b])
print("손실의 w, b 기울기:", 기울기_w.item(), 기울기_b.item())
