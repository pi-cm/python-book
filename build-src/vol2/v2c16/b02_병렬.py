import time

import torch


def 평균_시간(함수, 반복: int = 10) -> float:
    """준비 운동 한 번 뒤 여러 번 돌려, 한 번에 걸린 평균 시간(ms)을 잰다."""
    함수()
    torch.cuda.synchronize()                  # GPU 일이 끝날 때까지 기다린다 (16.2절)
    시작 = time.perf_counter()
    for _ in range(반복):
        함수()
    torch.cuda.synchronize()
    return (time.perf_counter() - 시작) / 반복 * 1000


def 작은_일_천_번(x: torch.Tensor) -> torch.Tensor:
    """앞의 결과가 있어야 다음을 할 수 있는 작은 계산을 1,000번."""
    for _ in range(1000):
        x = (x * 2 + 1).sqrt()
    return x


큰_cpu = torch.rand(100_000_000)              # 숫자 1억 개
큰_gpu = 큰_cpu.to("cuda")
작은_cpu = torch.rand(10)                     # 숫자 10개
작은_gpu = 작은_cpu.to("cuda")

print(f"큰 일 한 번   (1억 개)   CPU {평균_시간(lambda: (큰_cpu * 2 + 1).sqrt()):7.2f} ms"
      f" | GPU {평균_시간(lambda: (큰_gpu * 2 + 1).sqrt()):7.2f} ms")
print(f"작은 일 천 번 (10개씩)   CPU {평균_시간(lambda: 작은_일_천_번(작은_cpu)):7.2f} ms"
      f" | GPU {평균_시간(lambda: 작은_일_천_번(작은_gpu)):7.2f} ms")
