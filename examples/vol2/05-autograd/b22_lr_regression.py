# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.10 학습률: 너무 크면 튀고, 너무 작으면 늦다 · manuscript-vol2/chapters/05-autograd.md:910]
import numpy as np
import torch

rng = np.random.default_rng(0)
기온 = rng.uniform(18, 34, size=30).round(1)
판매량 = (2.5 * 기온 - 15 + rng.normal(0, 4, size=30)).round()
x = torch.tensor((기온 - 기온.mean()) / 기온.std(), dtype=torch.float32)
y = torch.tensor(판매량, dtype=torch.float32)


def 학습(x: torch.Tensor, y: torch.Tensor, 학습률: float, 횟수: int) -> list[float]:
    """경사하강법을 돌리며 정해 둔 시점의 손실을 모은다."""
    w = torch.zeros((), requires_grad=True)
    b = torch.zeros((), requires_grad=True)
    기록 = []
    for 반복 in range(1, 횟수 + 1):
        손실 = ((w * x + b - y) ** 2).mean()
        손실.backward()
        with torch.no_grad():
            w -= 학습률 * w.grad
            b -= 학습률 * b.grad
            w.grad.zero_()
            b.grad.zero_()
        if 반복 in (10, 50, 200):
            기록.append(손실.item())
    return 기록


print("학습률       10번째      50번째     200번째")
for 학습률 in [0.001, 0.01, 0.1, 0.9, 1.05]:
    print(f"{학습률:<6}", " ".join(f"{v:11.6g}" for v in 학습(x, y, 학습률, 200)))
