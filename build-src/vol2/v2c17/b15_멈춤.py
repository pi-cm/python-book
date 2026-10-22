import time
from datetime import timedelta

import torch
import torch.distributed as dist

# CPU끼리(gloo) 통신. 기다리는 한계를 5초로 짧게 잡는다
dist.init_process_group("gloo", timeout=timedelta(seconds=5))
rank = dist.get_rank()
x = torch.ones(1)

if rank == 0:                      # 실수: rank 0만 all_reduce를 부른다
    시작 = time.perf_counter()
    try:
        dist.all_reduce(x)
    except RuntimeError as e:
        print(f"[rank 0] {time.perf_counter() - 시작:.0f}초 만에 오류:", str(e).split("] ", 1)[-1])  # 파일 위치는 떼고
else:
    time.sleep(8)                  # rank 1은 다른 일을 하느라 통신에 오지 않는다
    print("[rank 1] 끝", flush=True)
