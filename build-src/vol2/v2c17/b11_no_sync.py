import os
import statistics
import time
from contextlib import nullcontext
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torchvision.models import resnet18

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=300), device_id=장치)
rank, 전체 = dist.get_rank(), dist.get_world_size()

누적 = 4
torch.manual_seed(rank)                               # GPU마다 다른 예제용 입력
조각들 = [(torch.randn(128, 3, 64, 64, device=장치), torch.randint(0, 10, (128,), device=장치))
        for _ in range(누적)]


def 한_걸음(모델: DDP, 옵티마이저: torch.optim.Optimizer, no_sync: bool) -> None:
    """작은 배치 4개의 기울기를 모은 뒤 한 번 고친다."""
    옵티마이저.zero_grad()
    for i, (x, y) in enumerate(조각들):
        마지막 = i == 누적 - 1
        문맥 = 모델.no_sync() if no_sync and not 마지막 else nullcontext()
        with 문맥:                                    # no_sync 안에서는 all_reduce를 건너뛴다
            (nn.functional.cross_entropy(모델(x), y) / 누적).backward()
    옵티마이저.step()


def 새_모델() -> tuple[DDP, torch.optim.Optimizer]:
    torch.manual_seed(0)
    모델 = DDP(resnet18(num_classes=10).to(장치))
    return 모델, torch.optim.SGD(모델.parameters(), lr=0.01)


for no_sync in (False, True):
    모델, 옵티마이저 = 새_모델()
    시간들 = []
    for 걸음 in range(13):
        torch.cuda.synchronize()
        시작 = time.perf_counter()
        한_걸음(모델, 옵티마이저, no_sync)
        torch.cuda.synchronize()
        if 걸음 >= 3:
            시간들.append(time.perf_counter() - 시작)
    장수 = 128 * 누적 * 전체 / statistics.median(시간들)
    if rank == 0:
        print(f"누적 {누적}번, no_sync {'씀 ' if no_sync else '안 씀'}: "
              f"한 걸음 {statistics.median(시간들) * 1000:4.0f} ms, 두 GPU 합계 {장수:6,.0f}장/초")


def 한_걸음_뒤(no_sync: bool) -> list[torch.Tensor]:
    """새 모델로 한 걸음만 고친 뒤의 파라미터."""
    모델, 옵티마이저 = 새_모델()
    한_걸음(모델, 옵티마이저, no_sync)
    return [p.detach().clone() for p in 모델.parameters()]


def 최대_차이(a: list[torch.Tensor], b: list[torch.Tensor]) -> float:
    return max((x - y).abs().max().item() for x, y in zip(a, b))


기준, 다시, 건너뜀 = 한_걸음_뒤(False), 한_걸음_뒤(False), 한_걸음_뒤(True)
if rank == 0:
    print(f"한 걸음 뒤 파라미터 최대 차이: 같은 방식 두 번 {최대_차이(기준, 다시):.1e}, "
          f"no_sync 쓴 쪽과 {최대_차이(기준, 건너뜀):.1e}")
dist.destroy_process_group()
