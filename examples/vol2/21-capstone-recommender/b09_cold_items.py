# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.9 콜드 스타트: 처음 보는 식당과 사용자 · manuscript-vol2/chapters/21-capstone-recommender.md:924]
import numpy as np
import pandas as pd
import torch

from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 순위지표 import 좋은_평점, ndcg_at_k, recall_at_k
from 추천학습 import 행렬분해, 학습설정, 학습하기, 좋았던_쌍
from 투타워 import 투타워

데이터 = 데이터_만들기(씨앗=0)
식당, 사용자 = 데이터.식당, 데이터.사용자
학습, 검증, 시험 = 시간으로_나누기(데이터.방문)
쌍, 후보_식당 = 좋았던_쌍(학습), torch.tensor(np.flatnonzero(식당["개업일"] < 300))
새_식당 = np.flatnonzero(식당["개업일"] >= 300)              # 학습 기간 뒤에 문을 연 40곳

# 문제: 학습 기록이 있는 사용자가 시험 기간에 '새 식당'에 처음 가서 좋았다. 새 식당 40곳 중에서 맞히기
가본_곳 = pd.concat([학습, 검증]).groupby("사용자")["식당"].apply(set)
좋았던 = 시험[(시험["평점"] >= 좋은_평점) & 시험["식당"].isin(새_식당)]
문제들 = [(u, set(g) - 가본_곳[u]) for u, g in 좋았던.groupby("사용자")["식당"]
        if u in set(학습["사용자"]) and set(g) - 가본_곳[u]]
print(f"평가할 사용자 {len(문제들)}명, 후보는 새 식당 {len(새_식당)}곳")


def 채점(점수_함수, k: int = 5) -> str:
    """점수_함수(사용자) → 새 식당 40곳의 점수. 상위 k개로 Recall과 NDCG 평균."""
    목록들 = [list(새_식당[np.argsort(-점수_함수(u), kind="stable")]) for u, _ in 문제들]
    r = np.mean([recall_at_k(목록, 답, k) for 목록, (_, 답) in zip(목록들, 문제들)])
    n = np.mean([ndcg_at_k(목록, 답, k) for 목록, (_, 답) in zip(목록들, 문제들)])
    return f"Recall@{k} {r:.4f}, NDCG@{k} {n:.4f}"


torch.manual_seed(0)
행렬 = 행렬분해(len(사용자), len(식당))
학습하기(행렬, 쌍, 후보_식당, 학습설정(손실="bpr"))
torch.manual_seed(0)
타워 = 투타워(사용자, 식당)
학습하기(타워, 쌍, 후보_식당, 학습설정(손실="bpr", 에폭=60))
타워.eval()

지역, 음식, 동네 = 식당["지역"].to_numpy(), 식당["음식"].to_numpy(), 사용자["동네"].to_numpy()
with torch.no_grad():
    행렬_사용자 = 행렬.사용자_벡터(torch.arange(len(사용자)))
    행렬_식당 = 행렬.식당_벡터(torch.arange(len(식당)))
    평균_식당 = 행렬_식당.clone()                    # 새 식당 = 같은 지역·같은 음식 식당들의 평균
    for i in 새_식당:
        같은 = np.flatnonzero((지역 == 지역[i]) & (음식 == 음식[i]) & (식당["개업일"] < 300))
        평균_식당[i] = 행렬_식당[같은].mean(dim=0)
    타워_사용자 = 타워.사용자_벡터(torch.arange(len(사용자)))
    타워_새_식당 = 타워.식당_벡터(torch.tensor(새_식당), 번호_쓰기=False)   # 특징만으로

rng = np.random.default_rng(0)
print(채점(lambda u: rng.random(len(새_식당))), "|", "무작위")
print(채점(lambda u: (지역[새_식당] == 동네[u]) + rng.random(len(새_식당)) * 0.1), "|", "내 동네 식당 먼저")
print(채점(lambda u: (행렬_사용자[u] @ 행렬_식당[새_식당].T).numpy()), "|", "행렬 분해 (배운 적 없음)")
print(채점(lambda u: (행렬_사용자[u] @ 평균_식당[새_식당].T).numpy()), "|", "행렬 분해 + 비슷한 곳 평균")
print(채점(lambda u: (타워_사용자[u] @ 타워_새_식당.T).numpy()), "|", "투-타워 (특징만)")
