import time

import torch

GB = 1024 ** 3
일반 = torch.randn(64, 1024, 1024)                 # 256MB, 보통의 CPU 메모리
고정 = 일반.pin_memory()                           # 같은 내용을 고정(pinned) 메모리에
gpu_텐서 = 일반.to("cuda")
고정_받을_곳 = torch.empty_like(일반).pin_memory()  # GPU에서 받아 올 고정 메모리 자리


def 초당_GB(옮기기, 반복: int = 10) -> float:
    """옮기기를 여러 번 해 보고 초당 몇 GB를 옮겼는지 잰다."""
    옮기기()
    torch.cuda.synchronize()
    시작 = time.perf_counter()
    for _ in range(반복):
        옮기기()
    torch.cuda.synchronize()
    return 일반.numel() * 일반.element_size() * 반복 / (time.perf_counter() - 시작) / GB


print(f"CPU(일반) → GPU: {초당_GB(lambda: 일반.to('cuda')):5.1f} GB/s")
print(f"CPU(고정) → GPU: {초당_GB(lambda: 고정.to('cuda')):5.1f} GB/s")
print(f"GPU → CPU(일반): {초당_GB(lambda: gpu_텐서.to('cpu')):5.1f} GB/s")
print(f"GPU → CPU(고정): {초당_GB(lambda: 고정_받을_곳.copy_(gpu_텐서)):5.1f} GB/s")

# non_blocking=True: 옮기라고 맡기고 기다리지 않고 바로 다음 줄로 간다
for 이름, 원본 in [("일반", 일반), ("고정", 고정)]:
    torch.cuda.synchronize()
    시작 = time.perf_counter()
    도착 = 원본.to("cuda", non_blocking=True)
    맡긴_시간 = (time.perf_counter() - 시작) * 1000
    torch.cuda.synchronize()
    끝난_시간 = (time.perf_counter() - 시작) * 1000
    print(f"{이름} 메모리 + non_blocking: 맡기고 돌아오기까지 {맡긴_시간:6.2f} ms, "
          f"다 옮기기까지 {끝난_시간:6.2f} ms")
