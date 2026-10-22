# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.8 장치: CPU와 GPU 사이 옮기기 · manuscript-vol2/chapters/04-tensors.md:1096]
import time
import torch

크기 = 4096
a = torch.randn(크기, 크기)
b = torch.randn(크기, 크기)

시작 = time.perf_counter()
a @ b
print(f"CPU: {time.perf_counter() - 시작:.3f}초")

if torch.backends.mps.is_available():
    ga, gb = a.to("mps"), b.to("mps")
    ga @ gb                              # 처음 한 번은 준비 운동
    torch.mps.synchronize()
    시작 = time.perf_counter()
    ga @ gb
    torch.mps.synchronize()              # GPU 일이 끝날 때까지 기다린 뒤 잰다
    print(f"MPS: {time.perf_counter() - 시작:.3f}초")
