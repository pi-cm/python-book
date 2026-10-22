import os
import statistics
import time
from datetime import timedelta

import torch
import torch.distributed as dist

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=60), device_id=장치)
rank = dist.get_rank()
MB = 1024 ** 2


def 재기(일, 횟수: int = 10) -> float:
    """준비 운동 3번 뒤 횟수만큼 재서 중앙값(초)을 돌려준다."""
    for _ in range(3):
        일()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(횟수):
        시작 = time.perf_counter()
        일()
        torch.cuda.synchronize()
        시간들.append(time.perf_counter() - 시작)
    return statistics.median(시간들)


if rank == 0:
    print(f"GPU {dist.get_world_size()}개: {torch.cuda.get_device_name(장치)}")
for 크기 in (1, 4, 16, 64, 256):
    x = torch.ones(크기 * MB // 4, device=장치)                  # float32 크기 MB짜리
    초 = 재기(lambda: dist.all_reduce(x))
    if rank == 0:
        print(f"all_reduce {크기:3} MB: {초 * 1000:7.2f} ms ({크기 / 1024 / 초:5.2f} GB/s)")

if rank == 0:                                                 # 비교: 같은 GPU 안에서 복사
    x = torch.ones(256 * MB // 4, device=장치)
    y = torch.empty_like(x)
    초 = 재기(lambda: y.copy_(x))
    print(f"GPU 안 복사 256 MB: {초 * 1000:7.2f} ms ({256 / 1024 / 초:5.0f} GB/s)")
dist.barrier()
dist.destroy_process_group()
