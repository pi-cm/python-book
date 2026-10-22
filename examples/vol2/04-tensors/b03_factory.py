# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.1 텐서 만들기 · manuscript-vol2/chapters/04-tensors.md:91]
import torch

print(torch.zeros(2, 3))          # 0으로 채운 2행 3열
print(torch.ones(2, 3))           # 1로 채운 2행 3열
print(torch.full((2, 3), 7.0))    # 원하는 값으로 채우기
print(torch.arange(0, 10, 2))     # range처럼: 0부터 10 전까지 2씩
print(torch.linspace(0, 1, 5))    # 0부터 1까지 똑같은 간격으로 5개
print(torch.eye(3))               # 대각선만 1인 단위 행렬
