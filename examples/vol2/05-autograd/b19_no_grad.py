# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.8 기록 끄기: no_grad, detach, inference_mode · manuscript-vol2/chapters/05-autograd.md:777]
import torch

w = torch.tensor([1.0, 2.0], requires_grad=True)

with torch.no_grad():                        # 이 안의 계산은 기록하지 않는다
    a = w * 2
print("no_grad       :", a.requires_grad, a.grad_fn)

with torch.inference_mode():                 # 예측만 할 때: no_grad보다 더 가볍다
    b = w * 2
print("inference_mode:", b.requires_grad, "/ 추론 전용 텐서인가?", b.is_inference())

c = w.detach()                               # 기록에서 떼어 낸 '창'(4.4절)
print("detach        :", c.requires_grad, "/ 메모리 공유:", c.data_ptr() == w.data_ptr())
c[0] = 100.0                                 # 떼어 낸 쪽을 바꾸면?
print("w도 바뀌었다  :", w)

try:
    w.numpy()
except RuntimeError as e:
    print("오류:", e)
print("detach 후 numpy:", w.detach().numpy())
