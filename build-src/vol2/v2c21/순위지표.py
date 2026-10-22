"""21장 순위 지표: 추천 목록 하나를 채점하고, 여러 사용자를 한꺼번에 평가한다."""
from dataclasses import dataclass

import numpy as np
import pandas as pd

좋은_평점 = 3                                 # 3점 이상 준 방문을 '좋았던 방문'으로 본다


def recall_at_k(추천: list[int], 정답: set[int], k: int) -> float:
    """정답 식당 중 상위 k개 안에 든 비율."""
    return len(set(추천[:k]) & 정답) / len(정답)


def ndcg_at_k(추천: list[int], 정답: set[int], k: int) -> float:
    """맞힌 식당이 위에 있을수록 높은 점수. 가장 좋은 순서일 때 1."""
    dcg = sum(1 / np.log2(순위 + 2) for 순위, 식당 in enumerate(추천[:k]) if 식당 in 정답)
    idcg = sum(1 / np.log2(순위 + 2) for 순위 in range(min(len(정답), k)))
    return dcg / idcg


@dataclass
class 평가셋:
    사용자: np.ndarray          # 평가할 사용자 번호들
    정답: list[set[int]]        # 사용자마다 '처음 가서 좋았던' 식당들
    제외: np.ndarray            # (사용자, 식당) 참이면 후보에서 뺀다


def 평가셋_만들기(이전: pd.DataFrame, 대상: pd.DataFrame, 식당: pd.DataFrame) -> 평가셋:
    """이전 기록이 있는 사용자가 대상 기간에 '처음 가서 좋았던' 식당을 맞히는 문제를 만든다."""
    가본_곳 = 이전.groupby("사용자")["식당"].apply(set)
    좋았던 = 대상[대상["평점"] >= 좋은_평점]
    사용자들, 정답들 = [], []
    for u, 식당들 in 좋았던.groupby("사용자")["식당"]:
        새_곳 = set(식당들) - 가본_곳.get(u, set())
        if u in 가본_곳.index and 새_곳:           # 이전 기록이 있고, 새로 간 곳이 있는 사람만
            사용자들.append(u)
            정답들.append(새_곳)
    마지막_날 = 대상["날짜"].max()
    제외 = np.zeros((len(사용자들), len(식당)), dtype=bool)
    제외[:, 식당["개업일"].to_numpy() > 마지막_날] = True     # 아직 문을 열지 않은 식당
    for 줄, u in enumerate(사용자들):
        제외[줄, list(가본_곳[u])] = True                     # 이미 가 본 식당
    return 평가셋(np.array(사용자들), 정답들, 제외)


def 평가하기(점수: np.ndarray, 셋: 평가셋, k: int = 10) -> dict[str, float]:
    """점수: (평가 사용자 수, 식당 수). 제외할 칸을 지우고 상위 k개로 두 지표의 평균을 낸다."""
    점수 = np.where(셋.제외, -np.inf, 점수)
    상위 = np.argsort(-점수, axis=1, kind="stable")[:, :k]
    return {f"Recall@{k}": float(np.mean([recall_at_k(list(줄), 답, k) for 줄, 답 in zip(상위, 셋.정답)])),
            f"NDCG@{k}": float(np.mean([ndcg_at_k(list(줄), 답, k) for 줄, 답 in zip(상위, 셋.정답)]))}
