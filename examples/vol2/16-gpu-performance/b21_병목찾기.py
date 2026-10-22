# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.10 프로파일러로 시간 새는 곳 찾기 · manuscript-vol2/chapters/16-gpu-performance.md:1270]
import os
import time

import torch
import torch.nn.functional as F
from torch import nn
from torch.autograd import DeviceType
from torch.profiler import ProfilerActivity, profile
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import v2

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")


def 작은_CNN() -> nn.Sequential:
    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Linear(64 * 7 * 7, 10))


def 재기(일꾼: int, 걸음_수: int = 100) -> tuple[float, float]:
    """걸음_수만큼 학습하며 (벽시계 시간, 그동안 GPU가 실제로 일한 시간)을 초로 잰다."""
    증강 = v2.Compose([v2.ToImage(), v2.RandomCrop(28, padding=2), v2.RandomHorizontalFlip(),
                       v2.ToDtype(torch.float32, scale=True)])
    데이터 = datasets.FashionMNIST(데이터_폴더, train=True, download=True, transform=증강)
    로더 = DataLoader(데이터, batch_size=256, shuffle=True, num_workers=일꾼,
                      pin_memory=True, persistent_workers=일꾼 > 0)
    모델 = 작은_CNN().to("cuda")
    옵티마이저 = torch.optim.Adam(모델.parameters())
    반복자 = iter(로더)
    next(반복자)                                         # 일꾼을 띄우는 시간은 빼고 잰다
    with profile(activities=[ProfilerActivity.CUDA]) as 기록:
        시작 = time.perf_counter()
        for _ in range(걸음_수):
            x, y = next(반복자)
            x, y = x.to("cuda", non_blocking=True), y.to("cuda", non_blocking=True)
            손실 = F.cross_entropy(모델(x), y)
            옵티마이저.zero_grad(set_to_none=True)
            손실.backward()
            옵티마이저.step()
        torch.cuda.synchronize()
        전체 = time.perf_counter() - 시작
    GPU_시간 = sum(e.self_device_time_total for e in 기록.key_averages()
                  if e.device_type == DeviceType.CUDA) / 1e6        # GPU에서 실제로 돈 시간
    return 전체, GPU_시간


if __name__ == "__main__":
    for 일꾼 in [0, 8]:
        전체, GPU = 재기(일꾼)
        print(f"num_workers={일꾼}: 100걸음 {전체:5.2f}초, GPU가 일한 시간 {GPU:4.2f}초 "
              f"→ GPU 사용률 {GPU / 전체:5.1%}")
