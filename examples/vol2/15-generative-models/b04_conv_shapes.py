# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.3 합성곱 오토인코더로 잡음 지우기 · manuscript-vol2/chapters/15-generative-models.md:316]
import torch
from torch import nn

x = torch.zeros(1, 1, 28, 28)                       # 사진 한 장 (장 수, 채널, 세로, 가로)

줄이기 = nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1)
키우기 = nn.ConvTranspose2d(16, 1, kernel_size=4, stride=2, padding=1)

작아진 = 줄이기(x)
print("Conv2d(stride=2)         :", tuple(x.shape), "→", tuple(작아진.shape))
print("ConvTranspose2d(stride=2):", tuple(작아진.shape), "→", tuple(키우기(작아진).shape))

# 출력 크기 공식: (입력 - 1) × stride - 2 × padding + kernel_size
print("공식으로 계산:", (14 - 1) * 2 - 2 * 1 + 4)
