# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.11 배치 크기와 처리량 · manuscript-vol2/chapters/16-gpu-performance.md:1342]
import time

import torch
import torch.nn.functional as F
from torchvision.models import resnet18

GB = 1024 ** 3
torch.manual_seed(0)
모델 = resnet18(num_classes=10).to("cuda")
옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.01)

for 배치 in [8, 32, 128, 512]:
    x = torch.randn(배치, 3, 224, 224, device="cuda")
    y = torch.randint(0, 10, (배치,), device="cuda")
    torch.cuda.reset_peak_memory_stats()
    for 걸음 in range(13):
        if 걸음 == 3:                                   # 준비 운동 세 걸음 뒤부터 잰다
            torch.cuda.synchronize()
            시작 = time.perf_counter()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            손실 = F.cross_entropy(모델(x), y)
        옵티마이저.zero_grad(set_to_none=True)
        손실.backward()
        옵티마이저.step()
    torch.cuda.synchronize()
    ms = (time.perf_counter() - 시작) / 10 * 1000
    print(f"배치 {배치:>3}: 걸음당 {ms:6.1f} ms | 초당 사진 {배치 / ms * 1000:5.0f}장"
          f" | 최고 메모리 {torch.cuda.max_memory_allocated() / GB:5.2f} GB")
    del x, y, 손실
