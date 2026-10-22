# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.8 기록 끄기: no_grad, detach, inference_mode · manuscript-vol2/chapters/05-autograd.md:741]
import torch

w = torch.tensor(2.0, requires_grad=True)
손실 = (w * 3.0 - 10.0) ** 2
손실.backward()

try:
    w -= 0.01 * w.grad                     # 기록을 켠 채로 잎 텐서를 고치면?
except RuntimeError as e:
    print("오류:", e)

w2 = w - 0.01 * w.grad                     # 새 텐서를 만들면 오류는 없지만...
print("w2:", w2, "/ 잎인가?", w2.is_leaf)

with torch.no_grad():                      # 올바른 방법
    w -= 0.01 * w.grad
print("w:", w, "/ 잎인가?", w.is_leaf)
