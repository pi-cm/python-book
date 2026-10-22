# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.7 트랜스포머 블록 조립하기 · manuscript-vol2/chapters/12-transformer.md:744]
import math

import torch
from torch import nn


class 멀티헤드_어텐션(nn.Module):
    def __init__(self, 차원: int, 헤드_수: int) -> None:
        super().__init__()
        self.헤드_수 = 헤드_수
        self.qkv = nn.Linear(차원, 3 * 차원)
        self.출력 = nn.Linear(차원, 차원)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape
        q, k, v = (t.view(B, T, self.헤드_수, -1).transpose(1, 2) for t in self.qkv(x).split(C, dim=2))
        점수 = q @ k.transpose(-2, -1) / math.sqrt(k.size(-1))
        점수 = 점수.masked_fill(torch.ones(T, T, dtype=torch.bool).triu(1), float("-inf"))
        return self.출력((점수.softmax(dim=-1) @ v).transpose(1, 2).contiguous().view(B, T, C))


class 블록(nn.Module):
    def __init__(self, 차원: int, 헤드_수: int) -> None:
        super().__init__()
        self.정규화1 = nn.LayerNorm(차원)
        self.어텐션 = 멀티헤드_어텐션(차원, 헤드_수)
        self.정규화2 = nn.LayerNorm(차원)
        self.피드포워드 = nn.Sequential(nn.Linear(차원, 4 * 차원), nn.GELU(), nn.Linear(4 * 차원, 차원))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.어텐션(self.정규화1(x))        # 글자끼리 정보 주고받기
        x = x + self.피드포워드(self.정규화2(x))    # 글자마다 혼자 생각하기
        return x


C = 128
b = 블록(C, 헤드_수=4)
x = torch.randn(2, 10, C)
print("입력", tuple(x.shape), "→ 출력", tuple(b(x).shape))
for 이름, 부품 in b.named_children():
    print(f"  {이름}: {sum(p.numel() for p in 부품.parameters()):,}개")
print(f"합계: {sum(p.numel() for p in b.parameters()):,}개 (12 × C² = {12 * C * C:,})")

내장 = nn.TransformerEncoderLayer(C, nhead=4, dim_feedforward=4 * C, activation="gelu",
                                  batch_first=True, norm_first=True)
print(f"nn.TransformerEncoderLayer: {sum(p.numel() for p in 내장.parameters()):,}개")
