# [2권 Chapter 8. 학습 잘 시키기 · 8.10 재현성 체크리스트 · manuscript-vol2/chapters/08-training-well.md:911]
import os
import random

import numpy as np
import torch
from torch.utils.data import random_split

from 학습도구 import 데이터_준비, 로더_만들기, 모델_만들기, 평가, 한_에폭_학습


def 씨앗_고정(씨앗: int = 42) -> None:
    """파이썬·NumPy·PyTorch의 난수 씨앗을 한꺼번에 고정한다."""
    random.seed(씨앗)
    np.random.seed(씨앗)
    torch.manual_seed(씨앗)                    # CPU와 모든 GPU의 씨앗
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"   # CUDA 행렬 곱 결정성용
    torch.use_deterministic_algorithms(True)   # 결정적이지 않은 연산은 오류로 알린다


def 한_번_학습(씨앗: int) -> float:
    씨앗_고정(씨앗)
    (X_학습, y_학습), (X_검증, y_검증), _ = 데이터_준비()
    로더 = 로더_만들기(X_학습, y_학습)
    모델 = 모델_만들기(드롭아웃=0.5)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    for 에폭 in range(30):
        한_에폭_학습(모델, 로더, 옵티마이저)
    return 평가(모델, X_검증, y_검증)[0]


print("씨앗 42, 첫 번째:", 한_번_학습(42))
print("씨앗 42, 두 번째:", 한_번_학습(42))
print("씨앗 7          :", 한_번_학습(7))

# 데이터 분할도 생성기로 고정한다
for 번 in (1, 2):
    _, 검증용 = random_split(range(10), [7, 3], generator=torch.Generator().manual_seed(0))
    print(f"{번}번째 분할의 검증용 번호:", list(검증용))
