# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.11 실습: FashionMNIST 옷 사진 분류기 · manuscript-vol2/chapters/06-nn-module.md:1330]
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


def 모델_만들기() -> nn.Module:
    """6.11절과 같은 구조의 다층 퍼셉트론."""
    return nn.Sequential(
        nn.Flatten(),
        nn.Linear(28 * 28, 256), nn.ReLU(),
        nn.Linear(256, 128), nn.ReLU(),
        nn.Linear(128, 10),
    )


def 학습하고_재기(옵티마이저_만들기, 에폭수: int = 2) -> float:
    """같은 씨앗에서 출발해 학습한 뒤 시험 정확도를 돌려준다."""
    torch.manual_seed(0)
    모델 = 모델_만들기()
    옵티마이저 = 옵티마이저_만들기(모델.parameters())
    손실함수 = nn.CrossEntropyLoss()
    for _ in range(에폭수):
        모델.train()
        for x, y in 학습_로더:
            옵티마이저.zero_grad()
            손실함수(모델(x), y).backward()
            옵티마이저.step()
    모델.eval()
    with torch.no_grad():
        예측 = 모델(X_시험).argmax(dim=1)
    return (예측 == y_시험).float().mean().item()


학습셋 = datasets.FashionMNIST("data", train=True, download=True, transform=transforms.ToTensor())
시험셋 = datasets.FashionMNIST("data", train=False, download=True)
학습_로더 = DataLoader(학습셋, batch_size=64, shuffle=True)
X_시험 = 시험셋.data.float().unsqueeze(1) / 255
y_시험 = 시험셋.targets

후보 = {
    "SGD lr=0.01          ": lambda p: torch.optim.SGD(p, lr=0.01),
    "SGD+momentum lr=0.01 ": lambda p: torch.optim.SGD(p, lr=0.01, momentum=0.9),
    "Adam lr=0.001        ": lambda p: torch.optim.Adam(p, lr=0.001),
    "Adam lr=0.1          ": lambda p: torch.optim.Adam(p, lr=0.1),
}
for 이름, 만들기 in 후보.items():
    print(f"{이름} 2에폭 뒤 시험 정확도 {학습하고_재기(만들기):.2%}")
