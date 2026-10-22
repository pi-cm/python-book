# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.4 기준선부터: 인기순과 동네 인기순 · manuscript-vol2/chapters/21-capstone-recommender.md:386]
import numpy as np
import pandas as pd

from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 순위지표 import 평가셋_만들기, 평가하기

데이터 = 데이터_만들기(씨앗=0)
학습, 검증, 시험 = 시간으로_나누기(데이터.방문)
셋들 = {"검증": 평가셋_만들기(학습, 검증, 데이터.식당),
       "시험": 평가셋_만들기(pd.concat([학습, 검증]), 시험, 데이터.식당)}
식당_지역 = 데이터.식당["지역"].to_numpy()
사용자_동네 = 데이터.사용자["동네"].to_numpy()


def 기준선_점수(이름: str, 이전: pd.DataFrame, 사용자: np.ndarray) -> np.ndarray:
    """(사용자 수, 식당 수) 점수표. 클수록 위에 추천한다."""
    인기 = np.bincount(이전["식당"], minlength=len(식당_지역)).astype(float)
    if 이름 == "무작위":
        return np.random.default_rng(0).random((len(사용자), len(식당_지역)))
    if 이름 == "최근 30일 인기순":
        최근 = 이전[이전["날짜"] >= 이전["날짜"].max() - 29]
        인기 = np.bincount(최근["식당"], minlength=len(식당_지역)).astype(float)
    점수 = np.tile(인기, (len(사용자), 1))
    if 이름 == "동네 인기순":            # 내 동네 식당을 먼저, 그 안에서는 인기순
        점수 += 1e6 * (식당_지역[None, :] == 사용자_동네[사용자][:, None])
    return 점수


print("검증 Recall@10  NDCG@10 | 시험 Recall@10  NDCG@10 | 방법")
for 이름 in ["무작위", "인기순", "최근 30일 인기순", "동네 인기순"]:
    칸 = []
    for 셋_이름, 셋 in 셋들.items():
        이전 = 학습 if 셋_이름 == "검증" else pd.concat([학습, 검증])
        결과 = 평가하기(기준선_점수(이름, 이전, 셋.사용자), 셋)
        칸.append(f"{결과['Recall@10']:14.4f} {결과['NDCG@10']:8.4f}")
    print(" | ".join(칸), "|", 이름)
