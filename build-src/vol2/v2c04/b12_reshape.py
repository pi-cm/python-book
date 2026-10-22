import torch

x = torch.arange(12)
print(x.reshape(3, 4))
print(x.reshape(2, -1))       # -1: 나머지는 알아서 계산
print(x.reshape(2, 2, 3).shape)

try:
    x.reshape(5, -1)
except RuntimeError as e:
    print("오류:", e)
