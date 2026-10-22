# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.10 학습률: 너무 크면 튀고, 너무 작으면 늦다 · manuscript-vol2/chapters/05-autograd.md:961]
import numpy as np
import torch

rng = np.random.default_rng(0)
기온 = rng.uniform(18, 34, size=30).round(1)
판매량 = (2.5 * 기온 - 15 + rng.normal(0, 4, size=30)).round()
x_원래 = torch.tensor(기온, dtype=torch.float32)          # 표준화하지 않은 18~34
y = torch.tensor(판매량, dtype=torch.float32)

for 학습률 in [0.01, 0.001]:
    w = torch.zeros((), requires_grad=True)
    b = torch.zeros((), requires_grad=True)
    for 반복 in range(1, 5001):
        손실 = ((w * x_원래 + b - y) ** 2).mean()
        손실.backward()
        with torch.no_grad():
            w -= 학습률 * w.grad
            b -= 학습률 * b.grad
            w.grad.zero_()
            b.grad.zero_()
        if 반복 in (5, 100, 5000):
            print(f"학습률 {학습률}, {반복:4}번째: 손실 {손실.item():.4g}, w = {w.item():.3f}, b = {b.item():.3f}")

정답_w, 정답_b = np.polyfit(기온, 판매량, deg=1)
print(f"정답: w = {정답_w:.3f}, b = {정답_b:.3f}")
