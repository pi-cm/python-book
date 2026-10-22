# [2권 부록 B. 꼭 필요한 수학 직관 · B.7 평균·분산·표준편차와 표준화 · manuscript-vol2/appendix/B-math-intuition.md:601]
import torch

키_cm = torch.tensor([160.0, 170.0, 180.0, 175.0, 165.0])
몸무게_kg = torch.tensor([55.0, 65.0, 80.0, 72.0, 60.0])
표 = torch.stack([키_cm, 몸무게_kg], dim=1)        # (사람 5, 특성 2)

평균 = 표.mean(dim=0)
표준편차 = 표.std(dim=0)
표준화 = (표 - 평균) / 표준편차                    # 브로드캐스팅 (4장 4.6절)
print(표준화.round(decimals=3))
print("열 평균:", 표준화.mean(dim=0).round(decimals=3).tolist(),
      " 열 표준편차:", 표준화.std(dim=0).round(decimals=3).tolist())
