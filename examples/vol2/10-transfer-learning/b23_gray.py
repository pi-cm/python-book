# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.7 다른 모델, 다른 입력 · manuscript-vol2/chapters/10-transfer-learning.md:1052]
import torch
from torch import nn
from torchvision import models

모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT).eval()
print("conv1 가중치:", tuple(모델.conv1.weight.shape))      # (출력 64, 입력 3색, 7, 7)

torch.manual_seed(0)
흑백 = torch.randn(2, 1, 64, 64)                            # 흑백 사진 2장 (예제용 난수)

# 방법 1: 흑백 한 채널을 세 번 복사해 컬러처럼 넣는다
with torch.no_grad():
    출력1 = 모델(흑백.repeat(1, 3, 1, 1))

# 방법 2: 첫 층을 한 채널짜리로 바꾸고, 세 색의 가중치를 더해 넣는다
새_첫층 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
with torch.no_grad():
    새_첫층.weight.copy_(모델.conv1.weight.sum(dim=1, keepdim=True))   # (64, 3, 7, 7) → (64, 1, 7, 7)
모델.conv1 = 새_첫층
with torch.no_grad():
    출력2 = 모델(흑백)
print("conv1 가중치:", tuple(모델.conv1.weight.shape))
print("두 방법의 출력이 같은가:", torch.allclose(출력1, 출력2, atol=1e-4))
