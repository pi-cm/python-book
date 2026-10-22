# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.5 멀티헤드 어텐션: 여러 관점으로 동시에 보기 · manuscript-vol2/chapters/12-transformer.md:434]
import math

import torch
from torch import nn


class 멀티헤드_어텐션(nn.Module):
    def __init__(self, 차원: int, 헤드_수: int) -> None:
        super().__init__()
        self.헤드_수 = 헤드_수
        self.qkv = nn.Linear(차원, 3 * 차원)        # 쿼리·키·값을 한 번에 만든다
        self.출력 = nn.Linear(차원, 차원)            # 헤드들의 결과를 섞는다

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)                      # 각각 (B, T, C)
        q, k, v = (t.view(B, T, self.헤드_수, -1).transpose(1, 2) for t in (q, k, v))
        점수 = torch.einsum("bhqd,bhkd->bhqk", q, k) / math.sqrt(k.size(-1))   # (B, H, T, T)
        미래 = torch.ones(T, T, dtype=torch.bool).triu(1)          # 대각선 위 = 앞으로 올 글자
        가중치 = 점수.masked_fill(미래, float("-inf")).softmax(dim=-1)
        y = (가중치 @ v).transpose(1, 2).contiguous().view(B, T, C)
        return self.출력(y), 가중치


torch.manual_seed(0)
x = torch.randn(2, 6, 16)                      # 문장 2개 × 글자 6개 × 숫자 16개
우리 = 멀티헤드_어텐션(16, 헤드_수=4)
출력, 가중치 = 우리(x)
print("출력", tuple(출력.shape), "가중치", tuple(가중치.shape))
print("파라미터 수:", sum(p.numel() for p in 우리.parameters()))

# PyTorch의 nn.MultiheadAttention에 같은 가중치를 넣고 결과를 비교한다
파이토치 = nn.MultiheadAttention(16, num_heads=4, batch_first=True)
with torch.no_grad():
    파이토치.in_proj_weight.copy_(우리.qkv.weight)      # (3C, C): 쿼리·키·값 순서로 쌓여 있다
    파이토치.in_proj_bias.copy_(우리.qkv.bias)
    파이토치.out_proj.weight.copy_(우리.출력.weight)
    파이토치.out_proj.bias.copy_(우리.출력.bias)
미래 = torch.ones(6, 6, dtype=torch.bool).triu(1)        # True = 보지 마
그쪽_출력, 그쪽_가중치 = 파이토치(x, x, x, attn_mask=미래, average_attn_weights=False)
print("파라미터 수:", sum(p.numel() for p in 파이토치.parameters()))
print("출력이 같은가:", torch.allclose(출력, 그쪽_출력, atol=1e-6))
print("가중치가 같은가:", torch.allclose(가중치, 그쪽_가중치, atol=1e-6))
