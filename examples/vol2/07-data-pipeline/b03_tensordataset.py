# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.2 TensorDataset: 이미 텐서로 있을 때 · manuscript-vol2/chapters/07-data-pipeline.md:116]
import torch
from torch.utils.data import TensorDataset

torch.manual_seed(0)
X = torch.randn(6, 3)                    # 샘플 6개 × 특성 3개
y = torch.tensor([0, 1, 0, 1, 1, 0])     # 샘플마다 정답 하나

데이터 = TensorDataset(X, y)
print("샘플 수:", len(데이터))
x0, y0 = 데이터[0]                         # 0번 샘플: (특성 3개, 정답)
print(x0, y0)
특성들, 정답들 = 데이터[1:3]               # 슬라이스로 여러 개도 꺼낼 수 있다
print(특성들.shape, 정답들)

try:
    TensorDataset(X, torch.tensor([0, 1]))   # 샘플 수가 다르면?
except AssertionError as e:
    print("오류:", e)
