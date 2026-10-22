# [2권 부록 B. 꼭 필요한 수학 직관 · B.5 확률과 소프트맥스 · manuscript-vol2/appendix/B-math-intuition.md:424]
import torch

점수 = torch.tensor([2.0, 1.0, 0.1])          # 로짓
지수 = torch.exp(점수)
확률 = 지수 / 지수.sum()
print("exp 씌우기:", 지수.round(decimals=4))
print("나눠서 합 1:", 확률.round(decimals=4), 확률.sum().item())
print("내장 함수  :", torch.softmax(점수, dim=0).round(decimals=4))
print("모두 +100 :", torch.softmax(점수 + 100, dim=0).round(decimals=4))
