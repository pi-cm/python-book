# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.1 오토인코더: 줄였다가 되살리기 · manuscript-vol2/chapters/15-generative-models.md:49]
"""15장에서 함께 쓰는 데이터·그림·오토인코더 도구."""
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets
from torchvision.utils import save_image

이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트", "샌들", "셔츠", "운동화", "가방", "앵클부츠"]


def 사진_불러오기(학습: bool = True) -> tuple[torch.Tensor, torch.Tensor]:
    """FashionMNIST를 통째로 (N, 1, 28, 28) 텐서(값 0~1)와 정답 텐서로 돌려준다."""
    셋 = datasets.FashionMNIST("data", train=학습, download=True)
    return 셋.data.unsqueeze(1).float() / 255, 셋.targets


def 로더_만들기(X: torch.Tensor, 배치: int = 256, 씨앗: int = 0) -> DataLoader:
    """사진만 담은 DataLoader. 정답이 필요 없으니 사진 하나만 넘긴다."""
    return DataLoader(TensorDataset(X), batch_size=배치, shuffle=True,
                      generator=torch.Generator().manual_seed(씨앗))


def 격자_저장(사진들: torch.Tensor, 파일: str, 한_줄: int = 8) -> None:
    """(N, 1, 28, 28) 사진 묶음을 격자 한 장으로 저장한다. 인쇄용으로 3배 키운다."""
    큰_사진 = F.interpolate(사진들.detach().cpu().clamp(0, 1), scale_factor=3, mode="nearest")
    save_image(큰_사진, 파일, nrow=한_줄, padding=6, pad_value=1.0)


class 오토인코더(nn.Module):
    """784칸 사진을 잠재_크기 칸으로 줄였다가(인코더) 다시 784칸으로 되살린다(디코더)."""

    def __init__(self, 잠재_크기: int = 32) -> None:
        super().__init__()
        self.인코더 = nn.Sequential(
            nn.Flatten(),
            nn.Linear(784, 256), nn.ReLU(),
            nn.Linear(256, 잠재_크기),
        )
        self.디코더 = nn.Sequential(
            nn.Linear(잠재_크기, 256), nn.ReLU(),
            nn.Linear(256, 784), nn.Sigmoid(),      # 밝기를 0~1로
            nn.Unflatten(1, (1, 28, 28)),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.디코더(self.인코더(x))


def 오토인코더_학습(모델: nn.Module, X: torch.Tensor, 에폭: int = 5,
                   잡음: float = 0.0, 출력: bool = True) -> nn.Module:
    """입력을 그대로 되살리도록 학습한다. 잡음 > 0이면 잡음 섞은 입력에서 깨끗한 원본을 되살린다."""
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    for 에폭_번호 in range(1, 에폭 + 1):
        손실_합 = 0.0
        for (x,) in 로더_만들기(X, 씨앗=에폭_번호):
            입력 = (x + 잡음 * torch.randn_like(x)).clamp(0, 1) if 잡음 > 0 else x
            손실 = F.mse_loss(모델(입력), x)         # 정답은 언제나 깨끗한 원본
            옵티마이저.zero_grad()
            손실.backward()
            옵티마이저.step()
            손실_합 += 손실.item() * len(x)
        if 출력:
            print(f"에폭 {에폭_번호}: 재구성 손실 {손실_합 / len(X):.4f}")
    return 모델


def 채점기_만들기(장치: torch.device, 에폭: int = 2) -> nn.Module:
    """생성한 그림을 채점할 작은 CNN 옷 분류기를 진짜 사진으로 학습해 돌려준다."""
    torch.manual_seed(0)
    X, y = 사진_불러오기(학습=True)
    모델 = nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10),
    ).to(장치)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    로더 = DataLoader(TensorDataset(X, y), batch_size=128, shuffle=True,
                    generator=torch.Generator().manual_seed(0))
    for _ in range(에폭):
        for x, 정답 in 로더:
            손실 = F.cross_entropy(모델(x.to(장치)), 정답.to(장치))
            옵티마이저.zero_grad()
            손실.backward()
            옵티마이저.step()
    return 모델.eval()
