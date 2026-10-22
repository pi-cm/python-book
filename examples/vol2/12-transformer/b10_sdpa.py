# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.5 멀티헤드 어텐션: 여러 관점으로 동시에 보기 · manuscript-vol2/chapters/12-transformer.md:504]
import math

import torch
from torch.nn import functional as F

torch.manual_seed(0)
B, H, T, D = 2, 4, 6, 8
q, k, v = torch.randn(B, H, T, D), torch.randn(B, H, T, D), torch.randn(B, H, T, D)

# 이 장에서 직접 쓴 계산
점수 = q @ k.transpose(-2, -1) / math.sqrt(D)
미래 = torch.ones(T, T, dtype=torch.bool).triu(1)
직접 = 점수.masked_fill(미래, float("-inf")).softmax(dim=-1) @ v

# PyTorch가 준비해 둔 한 줄짜리 함수
한줄 = F.scaled_dot_product_attention(q, k, v, is_causal=True)
print("모양:", tuple(한줄.shape), "같은가:", torch.allclose(직접, 한줄, atol=1e-6))

# 패딩 마스크도 받는다: True인 칸만 본다 (nn.MultiheadAttention과 뜻이 반대이니 주의)
보임 = torch.tensor([[True, True, True, True, False, False]])   # (1, T): 뒤의 두 칸은 채운 칸
직접2 = 점수.masked_fill(~보임, float("-inf")).softmax(dim=-1) @ v
한줄2 = F.scaled_dot_product_attention(q, k, v, attn_mask=보임)
print("패딩 마스크도 같은가:", torch.allclose(직접2, 한줄2, atol=1e-6))
