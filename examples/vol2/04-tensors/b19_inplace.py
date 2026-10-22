# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.7 제자리 연산과 메모리 · manuscript-vol2/chapters/04-tensors.md:992]
import torch

a = torch.tensor([1.0, 2.0, 3.0])
b = a.add(10)          # 새 텐서를 돌려준다
print(a, b)
a.add_(10)             # 밑줄: a 자신을 바꾼다
print(a)
