# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.3 합성곱 오토인코더로 잡음 지우기 · manuscript-vol2/chapters/15-generative-models.md:345]
import torch
import torch.nn.functional as F
from torch import nn

from 생성도구 import 격자_저장, 사진_불러오기, 오토인코더_학습


class 합성곱_오토인코더(nn.Module):
    """합성곱으로 28×28 → 7×7로 줄였다가, 전치 합성곱으로 다시 28×28로 키운다."""

    def __init__(self) -> None:
        super().__init__()
        self.인코더 = nn.Sequential(
            nn.Conv2d(1, 16, 3, stride=2, padding=1), nn.ReLU(),     # (16, 14, 14)
            nn.Conv2d(16, 32, 3, stride=2, padding=1), nn.ReLU(),    # (32, 7, 7)
        )
        self.디코더 = nn.Sequential(
            nn.ConvTranspose2d(32, 16, 4, stride=2, padding=1), nn.ReLU(),  # (16, 14, 14)
            nn.ConvTranspose2d(16, 1, 4, stride=2, padding=1), nn.Sigmoid(),  # (1, 28, 28)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.디코더(self.인코더(x))


torch.manual_seed(0)
X_학습, _ = 사진_불러오기(학습=True)
X_시험, _ = 사진_불러오기(학습=False)

모델 = 합성곱_오토인코더()
print(f"파라미터 {sum(p.numel() for p in 모델.parameters()):,}개")
오토인코더_학습(모델, X_학습, 에폭=3, 잡음=0.4)      # 잡음 섞인 입력 → 깨끗한 원본

모델.eval()
잡음_사진 = (X_시험 + 0.4 * torch.randn_like(X_시험)).clamp(0, 1)
with torch.no_grad():
    고친_사진 = 모델(잡음_사진)
print(f"잡음 사진과 원본의 차이(MSE): {F.mse_loss(잡음_사진, X_시험):.4f}")
print(f"고친 사진과 원본의 차이(MSE): {F.mse_loss(고친_사진, X_시험):.4f}")

격자_저장(torch.cat([잡음_사진[:8], 고친_사진[:8], X_시험[:8]]), "denoise.png")
