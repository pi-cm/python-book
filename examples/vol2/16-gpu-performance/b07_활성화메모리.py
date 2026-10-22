# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.4 GPU 메모리 들여다보기 · manuscript-vol2/chapters/16-gpu-performance.md:358]
import torch
import torch.nn.functional as F
from torchvision.models import resnet18

MB = 1024 ** 2
모델 = resnet18(num_classes=10).to("cuda")
개수 = sum(p.numel() for p in 모델.parameters())
print(f"파라미터 {개수:,}개 × 4바이트 = {개수 * 4 / MB:.1f} MB (14장 14.6절의 계산)")
print(f"모델을 올린 뒤 실제 할당   = {torch.cuda.memory_allocated() / MB:.1f} MB")

for 배치 in [16, 32, 64, 128]:
    x = torch.randn(배치, 3, 224, 224, device="cuda")
    y = torch.randint(0, 10, (배치,), device="cuda")
    전 = torch.cuda.memory_allocated()
    torch.cuda.reset_peak_memory_stats()             # 최고 기록을 지금부터 다시 잰다
    손실 = F.cross_entropy(모델(x), y)
    순전파_뒤 = torch.cuda.memory_allocated()       # backward를 위해 기억해 둔 중간값(활성화)
    손실.backward()
    최고 = torch.cuda.max_memory_allocated()
    모델.zero_grad(set_to_none=True)
    print(f"배치 {배치:>3}: 순전파가 남긴 것 {(순전파_뒤 - 전) / MB:7.1f} MB, "
          f"이 걸음의 최고 {최고 / MB:7.1f} MB")
    del x, y, 손실
