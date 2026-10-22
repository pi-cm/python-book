# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.5 첫 CNN으로 옷 사진 분류하기 · manuscript-vol2/chapters/09-cnn.md:446]
"""9장 예제에서 함께 쓰는 장치 선택·모델·학습·시험 도구."""
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


class 의류분류기(nn.Module):
    """6장 6.11절의 다층 퍼셉트론 설계도 (fashion_mlp.pt를 불러올 때 쓴다)."""

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


class 옷CNN(nn.Module):
    """합성곱 두 단으로 무늬를 찾고, 완전 연결층 두 개로 옷 종류를 고르는 작은 CNN."""

    def __init__(self) -> None:
        super().__init__()
        self.특징 = nn.Sequential(                       # 그림 모양 그대로 무늬 찾기
            nn.Conv2d(1, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.분류 = nn.Sequential(                       # 찾은 무늬로 종류 고르기
            nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.분류(self.특징(x))


def 한_에폭_학습(모델: nn.Module, 로더: DataLoader, 손실함수: nn.Module,
                옵티마이저: torch.optim.Optimizer, 장치: torch.device) -> float:
    """6장 6.11절과 같은 함수: 한 바퀴 학습하고 평균 손실을 돌려준다."""
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
    """6장 6.11절과 같은 함수: 평균 손실과 정확도를 잰다."""
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


def 시험_데이터() -> tuple[torch.Tensor, torch.Tensor]:
    """FashionMNIST 시험 사진 1만 장을 (10000, 1, 28, 28) 실수 텐서와 정답으로."""
    시험셋 = datasets.FashionMNIST("data", train=False, download=True)
    return 시험셋.data.float().unsqueeze(1) / 255, 시험셋.targets


def 오른쪽으로_밀기(x: torch.Tensor, 칸: int) -> torch.Tensor:
    """사진 묶음을 오른쪽으로 칸만큼 옮기고 빈자리는 0으로 채운다 (1장 1.11절과 같은 일)."""
    밀린 = torch.zeros_like(x)
    밀린[..., 칸:] = x[..., :x.shape[-1] - 칸]
    return 밀린
