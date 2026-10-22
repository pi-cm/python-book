import os
import statistics
import time
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torchvision.models import resnet18, resnet50

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=300), device_id=장치)
rank = dist.get_rank()


class 작은CNN(nn.Module):
    """9장의 옷CNN과 같은 구조 (파라미터 42만 개)."""

    def __init__(self) -> None:
        super().__init__()
        self.층들 = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.층들(x)


def 초당_장수(모델: nn.Module, 배치: int, 크기: int, 채널: int) -> float:
    """GPU 하나가 1초에 학습하는 사진 수 (준비 운동 3걸음 뒤 10걸음의 중앙값)."""
    x = torch.randn(배치, 채널, 크기, 크기, device=장치)        # 예제용 입력
    y = torch.randint(0, 10, (배치,), device=장치)
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.01)
    시간들 = []
    for 걸음 in range(13):
        torch.cuda.synchronize()
        시작 = time.perf_counter()
        옵티마이저.zero_grad()
        nn.functional.cross_entropy(모델(x), y).backward()
        옵티마이저.step()
        torch.cuda.synchronize()
        if 걸음 >= 3:
            시간들.append(time.perf_counter() - 시작)
    return 배치 / statistics.median(시간들)


실험들 = [  # (이름, 모델 만들기, GPU당 배치, 사진 크기, 채널)
    ("작은CNN 28px", 작은CNN, 256, 28, 1),
    ("ResNet18 64px", lambda: resnet18(num_classes=10), 128, 64, 3),
    ("ResNet18 224px", lambda: resnet18(num_classes=10), 128, 224, 3),
    ("ResNet50 224px", lambda: resnet50(num_classes=10), 64, 224, 3),
]
if rank == 0:
    print(f"{'모델':14} {'기울기 MB':>8} {'1 GPU':>7} {'2 GPU':>7} {'배율':>5}")
for 이름, 만들기, 배치, 크기, 채널 in 실험들:
    torch.manual_seed(0)
    모델 = 만들기().to(장치)
    MB = sum(p.numel() for p in 모델.parameters()) * 4 / 1024 ** 2
    하나 = 초당_장수(모델, 배치, 크기, 채널) if rank == 0 else 0.0   # GPU 0 혼자
    dist.barrier()
    둘 = 초당_장수(DDP(모델), 배치, 크기, 채널) * dist.get_world_size()  # 두 GPU 합계
    if rank == 0:
        print(f"{이름:14} {MB:8.1f} {하나:7,.0f} {둘:7,.0f} {둘 / 하나:5.2f}")
dist.barrier()
dist.destroy_process_group()
