# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.10 실습: 통신사 고객 이탈 데이터 손질하기 · manuscript-vol2/chapters/02-data-preparation.md:1097]
import os
from pathlib import Path

import numpy as np
import pandas as pd

데이터_폴더 = Path(os.environ.get("BOOK_DATA_DIR", "data"))
고객 = pd.read_csv(데이터_폴더 / "통신사_고객.csv")

print("1. 모양:", 고객.shape)
print("2. 빈칸:", {열: int(개수) for 열, 개수 in 고객.isna().sum().items() if 개수})
print("3. 중복 행:", int(고객.duplicated().sum()))
print("4. 지역 값:", sorted(고객["지역"].dropna().unique()))
print("5. 나이 범위:", 고객["나이"].min(), "~", 고객["나이"].max(),
      "/ 100살 넘는 사람:", int((고객["나이"] > 100).sum()))
print(f"6. 이탈 비율: {고객['이탈'].mean():.1%}")


def 정리하기(표: pd.DataFrame) -> pd.DataFrame:
    """행 하나만 보고 고칠 수 있는 문제를 고친다 (통계를 쓰지 않으므로 나누기 전에 해도 안전)."""
    표 = 표.drop_duplicates().copy()
    표["지역"] = 표["지역"].str.strip().str.removesuffix("시")
    표.loc[표["나이"] > 100, "나이"] = np.nan
    return 표


정리 = 정리하기(고객)
print("정리 후:", 정리.shape, sorted(정리["지역"].dropna().unique()),
      "나이 최대", 정리["나이"].max())
