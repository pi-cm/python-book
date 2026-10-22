import torch

a = torch.tensor([1.0, 2.0, 3.0])
b = a.add(10)          # 새 텐서를 돌려준다
print(a, b)
a.add_(10)             # 밑줄: a 자신을 바꾼다
print(a)
