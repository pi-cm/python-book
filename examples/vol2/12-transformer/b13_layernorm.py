# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.7 트랜스포머 블록 조립하기 · manuscript-vol2/chapters/12-transformer.md:676]
import torch
from torch import nn

torch.set_printoptions(precision=3)
# 문장 2개 × 글자 3개 × 숫자 4개. 둘째 문장의 마지막 글자는 채운 칸(0)이다
x = torch.tensor([[[1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0], [2.0, 2.0, 2.0, 6.0]],
                  [[0.5, 0.0, 0.5, 1.0], [3.0, 1.0, 4.0, 1.0], [0.0, 0.0, 0.0, 0.0]]])
층정규화 = nn.LayerNorm(4)                 # 글자 하나의 숫자 4개를 표준화한다
출력 = 층정규화(x)
print(출력[0].detach())

# 손으로: 글자마다(마지막 차원 방향으로) 평균과 분산을 낸다
평균 = x.mean(dim=-1, keepdim=True)
분산 = x.var(dim=-1, keepdim=True, unbiased=False)
print("손 계산과 같은가:", torch.allclose(출력, (x - 평균) / torch.sqrt(분산 + 층정규화.eps), atol=1e-5))
print("글자 1개만 넣어도 된다:", tuple(층정규화(x[:1, :1]).shape))
print("다른 글자와 섞이지 않는다:", torch.allclose(층정규화(x[:1, :1]), 출력[:1, :1]))
