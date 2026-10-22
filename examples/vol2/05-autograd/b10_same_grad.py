# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.4 PyTorch에게 미분 맡기기 · manuscript-vol2/chapters/05-autograd.md:400]
import numpy as np
import torch

rng = np.random.default_rng(0)
기온 = rng.uniform(18, 34, size=30).round(1)
판매량 = (2.5 * 기온 - 15 + rng.normal(0, 4, size=30)).round()
x_np = (기온 - 기온.mean()) / 기온.std()
y_np = 판매량

# 손으로 구한 기울기 (NumPy, w=0, b=0에서)
오차 = 0.0 * x_np + 0.0 - y_np
손_w, 손_b = (2 * 오차 * x_np).mean(), (2 * 오차).mean()

# PyTorch에게 맡긴 기울기
x = torch.from_numpy(x_np)                   # float64 그대로 (4.1절)
y = torch.from_numpy(y_np)
w = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
b = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
손실 = ((w * x + b - y) ** 2).mean()
손실.backward()

print(f"손으로  : w 기울기 {손_w:.10f}, b 기울기 {손_b:.10f}")
print(f"PyTorch : w 기울기 {w.grad.item():.10f}, b 기울기 {b.grad.item():.10f}")
print("같은가?", torch.allclose(w.grad, torch.tensor(손_w, dtype=torch.float64)),
      torch.allclose(b.grad, torch.tensor(손_b, dtype=torch.float64)))
