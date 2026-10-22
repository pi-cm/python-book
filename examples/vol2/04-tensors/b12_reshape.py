# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.5 모양 바꾸기 · manuscript-vol2/chapters/04-tensors.md:598]
import torch

x = torch.arange(12)
print(x.reshape(3, 4))
print(x.reshape(2, -1))       # -1: 나머지는 알아서 계산
print(x.reshape(2, 2, 3).shape)

try:
    x.reshape(5, -1)
except RuntimeError as e:
    print("오류:", e)
