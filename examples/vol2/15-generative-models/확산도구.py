# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.8 확산 모델: 잡음을 걷어 내며 그리기 · manuscript-vol2/chapters/15-generative-models.md:844]
"""15장 확산 모델 도구: 잡음 일정, 잡음 예측기(작은 U-Net), 그리기(거꾸로 가는 과정)."""
import math

import torch
import torch.nn.functional as F
from torch import nn

T = 1000                                         # 잡음을 더하는 단계 수
베타 = torch.linspace(1e-4, 0.02, T)             # 단계마다 섞는 잡음의 양
알파 = 1 - 베타
알파_누적 = torch.cumprod(알파, dim=0)           # 0단계부터 t단계까지 알파를 모두 곱한 값


def 잡음_더하기(x0: torch.Tensor, t: torch.Tensor, 잡음: torch.Tensor) -> torch.Tensor:
    """깨끗한 사진 x0에 t단계만큼의 잡음을 한 번에 섞는다."""
    a = 알파_누적.to(x0.device)[t].view(-1, 1, 1, 1)
    return a.sqrt() * x0 + (1 - a).sqrt() * 잡음


def 시간_임베딩(t: torch.Tensor, 크기: int) -> torch.Tensor:
    """단계 번호 t를 여러 빠르기의 sin·cos 값으로 펼친다. (배치,) → (배치, 크기)"""
    반 = 크기 // 2
    빠르기 = torch.exp(-math.log(10000) * torch.arange(반, device=t.device) / 반)
    각도 = t.float()[:, None] * 빠르기[None, :]
    return torch.cat([각도.sin(), 각도.cos()], dim=1)


class 블록(nn.Module):
    """합성곱 두 번 + 시간 정보 더하기 + 지름길(잔차 연결)."""

    def __init__(self, 입력: int, 출력: int, 시간_크기: int) -> None:
        super().__init__()
        self.합성곱1 = nn.Conv2d(입력, 출력, 3, padding=1)
        self.정규화1 = nn.GroupNorm(8, 출력)
        self.시간 = nn.Linear(시간_크기, 출력)
        self.합성곱2 = nn.Conv2d(출력, 출력, 3, padding=1)
        self.정규화2 = nn.GroupNorm(8, 출력)
        self.지름길 = nn.Conv2d(입력, 출력, 1) if 입력 != 출력 else nn.Identity()

    def forward(self, x: torch.Tensor, 시간: torch.Tensor) -> torch.Tensor:
        h = F.silu(self.정규화1(self.합성곱1(x)))
        h = h + self.시간(시간)[:, :, None, None]    # 채널마다 '지금 몇 단계인지'를 더한다
        h = F.silu(self.정규화2(self.합성곱2(h)))
        return h + self.지름길(x)


class 작은UNet(nn.Module):
    """28×28 → 14×14 → 7×7로 줄였다가 다시 키우며, 같은 크기끼리 이어 붙이는 잡음 예측기."""

    def __init__(self, 채널: int = 32, 시간_크기: int = 128, 클래스_수: int = 0) -> None:
        super().__init__()
        c = 채널
        self.시간_크기 = 시간_크기
        self.시간_층 = nn.Sequential(nn.Linear(시간_크기, 시간_크기), nn.SiLU(),
                                   nn.Linear(시간_크기, 시간_크기))
        self.클래스_층 = nn.Embedding(클래스_수, 시간_크기) if 클래스_수 > 0 else None
        self.입구 = nn.Conv2d(1, c, 3, padding=1)
        self.내려1, self.줄이기1 = 블록(c, c, 시간_크기), nn.Conv2d(c, c, 4, 2, 1)
        self.내려2, self.줄이기2 = 블록(c, 2 * c, 시간_크기), nn.Conv2d(2 * c, 2 * c, 4, 2, 1)
        self.가운데 = 블록(2 * c, 2 * c, 시간_크기)
        self.키우기2, self.올라2 = nn.ConvTranspose2d(2 * c, 2 * c, 4, 2, 1), 블록(4 * c, 2 * c, 시간_크기)
        self.키우기1, self.올라1 = nn.ConvTranspose2d(2 * c, c, 4, 2, 1), 블록(2 * c, c, 시간_크기)
        self.출구 = nn.Conv2d(c, 1, 3, padding=1)

    def forward(self, x: torch.Tensor, t: torch.Tensor,
                클래스: torch.Tensor | None = None) -> torch.Tensor:
        시간 = self.시간_층(시간_임베딩(t, self.시간_크기))
        if self.클래스_층 is not None:
            시간 = 시간 + self.클래스_층(클래스)         # 무엇을 그릴지도 함께 알려 준다
        h = self.입구(x)
        h1 = self.내려1(h, 시간)                        # (c, 28, 28)
        h2 = self.내려2(self.줄이기1(h1), 시간)         # (2c, 14, 14)
        h = self.가운데(self.줄이기2(h2), 시간)         # (2c, 7, 7)
        h = self.올라2(torch.cat([self.키우기2(h), h2], dim=1), 시간)   # 14×14끼리 이어 붙이기
        h = self.올라1(torch.cat([self.키우기1(h), h1], dim=1), 시간)   # 28×28끼리 이어 붙이기
        return self.출구(h)                             # 예측한 잡음 (1, 28, 28)


@torch.no_grad()
def 그리기(모델: nn.Module, 개수: int, 장치: torch.device, 클래스: torch.Tensor | None = None,
          기록_단계: tuple[int, ...] = ()) -> tuple[torch.Tensor, list[torch.Tensor]]:
    """순수한 잡음에서 출발해 T단계에 걸쳐 잡음을 덜어 낸다. 결과 값은 -1~1."""
    모델.eval()
    베타_, 알파_, 누적_ = 베타.to(장치), 알파.to(장치), 알파_누적.to(장치)
    x = torch.randn(개수, 1, 28, 28, device=장치)
    기록 = []
    for i in reversed(range(T)):
        t = torch.full((개수,), i, device=장치)
        예측_잡음 = 모델(x, t, 클래스)
        x = (x - 베타_[i] / (1 - 누적_[i]).sqrt() * 예측_잡음) / 알파_[i].sqrt()
        if i > 0:
            x = x + 베타_[i].sqrt() * torch.randn_like(x)   # 마지막 단계만 빼고 약간의 무작위를 다시 섞는다
        if i in 기록_단계:
            기록.append(x.cpu())
    return x, 기록
