# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.4 특징 추출: 눈은 빌리고 판단만 새로 · manuscript-vol2/chapters/10-transfer-learning.md:435]
import torch
from torch import nn
from torchvision import models

모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
for p in 모델.parameters():
    p.requires_grad_(False)                 # 몸통 전체를 얼린다(6장 6.4절)
모델.fc = nn.Linear(모델.fc.in_features, 10)  # 새로 만든 층은 얼어 있지 않다

전체 = sum(p.numel() for p in 모델.parameters())
학습_대상 = sum(p.numel() for p in 모델.parameters() if p.requires_grad)
print(f"전체 {전체:,}개 중 학습 대상 {학습_대상:,}개 ({학습_대상 / 전체:.3%})")
print("학습 대상 이름:", [이름 for 이름, p in 모델.named_parameters() if p.requires_grad])

# 가짜 배치로 한 번 거꾸로 계산해 보면 기울기가 어디에 생길까?
x = torch.randn(4, 3, 112, 112)
nn.functional.cross_entropy(모델(x), torch.tensor([0, 1, 2, 3])).backward()
print("conv1.weight.grad:", 모델.conv1.weight.grad)
print("fc.weight.grad 모양:", tuple(모델.fc.weight.grad.shape))

# 옵티마이저에는 학습 대상만 넘긴다
옵티마이저 = torch.optim.Adam(모델.fc.parameters(), lr=1e-3)
print("옵티마이저가 맡은 텐서 수:", len(옵티마이저.param_groups[0]["params"]))
