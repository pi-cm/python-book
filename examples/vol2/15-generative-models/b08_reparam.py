# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.6 VAE: 점 대신 구름으로 · manuscript-vol2/chapters/15-generative-models.md:531]
import torch
from torch.distributions import Normal, kl_divergence

평균 = torch.tensor([0.5, -1.0], requires_grad=True)
로그분산 = torch.tensor([0.0, -2.0], requires_grad=True)
표준편차 = torch.exp(0.5 * 로그분산)              # 로그분산 → 표준편차
분포 = Normal(평균, 표준편차)

# 1) 그냥 뽑기: 뽑힌 값은 계산 기록이 없는 '상수'다
torch.manual_seed(1)
z = 분포.sample()
print("sample()  :", z, "| grad_fn:", z.grad_fn)

# 2) 재매개변수화: 무작위는 잡음에 맡기고, z는 평균과 표준편차로 '계산'한다
torch.manual_seed(0)
잡음 = torch.randn(2)
z = 평균 + 표준편차 * 잡음
print("직접 계산 :", z.detach(), "| grad_fn:", type(z.grad_fn).__name__)
torch.manual_seed(0)
print("rsample() :", 분포.rsample().detach())     # 같은 씨앗이면 같은 값

z.sum().backward()
print("평균의 기울기:", 평균.grad)
print("로그분산의 기울기:", 로그분산.grad)

# KL 발산: N(평균, 표준편차²)가 표준정규분포 N(0, 1)에서 얼마나 떨어졌나
kl_공식 = -0.5 * (1 + 로그분산 - 평균 ** 2 - 로그분산.exp())
print("KL (공식)             :", kl_공식.detach())
print("KL (torch.distributions):", kl_divergence(분포, Normal(0.0, 1.0)).detach())
