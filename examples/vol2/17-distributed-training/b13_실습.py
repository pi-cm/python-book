# [2권 Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기 · 17.13 실습: 옷 분류기를 세 가지 방법으로 학습하기 · manuscript-vol2/chapters/17-distributed-training.md:1129]
"""17장 실습: 옷 사진 CNN을 1 GPU, 그래디언트 누적, DDP 2 GPU로 학습해 비교한다.

python으로 실행하면 프로세스 하나, torchrun으로 실행하면 분산 학습이 된다.
"""
import argparse
import os
import time
from contextlib import nullcontext
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision import datasets, transforms

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")
전체_배치 = 256                                      # 한 걸음에 반영하는 사진 수는 언제나 256장


class 옷CNN(nn.Module):
    """9장 9.5절의 작은 CNN."""

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


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


def 준비() -> tuple[torch.device, bool]:
    """torchrun으로 실행됐으면 분산을 시작하고, 아니면 장치만 고른다."""
    if "RANK" not in os.environ:
        return 장치_고르기(), False
    if torch.cuda.is_available():
        장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
        torch.cuda.set_device(장치)
        dist.init_process_group("nccl", timeout=timedelta(seconds=120), device_id=장치)
    else:
        장치 = torch.device("cpu")
        dist.init_process_group("gloo", timeout=timedelta(seconds=120))
    return 장치, True


def 옷_데이터(학습: bool) -> datasets.FashionMNIST:
    return datasets.FashionMNIST(데이터_폴더, train=학습, download=True,
                                 transform=transforms.ToTensor())


def 정확도(모델: nn.Module, 장치: torch.device) -> float:
    모델.eval()
    맞힘 = 0
    with torch.no_grad():
        for x, y in DataLoader(옷_데이터(False), batch_size=1000):
            맞힘 += (모델(x.to(장치)).argmax(1) == y.to(장치)).sum().item()
    return 맞힘 / 10_000


def 한_에폭(모델: nn.Module, 로더: DataLoader, 옵티마이저: torch.optim.Optimizer,
           장치: torch.device, 누적: int, 분산: bool) -> torch.Tensor:
    """한 에폭 학습하고 [손실 합, 개수]를 돌려준다. 배치를 누적 횟수만큼 나눠 기울기를 모은다."""
    모델.train()
    합계 = torch.zeros(2, device=장치)
    for x, y in 로더:
        x, y = x.to(장치), y.to(장치)
        옵티마이저.zero_grad()
        for i, (xb, yb) in enumerate(zip(x.chunk(누적), y.chunk(누적))):
            건너뛰기 = 분산 and i < 누적 - 1                   # 마지막 조각에서만 통신
            with 모델.no_sync() if 건너뛰기 else nullcontext():
                손실 = nn.functional.cross_entropy(모델(xb), yb)
                (손실 / 누적).backward()
            합계[0] += 손실.detach() * len(yb)
            합계[1] += len(yb)
        옵티마이저.step()
    return 합계


def main() -> None:
    인자 = argparse.ArgumentParser()
    인자.add_argument("--누적", type=int, default=1)
    인자.add_argument("--에폭", type=int, default=5)
    설정 = 인자.parse_args()

    장치, 분산 = 준비()
    rank = dist.get_rank() if 분산 else 0
    전체 = dist.get_world_size() if 분산 else 1
    if rank == 0:
        옷_데이터(True), 옷_데이터(False)              # 내려받기는 한 프로세스만
    if 분산:
        dist.barrier()

    학습셋 = 옷_데이터(True)
    GPU당 = 전체_배치 // 전체
    if 분산:
        샘플러 = DistributedSampler(학습셋, shuffle=True, seed=0)
        로더 = DataLoader(학습셋, batch_size=GPU당, sampler=샘플러)
    else:
        샘플러 = None
        로더 = DataLoader(학습셋, batch_size=GPU당, shuffle=True,
                        generator=torch.Generator().manual_seed(0))

    torch.manual_seed(0)
    모델 = 옷CNN().to(장치)
    if 분산:
        모델 = DDP(모델)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    if 장치.type == "cuda":
        torch.cuda.reset_peak_memory_stats(장치)

    손실들 = []
    시작 = time.perf_counter()
    for 에폭 in range(설정.에폭):
        if 샘플러 is not None:
            샘플러.set_epoch(에폭)
        합계 = 한_에폭(모델, 로더, 옵티마이저, 장치, 설정.누적, 분산)
        if 분산:
            dist.all_reduce(합계)
        손실들.append(round((합계[0] / 합계[1]).item(), 4))
    걸린_시간 = time.perf_counter() - 시작

    if rank == 0:
        원본 = 모델.module if 분산 else 모델
        조각 = f" ({GPU당 // 설정.누적}장 × {설정.누적}번 누적)" if 설정.누적 > 1 else ""
        메모리 = (f"{torch.cuda.max_memory_allocated(장치) / 1024 ** 2:.0f} MB"
                if 장치.type == "cuda" else "-")
        print(f"[{장치.type} {전체}개 × {GPU당}장{조각}]")
        print(f"  에폭별 학습 손실 {손실들}")
        print(f"  시험 정확도 {정확도(원본, 장치):.2%}, 학습 {걸린_시간:.1f}초, GPU당 최고 메모리 {메모리}")
    if 분산:
        dist.destroy_process_group()


if __name__ == "__main__":
    main()
