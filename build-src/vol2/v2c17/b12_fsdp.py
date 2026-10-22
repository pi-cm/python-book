import os
import statistics
import time
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.distributed.fsdp import fully_shard
from torch.nn.parallel import DistributedDataParallel as DDP

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=300), device_id=장치)
rank = dist.get_rank()
GB = 1024 ** 3


def 새_모델() -> nn.Sequential:
    """인코더 층 12개 (파라미터 약 1억 5천만 개). 두 방식이 같은 초깃값으로 시작한다."""
    torch.manual_seed(0)
    return nn.Sequential(*[nn.TransformerEncoderLayer(1024, 16, 4096, dropout=0.0, batch_first=True)
                           for _ in range(12)]).to(장치)


def 감싸기(방식: str) -> nn.Module:
    모델 = 새_모델()
    if 방식 == "DDP":
        return DDP(모델)                    # GPU마다 모델 전체를 복사해 둔다
    for 층 in 모델:
        fully_shard(층)                     # 층마다 파라미터를 GPU 수만큼 나눠 맡는다
    return fully_shard(모델)


torch.manual_seed(rank)
x = torch.randn(8, 256, 1024, device=장치)          # 예제용 입력, GPU마다 다르게
for 방식 in ("DDP", "FSDP"):
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    시작_메모리 = torch.cuda.memory_allocated()
    모델 = 감싸기(방식)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-4)
    손실들, 시간들 = [], []
    for _ in range(5):
        torch.cuda.synchronize()
        시작 = time.perf_counter()
        옵티마이저.zero_grad()
        손실 = 모델(x).pow(2).mean()
        손실.backward()
        옵티마이저.step()
        torch.cuda.synchronize()
        시간들.append(time.perf_counter() - 시작)
        손실 = 손실.detach()
        dist.all_reduce(손실)                          # 두 GPU 손실의 평균을 기록
        손실들.append(round(손실.item() / 2, 5))
    남은 = (torch.cuda.memory_allocated() - 시작_메모리) / GB   # 파라미터·기울기·Adam 상태
    if rank == 0:
        print(f"{방식:4}: GPU 하나에 남은 것 {남은:4.2f} GB, 최고 {torch.cuda.max_memory_allocated() / GB:4.2f} GB, "
              f"한 걸음 {statistics.median(시간들[1:]) * 1000:4.0f} ms")
        print(f"      손실 {손실들}")
    del 모델, 옵티마이저
dist.destroy_process_group()
