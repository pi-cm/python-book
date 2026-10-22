import torch

x = torch.tensor(3.0, requires_grad=True)   # "이 값에 대한 기울기가 필요해요" 표시
y = x ** 2                                   # 평소처럼 계산
print(y)

y.backward()                                 # y를 x로 미분해 줘
print("PyTorch가 구한 기울기:", x.grad)
print("손으로 구한 기울기 2x:", 2 * 3.0)

h = 1e-3
print("수치 미분:", ((3.0 + h) ** 2 - (3.0 - h) ** 2) / (2 * h))
