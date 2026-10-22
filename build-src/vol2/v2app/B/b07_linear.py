import torch
from torch import nn

torch.manual_seed(0)
층 = nn.Linear(3, 2)                      # 입력 3칸 -> 출력 2칸
x = torch.randn(5, 3)                     # 샘플 5개

print("가중치 모양:", tuple(층.weight.shape), " 편향 모양:", tuple(층.bias.shape))
직접 = x @ 층.weight.T + 층.bias           # 입력 @ 가중치(전치) + 편향
print("같은가:", torch.allclose(층(x), 직접))
print("파라미터 수:", sum(p.numel() for p in 층.parameters()), "= 3 x 2 + 2")
