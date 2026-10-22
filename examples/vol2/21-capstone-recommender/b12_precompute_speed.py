# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.11 서빙 준비: 벡터를 미리 계산해 두기 · manuscript-vol2/chapters/21-capstone-recommender.md:1194]
import statistics
import time

import numpy as np
import torch

from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 추천학습 import 학습설정, 학습하기, 좋았던_쌍
from 투타워 import 투타워

데이터 = 데이터_만들기(씨앗=0)
학습, _, _ = 시간으로_나누기(데이터.방문)
torch.manual_seed(0)
타워 = 투타워(데이터.사용자, 데이터.식당)
학습하기(타워, 좋았던_쌍(학습), torch.tensor(np.flatnonzero(데이터.식당["개업일"] < 300)),
        학습설정(에폭=3))                          # 시간만 잴 것이라 짧게
타워.eval()
전체_식당 = torch.arange(len(데이터.식당))


def 모델로_바로(u: int) -> list[int]:
    """요청마다 두 탑을 모두 돌린다."""
    with torch.no_grad():
        점수 = 타워.사용자_벡터(torch.tensor([u])) @ 타워.식당_벡터(전체_식당).T
    return 점수[0].topk(10).indices.tolist()


with torch.no_grad():
    식당_행렬 = 타워.식당_벡터(전체_식당)                       # (400, 32): 한 번만
    사용자_행렬 = 타워.사용자_벡터(torch.arange(len(데이터.사용자)))  # (3000, 32): 한 번만


def 식당만_미리(u: int) -> list[int]:
    with torch.no_grad():
        점수 = 타워.사용자_벡터(torch.tensor([u])) @ 식당_행렬.T
    return 점수[0].topk(10).indices.tolist()


식당_np, 사용자_np = 식당_행렬.numpy(), 사용자_행렬.numpy()


def 모두_미리_numpy(u: int) -> list[int]:
    점수 = 식당_np @ 사용자_np[u]                              # (400,): 곱셈 한 번
    상위 = np.argpartition(-점수, 10)[:10]                     # 상위 10개만 골라 놓고
    return 상위[np.argsort(-점수[상위])].tolist()              # 그 10개만 정렬


print("세 방법의 답이 같은가:", all(모델로_바로(u) == 식당만_미리(u) == 모두_미리_numpy(u)
                                  for u in range(100)))
for 이름, 함수 in [("요청마다 두 탑 모두", 모델로_바로), ("식당 벡터만 미리", 식당만_미리),
                  ("모두 미리 + NumPy", 모두_미리_numpy)]:
    for u in range(50):
        함수(u)                                                # 준비 운동
    시간 = []
    for u in range(2000):
        시작 = time.perf_counter()
        함수(u % 3000)
        시간.append((time.perf_counter() - 시작) * 1e6)
    print(f"요청 하나에 {statistics.median(시간):7.1f}µs (중앙값) | {이름}")
print(f"미리 계산한 벡터: 사용자 {사용자_np.nbytes / 1024:.0f}KB, 식당 {식당_np.nbytes / 1024:.0f}KB")
