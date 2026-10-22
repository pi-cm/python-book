import statistics
import time

import torch


def 재기(함수, 반복: int = 30) -> float:
    """준비 운동 뒤 동기화하며 재고 중앙값(ms)을 돌려준다."""
    for _ in range(5):
        함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


print(f"CPU 스레드 {torch.get_num_threads()}개")
for n in [16, 64, 256, 1024, 4096]:
    a, b = torch.randn(n, n), torch.randn(n, n)
    ga, gb = a.to("cuda"), b.to("cuda")
    cpu = 재기(lambda: a @ b)
    gpu = 재기(lambda: ga @ gb)
    왕복 = 재기(lambda: (a.to("cuda") @ b.to("cuda")).cpu())   # 옮기고, 곱하고, 되가져오기
    print(f"{n:>4}×{n:<4} CPU {cpu:7.3f} | GPU 계산만 {gpu:6.3f} | GPU 왕복 {왕복:6.3f} ms"
          f" → GPU가 {cpu / gpu:4.1f}배 / {cpu / 왕복:3.1f}배")
