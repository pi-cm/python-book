# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.3 DataLoader: 배치로 묶어 나르기 · manuscript-vol2/chapters/07-data-pipeline.md:156]
import torch
from torch.utils.data import DataLoader, TensorDataset

X = torch.arange(10).float().unsqueeze(1) * 10   # 샘플 10개 × 특성 1개: 0, 10, ..., 90
y = torch.arange(10)                             # 정답은 샘플 번호와 같게
데이터 = TensorDataset(X, y)

로더 = DataLoader(데이터, batch_size=4)
print("배치 수:", len(로더))
for xb, yb in 로더:
    print(tuple(xb.shape), yb.tolist())

버리는_로더 = DataLoader(데이터, batch_size=4, drop_last=True)
print("drop_last=True 배치 수:", len(버리는_로더))

g = torch.Generator().manual_seed(0)             # 섞는 순서도 씨앗으로 고정
섞는_로더 = DataLoader(데이터, batch_size=4, shuffle=True, generator=g)
for 에폭 in range(2):
    print(f"에폭 {에폭}:", [yb.tolist() for _, yb in 섞는_로더])
