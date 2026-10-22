# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.11 실습: FashionMNIST 옷 사진 분류기 · manuscript-vol2/chapters/06-nn-module.md:1143]
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


class 의류분류기(nn.Module):
    """28×28 흑백 사진을 받아 옷 종류 10가지의 점수를 내는 다층 퍼셉트론."""

    def __init__(self) -> None:
        super().__init__()
        self.펴기 = nn.Flatten()
        self.층들 = nn.Sequential(
            nn.Linear(28 * 28, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, 10),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.층들(self.펴기(x))


def 한_에폭_학습(모델: nn.Module, 로더: DataLoader, 손실함수: nn.Module,
                옵티마이저: torch.optim.Optimizer, 장치: torch.device) -> float:
    """학습 데이터를 한 바퀴 돌며 학습하고 평균 손실을 돌려준다."""
    모델.train()
    손실_합, 개수 = 0.0, 0
    for x, y in 로더:
        x, y = x.to(장치), y.to(장치)
        옵티마이저.zero_grad()
        손실 = 손실함수(모델(x), y)
        손실.backward()
        옵티마이저.step()
        손실_합 += 손실.item() * len(y)
        개수 += len(y)
    return 손실_합 / 개수


def 평가하기(모델: nn.Module, 로더: DataLoader, 손실함수: nn.Module,
            장치: torch.device) -> tuple[float, float]:
    """평균 손실과 정확도를 잰다. 모델은 고치지 않는다."""
    모델.eval()
    손실_합, 맞힘, 개수 = 0.0, 0, 0
    with torch.no_grad():
        for x, y in 로더:
            x, y = x.to(장치), y.to(장치)
            출력 = 모델(x)
            손실_합 += 손실함수(출력, y).item() * len(y)
            맞힘 += (출력.argmax(dim=1) == y).sum().item()
            개수 += len(y)
    return 손실_합 / 개수, 맞힘 / 개수


torch.manual_seed(0)
변환 = transforms.ToTensor()
학습셋 = datasets.FashionMNIST("data", train=True, download=True, transform=변환)
시험셋 = datasets.FashionMNIST("data", train=False, download=True, transform=변환)
학습_로더 = DataLoader(학습셋, batch_size=64, shuffle=True)    # 64장씩 섞어서(7장)
시험_로더 = DataLoader(시험셋, batch_size=256)

장치 = torch.device("cpu")      # 결과를 똑같이 재현하려고 CPU. 장치_고르기()로 바꿔도 된다
모델 = 의류분류기().to(장치)
손실함수 = nn.CrossEntropyLoss()
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
print(f"파라미터 {sum(p.numel() for p in 모델.parameters()):,}개")

for 에폭 in range(1, 11):
    학습_손실 = 한_에폭_학습(모델, 학습_로더, 손실함수, 옵티마이저, 장치)
    시험_손실, 정확도 = 평가하기(모델, 시험_로더, 손실함수, 장치)
    print(f"에폭 {에폭:2}: 학습 손실 {학습_손실:.4f}, 시험 손실 {시험_손실:.4f}, 시험 정확도 {정확도:.2%}")

torch.save(모델.state_dict(), "fashion_mlp.pt")
print("저장했습니다: fashion_mlp.pt")
