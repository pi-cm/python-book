import os
import time
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision import datasets, transforms

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")


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


def 분산_시작() -> torch.device:
    """torchrun이 넣어 준 환경 변수로 프로세스 그룹에 들어간다."""
    if torch.cuda.is_available():
        장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
        torch.cuda.set_device(장치)
        dist.init_process_group("nccl", timeout=timedelta(seconds=120), device_id=장치)
    else:
        장치 = torch.device("cpu")
        dist.init_process_group("gloo", timeout=timedelta(seconds=120))
    return 장치


def 옷_데이터(학습: bool) -> datasets.FashionMNIST:
    return datasets.FashionMNIST(데이터_폴더, train=학습, download=True,
                                 transform=transforms.ToTensor())


def 정확도(모델: nn.Module, 장치: torch.device) -> float:
    """시험 데이터 1만 장의 정확도 (rank 0에서만 부른다)."""
    모델.eval()
    맞힘 = 0
    with torch.no_grad():
        for x, y in DataLoader(옷_데이터(False), batch_size=1000):
            맞힘 += (모델(x.to(장치)).argmax(1) == y.to(장치)).sum().item()
    return 맞힘 / 10_000


장치 = 분산_시작()
rank, 전체 = dist.get_rank(), dist.get_world_size()
if rank == 0:
    옷_데이터(True), 옷_데이터(False)          # 내려받기는 한 프로세스만
dist.barrier()                               # 다 받을 때까지 나머지는 기다린다

학습셋 = 옷_데이터(True)
샘플러 = DistributedSampler(학습셋, shuffle=True, seed=0)   # 데이터를 프로세스 수만큼 나눈다
로더 = DataLoader(학습셋, batch_size=128, sampler=샘플러)    # GPU마다 128장, 합쳐서 256장
for 차례 in range(전체):
    if rank == 차례:
        print(f"[rank {rank}] 맡은 샘플 {len(샘플러):,}개, 배치 {len(로더)}개, "
              f"앞 번호 {list(샘플러)[:4]}", flush=True)
    dist.barrier()

torch.manual_seed(0)                         # 모든 프로세스가 같은 초깃값으로 시작
모델 = DDP(옷CNN().to(장치))                  # 기울기를 all_reduce로 평균 내 주는 포장지
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
손실함수 = nn.CrossEntropyLoss()

for 에폭 in range(1, 4):
    샘플러.set_epoch(에폭)                    # 에폭마다 섞는 순서를 바꾼다
    모델.train()
    합계 = torch.zeros(2, device=장치)         # [손실 합, 개수]
    시작 = time.perf_counter()
    for x, y in 로더:
        x, y = x.to(장치), y.to(장치)
        옵티마이저.zero_grad()
        손실 = 손실함수(모델(x), y)
        손실.backward()                       # 여기서 GPU끼리 기울기를 평균 낸다
        옵티마이저.step()
        합계[0] += 손실.detach() * len(y)
        합계[1] += len(y)
    dist.all_reduce(합계)                     # 모든 프로세스의 손실을 모은다
    if rank == 0:
        print(f"에폭 {에폭}: 학습 손실 {합계[0] / 합계[1]:.4f} "
              f"({int(합계[1]):,}장, {time.perf_counter() - 시작:.1f}초)")

if rank == 0:                                # 저장과 평가는 한 프로세스만
    print(f"시험 정확도: {정확도(모델.module, 장치):.2%}")
    torch.save({"에폭": 3, "모델": 모델.module.state_dict(),
                "옵티마이저": 옵티마이저.state_dict()}, "ddp_옷CNN.pt")
    print("저장한 키:", list(torch.load("ddp_옷CNN.pt")["모델"])[:2], "...")
dist.barrier()
dist.destroy_process_group()
