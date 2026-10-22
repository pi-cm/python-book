import torch

# y = (3 * x + 1) ** 2 를 두 단계로: u = 3 * x + 1, y = u ** 2
x = torch.tensor(2.0, requires_grad=True)
u = 3 * x + 1
y = u ** 2
y.backward()

du_dx = 3                 # u는 x가 1 움직이면 3 움직인다
dy_du = 2 * u.item()      # y는 u가 1 움직이면 2 * u 움직인다
print("단계별 기울기의 곱:", dy_du * du_dx)
print("PyTorch가 구한 값 :", x.grad.item())
