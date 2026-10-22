# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.4 직접 만든 Dataset ①: CSV 파일 · manuscript-vol2/chapters/07-data-pipeline.md:345]
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset

# 7.4절 앞 블록과 같은 예제용 귤 데이터를 만든다(이미 있으면 그대로 쓴다)
폴더 = Path("data/귤")
if not (폴더 / "학습.csv").exists():
    rng = np.random.default_rng(7)
    폴더.mkdir(parents=True, exist_ok=True)
    for 이름, 개수 in [("학습", 160), ("검증", 40)]:
        n = rng.integers(0, 3, 개수)
        pd.DataFrame({"무게": (rng.normal(80, 12, 개수) + n * 8).round(1),
                      "당도": (rng.normal(9.5, 1.0, 개수) + n * 1.2).round(1),
                      "껍질": (rng.normal(3.0, 0.4, 개수) - n * 0.3).round(2),
                      "등급": np.array(["하", "중", "상"])[n]}
                     ).to_csv(폴더 / f"{이름}.csv", index=False)


class 귤_데이터셋(Dataset):
    """CSV 한 파일을 읽어 (특성 3개, 등급 번호)를 돌려준다."""

    특성_열 = ["무게", "당도", "껍질"]
    등급_번호 = {"하": 0, "중": 1, "상": 2}

    def __init__(self, 경로: Path, 평균: torch.Tensor | None = None,
                 표준편차: torch.Tensor | None = None) -> None:
        표 = pd.read_csv(경로)
        self.X = torch.tensor(표[self.특성_열].to_numpy(), dtype=torch.float32)
        self.y = torch.tensor(표["등급"].map(self.등급_번호).to_numpy())
        # 기준값을 받지 않았으면 이 파일에서 구한다(학습용일 때만 그래야 한다)
        self.평균 = self.X.mean(dim=0) if 평균 is None else 평균
        self.표준편차 = self.X.std(dim=0) if 표준편차 is None else 표준편차

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, torch.Tensor]:
        x = (self.X[i] - self.평균) / self.표준편차   # 꺼낼 때 표준화
        return x, self.y[i]


학습 = 귤_데이터셋(폴더 / "학습.csv")
검증 = 귤_데이터셋(폴더 / "검증.csv", 학습.평균, 학습.표준편차)  # 학습 기준을 그대로 넘긴다
print("샘플 수:", len(학습), len(검증))
print("학습 기준 평균:", 학습.평균)
x, y = 학습[0]
print("0번 샘플:", x, y)
xb, yb = next(iter(DataLoader(학습, batch_size=8)))
print("배치 모양:", tuple(xb.shape), tuple(yb.shape), yb.dtype)
print("등급별 개수:", torch.bincount(학습.y).tolist())
