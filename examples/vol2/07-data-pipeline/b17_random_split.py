# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.8 학습/검증 나누기: random_split과 재현 가능한 분할 · manuscript-vol2/chapters/07-data-pipeline.md:913]
import torch
from torch.utils.data import TensorDataset, random_split

데이터 = TensorDataset(torch.arange(100).float(), torch.arange(100))   # 샘플 100개 (예제용)

학습, 검증 = random_split(데이터, [0.8, 0.2], generator=torch.Generator().manual_seed(42))
print("크기:", len(학습), len(검증), type(학습).__name__)
print("검증에 뽑힌 번호(앞 8개):", 검증.indices[:8])
print("검증 2번 샘플:", 검증[2], "= 원래 데이터의", 검증.indices[2], "번")

다시_학습, 다시_검증 = random_split(데이터, [0.8, 0.2], generator=torch.Generator().manual_seed(42))
print("같은 씨앗이면 같은 분할:", 검증.indices == 다시_검증.indices)
print("학습과 검증이 겹치나:", bool(set(학습.indices) & set(검증.indices)))

학, 검, 시 = random_split(데이터, [70, 15, 15], generator=torch.Generator().manual_seed(42))
print("세 갈래:", len(학), len(검), len(시))
