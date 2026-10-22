# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.8 유명한 구조의 아이디어 · manuscript-vol2/chapters/09-cnn.md:1021]
import torch
import torch.nn.functional as F
from torch import nn
from torchvision import datasets

from 옷도구 import 장치_고르기


class 블록(nn.Module):
    """합성곱 두 번. 잔차=True면 입력을 더하고, 정규화=True면 합성곱마다 배치 정규화."""

    def __init__(self, c: int, 잔차: bool, 정규화: bool) -> None:
        super().__init__()
        self.잔차 = 잔차
        self.합성곱1 = nn.Conv2d(c, c, 3, padding=1)
        self.합성곱2 = nn.Conv2d(c, c, 3, padding=1)
        self.정규화1 = nn.BatchNorm2d(c) if 정규화 else nn.Identity()
        self.정규화2 = nn.BatchNorm2d(c) if 정규화 else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        출력 = self.정규화2(self.합성곱2(F.relu(self.정규화1(self.합성곱1(x)))))
        return F.relu(출력 + x) if self.잔차 else F.relu(출력)


def 깊은_CNN(블록수: int, 잔차: bool, 정규화: bool) -> nn.Sequential:
    return nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(),
                         *[블록(16, 잔차, 정규화) for _ in range(블록수)],
                         nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(16, 10))


# 빨리 보려고 학습 5,000장·시험 2,000장만, 사진은 14×14로 줄여서
장치 = 장치_고르기()
학습셋 = datasets.FashionMNIST("data", train=True, download=True)
시험셋 = datasets.FashionMNIST("data", train=False, download=True)
X = F.avg_pool2d(학습셋.data[:5000].float().unsqueeze(1) / 255, 2).to(장치)
y = 학습셋.targets[:5000].to(장치)
X_시험 = F.avg_pool2d(시험셋.data[:2000].float().unsqueeze(1) / 255, 2).to(장치)
y_시험 = 시험셋.targets[:2000].to(장치)

설정들 = [("평범한       ", False, False), ("평범한 + BN  ", False, True),
          ("잔차         ", True, False), ("잔차 + BN    ", True, True)]
for 이름, 잔차, 정규화 in 설정들:
    torch.manual_seed(0)
    모델 = 깊은_CNN(10, 잔차, 정규화).to(장치)   # 합성곱 21층
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.01, momentum=0.9)
    섞기 = torch.Generator().manual_seed(0)
    기록 = []
    for 에폭 in range(1, 6):
        모델.train()
        순서 = torch.randperm(len(X), generator=섞기).to(장치)
        손실들 = []
        for i in range(0, len(X), 64):
            묶음 = 순서[i:i + 64]
            옵티마이저.zero_grad()
            손실 = F.cross_entropy(모델(X[묶음]), y[묶음])
            손실.backward()
            옵티마이저.step()
            손실들.append(손실.item())
        모델.eval()
        with torch.no_grad():
            정확도 = (모델(X_시험).argmax(dim=1) == y_시험).float().mean().item()
        if 에폭 % 2 == 1:
            기록.append(f"{에폭}에폭 손실 {sum(손실들) / len(손실들):.3f}, 정확도 {정확도:5.1%}")
    print(이름, " / ".join(기록))
