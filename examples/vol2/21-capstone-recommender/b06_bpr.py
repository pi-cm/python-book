# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.6 순위를 직접 배우기: BPR · manuscript-vol2/chapters/21-capstone-recommender.md:620]
import numpy as np
import pandas as pd
import torch

from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 순위지표 import 평가셋_만들기, 평가하기
from 추천학습 import 행렬분해, 학습설정, 학습하기, 좋았던_쌍

데이터 = 데이터_만들기(씨앗=0)
학습, 검증, 시험 = 시간으로_나누기(데이터.방문)
검증셋 = 평가셋_만들기(학습, 검증, 데이터.식당)
시험셋 = 평가셋_만들기(pd.concat([학습, 검증]), 시험, 데이터.식당)
쌍 = 좋았던_쌍(학습)
후보_식당 = torch.tensor(np.flatnonzero(데이터.식당["개업일"] < 300))


def 점수표(모델: 행렬분해, 사용자: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        return 모델.모든_점수(torch.tensor(사용자)).numpy()


기록들, 시험_결과 = {}, {}
for 손실 in ["bce", "bpr"]:
    torch.manual_seed(0)
    모델 = 행렬분해(len(데이터.사용자), len(데이터.식당), 차원=32)
    기록들[손실] = 학습하기(모델, 쌍, 후보_식당, 학습설정(손실=손실),
                       lambda m: 평가하기(점수표(m, 검증셋.사용자), 검증셋)["NDCG@10"])
    시험_결과[손실] = 평가하기(점수표(모델, 시험셋.사용자), 시험셋)

print("에폭   BCE 검증 NDCG   BPR 검증 NDCG")
for 에폭 in [1, 5, 10, 20, 30, 40, 50]:
    print(f"{에폭:4} {기록들['bce'][에폭 - 1]['검증']:15.4f} {기록들['bpr'][에폭 - 1]['검증']:15.4f}")
for 손실, 결과 in 시험_결과.items():
    print(f"{손실.upper()} 시험: Recall@10 {결과['Recall@10']:.4f}, NDCG@10 {결과['NDCG@10']:.4f}")
