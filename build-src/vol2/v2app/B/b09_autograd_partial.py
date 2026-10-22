import torch

# 변수가 둘인 함수: 손실 = (w * 2 + b - 7) ** 2
w = torch.tensor(1.0, requires_grad=True)
b = torch.tensor(0.5, requires_grad=True)
손실 = (w * 2 + b - 7) ** 2
손실.backward()
print("손실:", 손실.item())
print("w 방향 기울기:", w.grad.item(), " b 방향 기울기:", b.grad.item())

# 경사하강법 한 걸음: 기울기의 반대쪽으로 조금
학습률 = 0.05
with torch.no_grad():
    w -= 학습률 * w.grad
    b -= 학습률 * b.grad
print("한 걸음 뒤 손실:", ((w * 2 + b - 7) ** 2).item())
