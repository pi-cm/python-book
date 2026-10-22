import numpy as np
import torch

from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 순위지표 import 평가셋_만들기, 평가하기
from 추천학습 import 행렬분해, 학습설정, 학습하기, 좋았던_쌍

데이터 = 데이터_만들기(씨앗=0)
학습, 검증, 시험 = 시간으로_나누기(데이터.방문)
검증셋 = 평가셋_만들기(학습, 검증, 데이터.식당)

쌍 = 좋았던_쌍(학습)                                             # (사용자, 식당) 짝
후보_식당 = torch.tensor(np.flatnonzero(데이터.식당["개업일"] < 300))  # 음성으로 뽑을 식당
print("좋았던 짝:", tuple(쌍.shape), "음성 후보:", len(후보_식당), "곳")

torch.manual_seed(0)
모델 = 행렬분해(len(데이터.사용자), len(데이터.식당), 차원=32)
print("파라미터:", f"{sum(p.numel() for p in 모델.parameters()):,}개")


def 검증_NDCG(모델: 행렬분해) -> float:
    with torch.no_grad():
        점수 = 모델.모든_점수(torch.tensor(검증셋.사용자)).numpy()
    return 평가하기(점수, 검증셋)["NDCG@10"]


기록 = 학습하기(모델, 쌍, 후보_식당, 학습설정(손실="bce"), 검증_NDCG)
for 줄 in [기록[0]] + 기록[9::10]:
    print(f"에폭 {줄['에폭']:2}: 손실 {줄['손실']:.4f}, 검증 NDCG@10 {줄['검증']:.4f}")
최고 = max(기록, key=lambda 줄: 줄["검증"])
print(f"가장 좋았던 에폭 {최고['에폭']}: 검증 NDCG@10 {최고['검증']:.4f}")
