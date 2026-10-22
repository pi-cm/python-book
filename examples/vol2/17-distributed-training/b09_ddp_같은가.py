# [2권 Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기 · 17.8 1 GPU와 같은 결과일까 · manuscript-vol2/chapters/17-distributed-training.md:694]
import os
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.distributed import DistributedSampler

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=60), device_id=장치)
rank, 전체 = dist.get_rank(), dist.get_world_size()

torch.manual_seed(0)
데이터 = TensorDataset(torch.randn(256, 20), torch.randn(256, 1))   # 예제용으로 만든 데이터
전체_배치 = 32


def 새_모델() -> nn.Module:
    torch.manual_seed(1)
    return nn.Sequential(nn.Linear(20, 64), nn.ReLU(), nn.Linear(64, 1)).to(장치)


def 학습(모델: nn.Module, 로더: DataLoader, 분산: bool) -> list[float]:
    """한 에폭 동안 걸음마다 (전체 배치의) 손실을 기록한다."""
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.1)
    기록 = []
    for x, y in 로더:
        옵티마이저.zero_grad()
        손실 = nn.functional.mse_loss(모델(x.to(장치)), y.to(장치))
        손실.backward()
        옵티마이저.step()
        손실 = 손실.detach()
        if 분산:
            dist.all_reduce(손실)          # 두 GPU의 손실 평균 = 전체 배치의 손실
            손실 /= 전체
        기록.append(round(손실.item(), 5))
    return 기록


# 2 GPU: GPU마다 16개씩, 합쳐서 32개
샘플러 = DistributedSampler(데이터, shuffle=False)
ddp = DDP(새_모델())
ddp_기록 = 학습(ddp, DataLoader(데이터, batch_size=전체_배치 // 전체, sampler=샘플러), 분산=True)

if rank == 0:                              # 비교용: 1 GPU에서 32개씩
    하나 = 새_모델()
    하나_기록 = 학습(하나, DataLoader(데이터, batch_size=전체_배치), 분산=False)
    print("2 GPU × 16개:", ddp_기록)
    print("1 GPU × 32개:", 하나_기록)
    차이 = max((a - b).abs().max().item()
             for a, b in zip(ddp.module.parameters(), 하나.parameters()))
    print(f"8걸음 뒤 파라미터 최대 차이: {차이:.1e}")
dist.barrier()
dist.destroy_process_group()
