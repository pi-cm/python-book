# [2권 Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기 · 17.2 그래디언트 누적: 큰 배치를 나눠 담기 · manuscript-vol2/chapters/17-distributed-training.md:218]
import statistics
import time

import torch
from torch import nn
from torchvision.models import resnet18

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 있어야 합니다"
장치 = torch.device("cuda")
GB = 1024 ** 3

torch.manual_seed(0)
모델 = resnet18(num_classes=10).to(장치)
옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.01, momentum=0.9)
손실함수 = nn.CrossEntropyLoss()
X = torch.randn(256, 3, 224, 224, device=장치)   # 예제용 입력: 224×224 사진 256장
y = torch.randint(0, 10, (256,), device=장치)


def 한_걸음(단계: int) -> None:
    """256장을 단계 수만큼 나눠 기울기를 누적한 뒤 한 번 고친다."""
    옵티마이저.zero_grad()
    for xb, yb in zip(X.chunk(단계), y.chunk(단계)):
        (손실함수(모델(xb), yb) / 단계).backward()
    옵티마이저.step()


for 단계 in (1, 2, 4, 8, 16):
    한_걸음(단계)                                 # 준비 운동
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    시간들 = []
    for _ in range(5):
        시작 = time.perf_counter()
        한_걸음(단계)
        torch.cuda.synchronize()                  # GPU 일이 끝날 때까지 기다린 뒤 잰다
        시간들.append(time.perf_counter() - 시작)
    print(f"{256 // 단계:3}장 × {단계:2}번: 최고 메모리 {torch.cuda.max_memory_allocated() / GB:5.2f} GB, "
          f"256장 한 걸음 {statistics.median(시간들) * 1000:5.0f} ms")
