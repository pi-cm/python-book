# [2권 부록 B. 꼭 필요한 수학 직관 · B.5 확률과 소프트맥스 · manuscript-vol2/appendix/B-math-intuition.md:476]
import torch

로짓 = torch.tensor([2.0, 1.0, 0.1])
for 온도 in [0.5, 1.0, 2.0]:
    print(f"온도 {온도}:", [f"{p:.3f}" for p in torch.softmax(로짓 / 온도, dim=0).tolist()])
