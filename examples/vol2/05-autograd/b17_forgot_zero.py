# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.7 기울기가 쌓이는 함정과 zero_grad · manuscript-vol2/chapters/05-autograd.md:686]
import numpy as np
import torch

rng = np.random.default_rng(0)
기온 = rng.uniform(18, 34, size=30).round(1)
판매량 = (2.5 * 기온 - 15 + rng.normal(0, 4, size=30)).round()
x = torch.tensor((기온 - 기온.mean()) / 기온.std(), dtype=torch.float32)
y = torch.tensor(판매량, dtype=torch.float32)


def 학습(비우기: bool) -> list[float]:
    w = torch.zeros((), requires_grad=True)
    b = torch.zeros((), requires_grad=True)
    기록 = []
    for _ in range(30):
        손실 = ((w * x + b - y) ** 2).mean()
        손실.backward()
        with torch.no_grad():                  # 값 고치기는 기록하지 않는다(5.8절)
            w -= 0.1 * w.grad
            b -= 0.1 * b.grad
        if 비우기:
            w.grad.zero_()
            b.grad.zero_()
        기록.append(손실.item())
    return 기록


for 비우기 in (True, False):
    기록 = 학습(비우기)
    print(f"grad 비우기={비우기!s:5}:", [round(v, 1) for v in 기록[::5]], "→", round(기록[-1], 1))
