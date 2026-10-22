# [2권 Chapter 8. 학습 잘 시키기 · 8.4 배치 정규화 · manuscript-vol2/chapters/08-training-well.md:468]
import torch
from torch import nn

torch.manual_seed(0)
# 4개 샘플 × 특성 2개. 두 특성의 크기(눈금)가 아주 다르다
x = torch.tensor([[1.0, 100.0],
                  [2.0, 300.0],
                  [3.0, 200.0],
                  [4.0, 400.0]])
bn = nn.BatchNorm1d(2)                        # 특성 2개짜리 배치 정규화
print("처음 running_mean:", bn.running_mean)

bn.train()
출력 = bn(x)
print("학습 모드 출력:")
print(출력.detach())
손으로 = (x - x.mean(dim=0)) / torch.sqrt(x.var(dim=0, unbiased=False) + bn.eps)
print("손으로 계산과 같은가?", torch.allclose(출력, 손으로, atol=1e-5))
print("한 번 본 뒤 running_mean:", bn.running_mean)

bn.eval()                                     # 평가 모드는 저장해 둔 평균·분산을 쓴다
print("평가 모드 출력(첫 줄):", bn(x[:1]).detach())

bn.train()
try:
    bn(x[:1])                                 # 학습 모드에 샘플 1개
except ValueError as e:
    print("오류:", e)
