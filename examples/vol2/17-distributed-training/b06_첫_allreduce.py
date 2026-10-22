# [2권 Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기 · 17.5 분산의 기본 낱말: 프로세스, rank, all-reduce · manuscript-vol2/chapters/17-distributed-training.md:391]
import os
from datetime import timedelta

import torch
import torch.distributed as dist


def 분산_시작() -> torch.device:
    """torchrun이 넣어 준 환경 변수로 프로세스 그룹에 들어간다."""
    if torch.cuda.is_available():
        장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))  # 프로세스마다 GPU 하나
        torch.cuda.set_device(장치)
        dist.init_process_group("nccl", timeout=timedelta(seconds=60), device_id=장치)
    else:
        장치 = torch.device("cpu")                                  # GPU가 없으면 CPU끼리
        dist.init_process_group("gloo", timeout=timedelta(seconds=60))
    return 장치


def 차례로_말하기(말: str) -> None:
    """rank 0부터 차례로 한 줄씩 출력한다 (출력이 뒤섞이지 않게)."""
    for 차례 in range(dist.get_world_size()):
        if dist.get_rank() == 차례:
            print(말, flush=True)
        dist.barrier()                                              # 모두 여기까지 올 때까지 기다린다


장치 = 분산_시작()
rank, 전체 = dist.get_rank(), dist.get_world_size()
if rank == 0:
    print(f"백엔드 {dist.get_backend()}, 프로세스 {전체}개", flush=True)
dist.barrier()

x = torch.full((3,), float(rank + 1), device=장치)                  # rank 0은 1, rank 1은 2
차례로_말하기(f"[rank {rank}] 내 값        {x.tolist()} ({장치})")
dist.all_reduce(x, op=dist.ReduceOp.SUM)                            # 모두의 값을 더해 모두에게
차례로_말하기(f"[rank {rank}] all_reduce 뒤 {x.tolist()}")

평균 = torch.tensor([float(rank + 1)], device=장치)
dist.all_reduce(평균)                                               # 더한 뒤
평균 /= 전체                                                        # 프로세스 수로 나누면 평균
차례로_말하기(f"[rank {rank}] 평균          {평균.item()}")

dist.destroy_process_group()                                        # 끝낼 때 정리
