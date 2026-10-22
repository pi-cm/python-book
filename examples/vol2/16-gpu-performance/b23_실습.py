# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.13 실습: 옷 분류기 학습을 단계별로 빠르게 · manuscript-vol2/chapters/16-gpu-performance.md:1422]
import os
import time
from contextlib import nullcontext

import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import v2

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")


class 잔차블록(nn.Module):
    """9장 9.8절의 잔차 블록."""

    def __init__(self, 입력: int, 출력: int, 보폭: int = 1) -> None:
        super().__init__()
        self.합성곱1 = nn.Conv2d(입력, 출력, 3, stride=보폭, padding=1, bias=False)
        self.정규화1 = nn.BatchNorm2d(출력)
        self.합성곱2 = nn.Conv2d(출력, 출력, 3, padding=1, bias=False)
        self.정규화2 = nn.BatchNorm2d(출력)
        self.지름길 = nn.Identity()
        if 보폭 != 1 or 입력 != 출력:
            self.지름길 = nn.Sequential(nn.Conv2d(입력, 출력, 1, stride=보폭, bias=False),
                                        nn.BatchNorm2d(출력))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        고칠양 = self.정규화2(self.합성곱2(F.relu(self.정규화1(self.합성곱1(x)))))
        return F.relu(고칠양 + self.지름길(x))


def 작은_ResNet() -> nn.Sequential:
    """9장 9.10절의 작은 ResNet."""
    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1, bias=False), nn.BatchNorm2d(32), nn.ReLU(),
        잔차블록(32, 32), 잔차블록(32, 64, 보폭=2), 잔차블록(64, 128, 보폭=2),
        nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(0.3), nn.Linear(128, 10))


def 로더들(일꾼: int) -> tuple[DataLoader, DataLoader]:
    증강 = v2.Compose([v2.ToImage(), v2.RandomCrop(28, padding=2), v2.RandomHorizontalFlip(),
                       v2.ToDtype(torch.float32, scale=True)])
    기본 = v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
    학습 = datasets.FashionMNIST(데이터_폴더, train=True, download=True, transform=증강)
    시험 = datasets.FashionMNIST(데이터_폴더, train=False, download=True, transform=기본)
    옵션 = dict(num_workers=일꾼, pin_memory=일꾼 > 0, persistent_workers=일꾼 > 0)
    return (DataLoader(학습, batch_size=256, shuffle=True, **옵션),
            DataLoader(시험, batch_size=1024, **옵션))


def 실험(이름: str, amp: bool, 컴파일: bool, 일꾼: int, 에폭_수: int = 4) -> None:
    torch.manual_seed(0)
    학습_로더, 시험_로더 = 로더들(일꾼)
    모델 = 작은_ResNet().to("cuda")
    옵티마이저 = torch.optim.AdamW(모델.parameters())        # 학습률은 아래 OneCycleLR이 정한다
    스케줄러 = torch.optim.lr_scheduler.OneCycleLR(          # 8장 8.7절, 배치마다 step()
        옵티마이저, max_lr=4e-3, total_steps=에폭_수 * len(학습_로더))
    실행 = torch.compile(모델) if 컴파일 else 모델

    def 정밀도():
        """amp를 켰으면 bfloat16 autocast, 아니면 아무것도 안 하는 with 블록."""
        return torch.autocast("cuda", dtype=torch.bfloat16) if amp else nullcontext()

    에폭_시간 = []
    for _ in range(에폭_수):
        모델.train()
        torch.cuda.synchronize()
        시작 = time.perf_counter()
        for x, y in 학습_로더:
            x, y = x.to("cuda", non_blocking=True), y.to("cuda", non_blocking=True)
            with 정밀도():
                손실 = F.cross_entropy(실행(x), y)
            옵티마이저.zero_grad(set_to_none=True)
            손실.backward()
            옵티마이저.step()
            스케줄러.step()
        torch.cuda.synchronize()
        에폭_시간.append(time.perf_counter() - 시작)
    모델.eval()
    맞힘 = 0
    with torch.no_grad(), 정밀도():
        for x, y in 시험_로더:
            맞힘 += (실행(x.to("cuda")).argmax(dim=1).cpu() == y).sum().item()
    이후 = sum(에폭_시간[1:]) / (에폭_수 - 1)               # 첫 에폭은 준비 시간이 섞여 따로 본다
    print(f"첫 에폭 {에폭_시간[0]:4.1f}초 | 이후 에폭 평균 {이후:4.1f}초"
          f" | 시험 정확도 {맞힘 / 100:5.2f}% ← {이름}")


if __name__ == "__main__":
    실험("① 기본", amp=False, 컴파일=False, 일꾼=0)
    실험("② + bfloat16 autocast", amp=True, 컴파일=False, 일꾼=0)
    실험("③ + torch.compile", amp=True, 컴파일=True, 일꾼=0)
    실험("④ + 데이터 로더 일꾼 8", amp=True, 컴파일=True, 일꾼=8)
    실험("⑤ ④에서 autocast·compile 빼기", amp=False, 컴파일=False, 일꾼=8)
