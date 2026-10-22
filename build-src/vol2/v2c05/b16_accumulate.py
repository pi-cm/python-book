import torch

x = torch.tensor(3.0, requires_grad=True)
for 번째 in range(1, 4):
    y = x ** 2
    y.backward()
    print(f"{번째}번째 backward 뒤 x.grad = {x.grad.item()}")   # 6, 12, 18 ... 쌓인다

x.grad.zero_()                                  # 비우기
(x ** 2).backward()
print("비운 뒤 다시:", x.grad.item())
