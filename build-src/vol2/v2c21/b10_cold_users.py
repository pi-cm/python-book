import numpy as np
import pandas as pd
import torch

from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 순위지표 import 좋은_평점, ndcg_at_k, recall_at_k
from 추천학습 import 학습설정, 학습하기, 좋았던_쌍
from 투타워 import 투타워

데이터 = 데이터_만들기(씨앗=0)
식당, 사용자 = 데이터.식당, 데이터.사용자
학습, 검증, 시험 = 시간으로_나누기(데이터.방문)
이전 = pd.concat([학습, 검증])                             # 시험 직전까지 쌓인 기록

# 문제: 학습 기간 뒤에 가입한 사용자. 가입 때 적은 동네와, 그 뒤 검증 기간에 다녀온 곳(있으면)만 안다
새_사용자 = sorted(set(시험["사용자"]) - set(학습["사용자"]))
가본_곳 = 이전.groupby("사용자")["식당"].apply(set)
좋았던 = 시험[시험["평점"] >= 좋은_평점].groupby("사용자")["식당"].apply(set)
문제들 = [(u, 좋았던[u] - 가본_곳.get(u, set()), 가본_곳.get(u, set()))
        for u in 새_사용자 if u in 좋았던.index and 좋았던[u] - 가본_곳.get(u, set())]
print(f"새 사용자 {len(문제들)}명, 그중 시험 전에 다녀온 곳이 있는 사람 {sum(bool(h) for *_, h in 문제들)}명")

torch.manual_seed(0)
타워 = 투타워(사용자, 식당)
학습하기(타워, 좋았던_쌍(학습), torch.tensor(np.flatnonzero(식당["개업일"] < 300)),
        학습설정(손실="bpr", 에폭=60))
타워.eval()
with torch.no_grad():
    아는_식당 = torch.tensor((식당["개업일"] < 300).to_numpy())[:, None]
    전체 = torch.arange(len(식당))
    식당_벡터 = torch.where(아는_식당, 타워.식당_벡터(전체), 타워.식당_벡터(전체, 번호_쓰기=False))
    단위 = 식당_벡터 / 식당_벡터.norm(dim=1, keepdim=True)
    비슷함 = (단위 @ 단위.T).numpy()
    동네만_사용자 = 타워.사용자_벡터(torch.arange(len(사용자)), 번호_쓰기=False)

인기 = np.log1p(np.bincount(이전["식당"], minlength=len(식당)))
지역, 동네 = 식당["지역"].to_numpy(), 사용자["동네"].to_numpy()


def 채점(점수_함수, k: int = 10) -> str:
    rec, ndcg = [], []
    for u, 답, 가본 in 문제들:
        점수 = 점수_함수(u, 가본).astype(float)
        점수[list(가본)] = -np.inf                           # 이미 가 본 곳은 빼고
        목록 = list(np.argsort(-점수, kind="stable")[:k])
        rec.append(recall_at_k(목록, 답, k))
        ndcg.append(ndcg_at_k(목록, 답, k))
    return f"Recall@{k} {np.mean(rec):.4f}, NDCG@{k} {np.mean(ndcg):.4f}"


def 동네_인기(u: int, 가본: set[int]) -> np.ndarray:
    return 인기 + 3.0 * (지역 == 동네[u])                    # 내 동네면 점수를 크게 더한다


def 동네_인기_비슷한_곳(u: int, 가본: set[int]) -> np.ndarray:
    점수 = 동네_인기(u, 가본)
    if 가본:                                                # 다녀온 곳이 있으면 그와 비슷한 곳을 더 올린다
        점수 = 점수 + 2.0 * 비슷함[list(가본)].mean(axis=0)
    return 점수


print(채점(lambda u, h: 인기), "| 인기순")
print(채점(동네_인기), "| 동네 인기순")
print(채점(lambda u, h: (동네만_사용자[u] @ 식당_벡터.T).numpy()), "| 투-타워 (동네만)")
print(채점(동네_인기_비슷한_곳), "| 동네 인기순 + 다녀온 곳과 비슷한 곳")
