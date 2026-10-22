# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.10 실습: 통신사 고객 이탈 데이터 손질하기 · manuscript-vol2/chapters/02-data-preparation.md:1035]
import os
from pathlib import Path

import numpy as np
import pandas as pd

데이터_폴더 = Path(os.environ.get("BOOK_DATA_DIR", "data"))
데이터_폴더.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(2025)
n = 3000
요금제 = rng.choice(["베이직", "스탠다드", "프리미엄"], n, p=[0.5, 0.35, 0.15])
약정 = rng.choice(["무약정", "1년", "2년"], n, p=[0.45, 0.35, 0.2])
기본료 = pd.Series(요금제).map({"베이직": 33000, "스탠다드": 55000, "프리미엄": 89000})
고객 = pd.DataFrame({
    "고객번호": np.arange(1, n + 1),
    "나이": rng.integers(19, 75, n).astype(float),
    "지역": rng.choice(["서울", "경기", "부산", "대구", "광주", "대전"], n,
                      p=[0.3, 0.3, 0.15, 0.1, 0.08, 0.07]),
    "요금제": 요금제,
    "약정": 약정,
    "가입개월": rng.integers(1, 73, n),
    "월요금": (기본료 + rng.normal(0, 5000, n)).round(-2),
    "상담횟수": rng.poisson(1.0, n),
})
# 이탈 확률: 무약정·짧은 가입·잦은 상담·젊은 나이일수록 높다고 정한다
점수 = (-2.6 + 1.1 * (약정 == "무약정") - 0.8 * (약정 == "2년")
        - 0.025 * 고객["가입개월"] + 0.55 * 고객["상담횟수"]
        - 0.015 * (고객["나이"] - 45) + 0.000015 * (고객["월요금"] - 50000))
고객["이탈"] = (rng.random(n) < 1 / (1 + np.exp(-점수))).astype(int)

# 실제 데이터처럼 지저분하게: 빈칸, 입력 실수, 표기 흔들림, 중복 행
고객.loc[rng.random(n) < 0.07, "나이"] = np.nan
고객.loc[rng.random(n) < 0.01, "나이"] = 999
고객.loc[rng.random(n) < 0.05, "월요금"] = np.nan
고객.loc[rng.random(n) < 0.04, "지역"] = np.nan
흔들림 = rng.random(n) < 0.03
고객.loc[흔들림, "지역"] = 고객.loc[흔들림, "지역"] + rng.choice(["시", " "], 흔들림.sum())
고객 = pd.concat([고객, 고객.sample(25, random_state=0)]).reset_index(drop=True)

고객.to_csv(데이터_폴더 / "통신사_고객.csv", index=False)
print("저장:", 고객.shape)
print(고객.head(3).to_string())
