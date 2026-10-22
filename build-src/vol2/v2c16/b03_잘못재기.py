import time

import torch

a = torch.randn(8192, 8192, device="cuda")
b = torch.randn(8192, 8192, device="cuda")

시작 = time.perf_counter()
c = a @ b                                     # 이 크기의 행렬 곱은 처음
torch.cuda.synchronize()
print(f"① 첫 호출 (준비 포함)   : {(time.perf_counter() - 시작) * 1000:8.2f} ms")

시작 = time.perf_counter()
c = a @ b
print(f"② 기다리지 않고 잼      : {(time.perf_counter() - 시작) * 1000:8.2f} ms")
torch.cuda.synchronize()

시작 = time.perf_counter()
c = a @ b
torch.cuda.synchronize()                      # GPU가 다 끝낼 때까지 기다린 뒤 잰다
print(f"③ synchronize 후 잼     : {(time.perf_counter() - 시작) * 1000:8.2f} ms")

# ④ CUDA 이벤트: GPU의 작업 줄에 시작·끝 표시를 끼워 넣는다
시작_표시 = torch.cuda.Event(enable_timing=True)
끝_표시 = torch.cuda.Event(enable_timing=True)
시작_표시.record()
c = a @ b
끝_표시.record()
끝_표시.synchronize()                         # 끝 표시까지 지나갈 때까지 기다린다
print(f"④ CUDA 이벤트           : {시작_표시.elapsed_time(끝_표시):8.2f} ms")

# ⑤ 결과를 CPU로 꺼내는 순간(.item(), print, .cpu()) 저절로 기다리게 된다
시작 = time.perf_counter()
c = a @ b
합계 = c.sum().item()
print(f"⑤ .item()까지 잼        : {(time.perf_counter() - 시작) * 1000:8.2f} ms")
