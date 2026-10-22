# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.3 셀프 어텐션: 문장이 자기 자신을 본다 · manuscript-vol2/chapters/12-transformer.md:238]
import math

import torch
from torch import nn

torch.manual_seed(0)
차원 = 8
쿼리, 키, 값 = (nn.Linear(차원, 차원, bias=False) for _ in range(3))


def 셀프_어텐션(x: torch.Tensor) -> torch.Tensor:
    점수 = 쿼리(x) @ 키(x).transpose(-2, -1) / math.sqrt(차원)
    return 점수.softmax(dim=-1) @ 값(x)


x = torch.randn(1, 5, 차원)             # 글자 5개
순서 = torch.tensor([4, 2, 0, 3, 1])     # 글자 순서를 뒤섞는다
with torch.no_grad():
    원래 = 셀프_어텐션(x)
    섞은 = 셀프_어텐션(x[:, 순서])
print("섞은 입력의 출력 == 원래 출력을 같은 순서로 섞은 것:",
      torch.allclose(섞은, 원래[:, 순서], atol=1e-6))
print("0번 글자의 출력, 원래    :", 원래[0, 0, :4].round(decimals=4))
print("0번 글자의 출력, 섞은 뒤 :", 섞은[0, 2, :4].round(decimals=4))
