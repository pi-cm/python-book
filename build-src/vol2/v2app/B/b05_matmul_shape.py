import torch

A = torch.ones(2, 3)
B = torch.ones(3, 4)
print("(2, 3) @ (3, 4) ->", tuple((A @ B).shape))

try:
    A @ torch.ones(2, 4)
except RuntimeError as 오류:
    print("오류:", 오류)

# 맨 앞 차원은 배치로 보고 따로따로 곱한다
배치 = torch.ones(8, 2, 3)
print("(8, 2, 3) @ (3, 4) ->", tuple((배치 @ B).shape))
