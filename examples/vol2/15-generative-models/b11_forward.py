# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.8 확산 모델: 잡음을 걷어 내며 그리기 · manuscript-vol2/chapters/15-generative-models.md:775]
import torch

from 생성도구 import 격자_저장, 사진_불러오기
from 확산도구 import T, 베타, 알파, 알파_누적, 잡음_더하기

X, _ = 사진_불러오기(학습=False)
x0 = X[:1] * 2 - 1                              # 밝기 0~1 → -1~1 (잡음과 눈금을 맞춘다)

print("단계 t   원본 비율 √a   잡음 비율 √(1-a)   (a = 알파_누적[t])")
for t in [0, 50, 100, 200, 400, 700, 999]:
    a = 알파_누적[t]
    print(f"{t:6}   {a.sqrt():12.3f}   {(1 - a).sqrt():16.3f}")

# 같은 사진에 단계별로 잡음을 섞어 한 줄로 저장
torch.manual_seed(0)
단계들 = torch.tensor([0, 50, 100, 200, 300, 500, 700, 999])
섞인 = 잡음_더하기(x0.expand(8, -1, -1, -1), 단계들, torch.randn(8, 1, 28, 28))
격자_저장((섞인 + 1) / 2, "forward.png")

# 한 걸음씩 300번 섞은 것과 공식으로 한 번에 섞은 것은 같은 분포일까?
torch.manual_seed(0)
x = x0.expand(5000, -1, -1, -1).clone()          # 같은 사진 5,000장
for t in range(300):
    x = 알파[t].sqrt() * x + 베타[t].sqrt() * torch.randn_like(x)
a = 알파_누적[299]
print(f"한 걸음씩: 평균의 평균 오차 {(x.mean(0) - a.sqrt() * x0[0]).abs().mean():.4f}, "
      f"표준편차 {x.std(0).mean():.4f}")
print(f"공식     : 표준편차 √(1-a) = {(1 - a).sqrt():.4f}")
