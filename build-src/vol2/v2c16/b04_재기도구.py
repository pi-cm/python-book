import statistics
import time

import torch
from torch.utils import benchmark


def 재기(함수, 반복: int = 50, 준비: int = 5) -> float:
    """준비 운동 뒤 한 번씩 동기화하며 재고, 중앙값(ms)을 돌려준다."""
    for _ in range(준비):
        함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


n = 4096
a = torch.randn(n, n, device="cuda")
b = torch.randn(n, n, device="cuda")

직접 = 재기(lambda: a @ b)
타이머 = benchmark.Timer(stmt="a @ b", globals={"a": a, "b": b})
측정 = 타이머.blocked_autorange(min_run_time=1.0)   # 1초 이상 알아서 반복해 잰다

print(f"직접 만든 재기()   : 중앙값 {직접:.3f} ms")
print(f"benchmark.Timer    : 중앙값 {측정.median * 1000:.3f} ms ({측정.number_per_run}번씩 {len(측정.times)}묶음)")
연산수 = 2 * n ** 3                                 # 곱하기와 더하기 각각 n³번
print(f"초당 {연산수 / (직접 / 1000) / 1e12:.1f}조 번 계산 (TFLOPS)")
