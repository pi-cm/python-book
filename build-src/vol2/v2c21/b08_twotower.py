import numpy as np
import pandas as pd
import torch

from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 순위지표 import 평가셋_만들기, 평가하기
from 추천학습 import 내적추천, 행렬분해, 학습설정, 학습하기, 좋았던_쌍
from 투타워 import 투타워

데이터 = 데이터_만들기(씨앗=0)
학습, 검증, 시험 = 시간으로_나누기(데이터.방문)
검증셋 = 평가셋_만들기(학습, 검증, 데이터.식당)
시험셋 = 평가셋_만들기(pd.concat([학습, 검증]), 시험, 데이터.식당)
쌍 = 좋았던_쌍(학습)
후보_식당 = torch.tensor(np.flatnonzero(데이터.식당["개업일"] < 300))


def 점수표(모델: 내적추천, 사용자: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        return 모델.모든_점수(torch.tensor(사용자)).numpy()


모델들 = {"행렬 분해": lambda: 행렬분해(len(데이터.사용자), len(데이터.식당)),
        "투-타워": lambda: 투타워(데이터.사용자, 데이터.식당)}
for 이름, 만들기 in 모델들.items():
    torch.manual_seed(0)
    모델 = 만들기()
    기록 = 학습하기(모델, 쌍, 후보_식당, 학습설정(손실="bpr", 에폭=60),
                 lambda m: 평가하기(점수표(m, 검증셋.사용자), 검증셋)["NDCG@10"])
    최고 = max(기록, key=lambda 줄: 줄["검증"])
    결과 = 평가하기(점수표(모델, 시험셋.사용자), 시험셋)
    print(f"{이름}: 파라미터 {sum(p.numel() for p in 모델.parameters()):,}개, "
          f"검증 곡선 {[round(기록[i]['검증'], 3) for i in (0, 9, 19, 39, 59)]}")
    print(f"   가장 좋던 에폭 {최고['에폭']} → 시험 Recall@10 {결과['Recall@10']:.4f}, "
          f"NDCG@10 {결과['NDCG@10']:.4f}")
