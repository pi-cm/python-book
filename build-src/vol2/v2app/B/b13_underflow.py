import math

import torch

# 확률 0.01을 200번 곱하면? (토큰 200개짜리 문장의 확률을 생각해 보자)
p = torch.full((200,), 0.01)
print("그냥 곱하기 (float32):", torch.prod(p).item())
print("로그를 더하기        :", torch.log(p).sum().item())
print("손으로 200 * log(0.01):", 200 * math.log(0.01))
