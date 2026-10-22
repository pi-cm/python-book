"""20장 예제에서 함께 쓰는 옷 분류 모델 도구 (9장 9.5절의 옷CNN)."""
from pathlib import Path

import torch
from torch import nn

클래스_이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트",
          "샌들", "셔츠", "운동화", "가방", "앵클부츠"]


class 옷CNN(nn.Module):
    """9장 9.5절의 작은 CNN: 합성곱 두 단 + 완전 연결층 두 개."""

    def __init__(self) -> None:
        super().__init__()
        self.특징 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.분류 = nn.Sequential(
            nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.분류(self.특징(x))


def 모델_불러오기(경로: str | Path = "fashion_cnn.pt") -> 옷CNN:
    """저장된 가중치를 CPU로 불러와 평가 모드로 돌려준다."""
    모델 = 옷CNN()
    모델.load_state_dict(torch.load(경로, map_location="cpu", weights_only=True))
    return 모델.eval()
