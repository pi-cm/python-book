# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.3 셀프 어텐션: 문장이 자기 자신을 본다 · manuscript-vol2/chapters/12-transformer.md:183]
import math

import torch
from torch import nn


class 셀프_어텐션(nn.Module):
    """같은 입력에서 쿼리·키·값을 따로 만들어, 글자마다 다른 글자들을 섞어 본다."""

    def __init__(self, 차원: int) -> None:
        super().__init__()
        self.쿼리 = nn.Linear(차원, 차원, bias=False)   # "나는 무엇을 찾나"
        self.키 = nn.Linear(차원, 차원, bias=False)     # "나는 이런 정보를 가졌다"
        self.값 = nn.Linear(차원, 차원, bias=False)     # "나를 고르면 이걸 준다"

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        q, k, v = self.쿼리(x), self.키(x), self.값(x)               # 모두 (B, T, C)
        점수 = q @ k.transpose(-2, -1) / math.sqrt(x.size(-1))      # (B, T, T)
        가중치 = 점수.softmax(dim=-1)
        return 가중치 @ v, 가중치


torch.manual_seed(0)
torch.set_printoptions(precision=2)          # 텐서를 소수점 둘째 자리까지만 보여 주기
x = torch.randn(1, 5, 8)            # 문장 1개 × 글자 5개 × 글자마다 숫자 8개
층 = 셀프_어텐션(8)
출력, 가중치 = 층(x)
print("입력", tuple(x.shape), "→ 출력", tuple(출력.shape), "/ 가중치", tuple(가중치.shape))
print(가중치[0].detach())
print("파라미터 수:", sum(p.numel() for p in 층.parameters()))
