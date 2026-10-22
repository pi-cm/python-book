# [2권 Chapter 18. 실험 관리와 재현성 · 18.2 설정을 코드 밖으로 · manuscript-vol2/chapters/18-experiment-management.md:257]
"""18장 예제에서 함께 쓰는 설정·데이터·모델·학습 도구."""
import os
import random
from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")    # 2장부터 써 온 데이터 폴더 설정


@dataclass
class 학습설정:
    """실험 하나를 정하는 값들. 코드와 이 값이 같으면 결과도 같아야 한다."""
    모델: str = "mlp"             # "mlp"(6장) 또는 "cnn"(9장)
    학습률: float = 1e-3
    배치_크기: int = 64
    에폭: int = 2
    드롭아웃: float = 0.0
    가중치_감쇠: float = 0.0
    학습_개수: int = 55_000       # 노트북에서 빨리 돌려 볼 때는 줄인다
    씨앗: int = 0


def 씨앗_고정(씨앗: int) -> None:
    """8장 8.10절: 파이썬·NumPy·PyTorch의 난수 씨앗을 한꺼번에 고정한다."""
    random.seed(씨앗)
    np.random.seed(씨앗)
    torch.manual_seed(씨앗)


def 옷_데이터(학습_개수: int = 55_000, 검증_개수: int = 5_000):
    """FashionMNIST를 텐서로 읽어 학습·검증·시험으로 나눈다. 나누는 방법은 언제나 같다."""
    학습셋 = datasets.FashionMNIST(데이터_폴더, train=True, download=True)
    시험셋 = datasets.FashionMNIST(데이터_폴더, train=False, download=True)
    X, y = 학습셋.data.float().unsqueeze(1) / 255, 학습셋.targets
    순서 = torch.randperm(len(X), generator=torch.Generator().manual_seed(0))
    검증, 학습 = 순서[:검증_개수], 순서[검증_개수:검증_개수 + 학습_개수]
    X_시험 = 시험셋.data.float().unsqueeze(1) / 255
    return (X[학습], y[학습]), (X[검증], y[검증]), (X_시험, 시험셋.targets)


def 모델_만들기(설정: 학습설정) -> nn.Sequential:
    """설정에 적힌 이름으로 6장의 MLP나 9장의 CNN을 만든다."""
    if 설정.모델 == "mlp":
        몸통 = [nn.Flatten(), nn.Linear(28 * 28, 256), nn.ReLU(), nn.Linear(256, 128), nn.ReLU()]
        마지막 = 128
    elif 설정.모델 == "cnn":
        몸통 = [nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
               nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
               nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU()]
        마지막 = 128
    else:
        raise ValueError(f"모르는 모델 이름: {설정.모델}")
    if 설정.드롭아웃 > 0:
        몸통.append(nn.Dropout(설정.드롭아웃))
    return nn.Sequential(*몸통, nn.Linear(마지막, 10))


def 로더_만들기(X: torch.Tensor, y: torch.Tensor, 배치_크기: int, 씨앗: int) -> DataLoader:
    """섞는 순서를 자기 생성기로 정하는 DataLoader (4장 4.1절, 7장)."""
    생성기 = torch.Generator().manual_seed(씨앗)
    return DataLoader(TensorDataset(X, y), batch_size=배치_크기, shuffle=True, generator=생성기)


def 한_에폭_학습(모델: nn.Module, 로더: DataLoader, 옵티마이저: torch.optim.Optimizer) -> float:
    """한 바퀴 학습하고 평균 손실을 돌려준다."""
    모델.train()
    손실_합, 개수 = 0.0, 0
    for x, y in 로더:
        옵티마이저.zero_grad()
        손실 = nn.functional.cross_entropy(모델(x), y)
        손실.backward()
        옵티마이저.step()
        손실_합 += 손실.item() * len(y)
        개수 += len(y)
    return 손실_합 / 개수


@torch.no_grad()
def 평가(모델: nn.Module, X: torch.Tensor, y: torch.Tensor) -> tuple[float, float]:
    """손실과 정확도를 돌려준다. 메모리를 아끼려고 1,000장씩 나눠 계산한다."""
    모델.eval()
    출력 = torch.cat([모델(X[i:i + 1000]) for i in range(0, len(X), 1000)])
    return nn.functional.cross_entropy(출력, y).item(), (출력.argmax(dim=1) == y).float().mean().item()
