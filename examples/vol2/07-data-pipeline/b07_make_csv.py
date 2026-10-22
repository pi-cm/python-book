# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.4 직접 만든 Dataset ①: CSV 파일 · manuscript-vol2/chapters/07-data-pipeline.md:306]
from pathlib import Path

import numpy as np
import pandas as pd

# 예제용으로 만든 귤 품질 데이터: 무게(g), 당도(브릭스), 껍질 두께(mm) → 등급
rng = np.random.default_rng(7)
등급들 = np.array(["하", "중", "상"])


def 귤_표_만들기(개수: int) -> pd.DataFrame:
    """등급을 먼저 정하고, 등급에 따라 조금씩 다른 측정값을 만든다."""
    등급번호 = rng.integers(0, 3, 개수)
    return pd.DataFrame({
        "무게": (rng.normal(80, 12, 개수) + 등급번호 * 8).round(1),
        "당도": (rng.normal(9.5, 1.0, 개수) + 등급번호 * 1.2).round(1),
        "껍질": (rng.normal(3.0, 0.4, 개수) - 등급번호 * 0.3).round(2),
        "등급": 등급들[등급번호],
    })


폴더 = Path("data/귤")
폴더.mkdir(parents=True, exist_ok=True)
귤_표_만들기(160).to_csv(폴더 / "학습.csv", index=False)
귤_표_만들기(40).to_csv(폴더 / "검증.csv", index=False)
print((폴더 / "학습.csv").read_text(encoding="utf-8").splitlines()[:4])
