# [2권 부록 B. 꼭 필요한 수학 직관 · B.6 교차 엔트로피: 정답 확률에 매기는 벌점 · manuscript-vol2/appendix/B-math-intuition.md:528]
import math

import torch
import torch.nn.functional as F

로짓 = torch.tensor([[2.0, 1.0, 0.1],
                    [0.5, 2.5, 0.3]])     # 샘플 2개, 클래스 3개
정답 = torch.tensor([0, 2])               # 두 번째 샘플은 확률이 낮은 칸이 정답

확률 = torch.softmax(로짓, dim=1)
정답_확률 = 확률[torch.arange(2), 정답]
print("정답 칸의 확률:", [f"{p:.4f}" for p in 정답_확률.tolist()])
print("-log 평균     :", round((-torch.log(정답_확률)).mean().item(), 4))
print("F.cross_entropy:", round(F.cross_entropy(로짓, 정답).item(), 4))
print("클래스 10개를 찍을 때 손실 -log(1/10):", round(-math.log(1 / 10), 4))
