# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.6 VAE: 점 대신 구름으로 · manuscript-vol2/chapters/15-generative-models.md:583]
import torch
import torch.nn.functional as F
from torch import nn

from 생성도구 import 격자_저장, 로더_만들기, 사진_불러오기


class VAE(nn.Module):
    """인코더가 점 하나 대신 '평균과 로그분산'을 내는 변분 오토인코더."""

    def __init__(self, 잠재_크기: int = 2) -> None:
        super().__init__()
        self.몸통 = nn.Sequential(nn.Flatten(), nn.Linear(784, 256), nn.ReLU())
        self.평균 = nn.Linear(256, 잠재_크기)
        self.로그분산 = nn.Linear(256, 잠재_크기)
        self.디코더 = nn.Sequential(
            nn.Linear(잠재_크기, 256), nn.ReLU(),
            nn.Linear(256, 784),                      # 로짓. 시그모이드는 손실 함수와 그림 그릴 때
            nn.Unflatten(1, (1, 28, 28)),
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        h = self.몸통(x)
        평균, 로그분산 = self.평균(h), self.로그분산(h)
        z = 평균 + torch.exp(0.5 * 로그분산) * torch.randn_like(평균)   # 재매개변수화
        return self.디코더(z), 평균, 로그분산


def vae_손실(로짓: torch.Tensor, x: torch.Tensor, 평균: torch.Tensor,
            로그분산: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """사진 한 장당 재구성 손실과 KL 발산 (둘 다 칸별 값을 더한 뒤 배치 평균)."""
    재구성 = F.binary_cross_entropy_with_logits(로짓, x, reduction="sum") / len(x)
    kl = -0.5 * (1 + 로그분산 - 평균 ** 2 - 로그분산.exp()).sum() / len(x)
    return 재구성, kl


torch.manual_seed(0)
X_학습, _ = 사진_불러오기(학습=True)
모델 = VAE(잠재_크기=2)
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)

for 에폭 in range(1, 11):
    합계 = torch.zeros(2)
    for (x,) in 로더_만들기(X_학습, 씨앗=에폭):
        로짓, 평균, 로그분산 = 모델(x)
        재구성, kl = vae_손실(로짓, x, 평균, 로그분산)
        옵티마이저.zero_grad()
        (재구성 + kl).backward()
        옵티마이저.step()
        합계 += torch.tensor([재구성.item(), kl.item()]) * len(x)
    재구성_평균, kl_평균 = (합계 / len(X_학습)).tolist()
    if 에폭 in (1, 2, 5, 10):
        print(f"에폭 {에폭:2}: 재구성 {재구성_평균:6.1f}, KL {kl_평균:4.2f}")

torch.save(모델.state_dict(), "vae.pt")

# 표준정규분포에서 점을 뽑아 디코더에 넣으면 새 사진이 나온다
모델.eval()
with torch.no_grad():
    새_사진 = torch.sigmoid(모델.디코더(torch.randn(1000, 2)))
격자_저장(새_사진[:32], "vae_samples.png")
torch.save(새_사진, "vae_1000.pt")                  # 15.9절에서 채점할 1,000장
