# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.2 예제용 데이터 만들기 · manuscript-vol2/chapters/21-capstone-recommender.md:174]
"""21장 예제용 맛집 데이터: 숨은 취향을 넣어 만든 가짜 사용자·식당·방문 기록 (실제 데이터가 아니다)."""
from dataclasses import dataclass

import numpy as np
import pandas as pd

지역들 = ["강남", "홍대", "성수", "종로", "여의도", "잠실", "이태원", "신촌"]
음식들 = ["한식", "중식", "일식", "양식", "분식", "고기", "해산물", "카페"]
음식별_매운맛 = np.array([0.6, 0.7, 0.2, 0.2, 0.7, 0.4, 0.4, 0.05])
기간 = 365                                   # 1년치 기록 (0일 ~ 364일)


@dataclass
class 맛집데이터:
    식당: pd.DataFrame
    사용자: pd.DataFrame
    방문: pd.DataFrame


def 식당_만들기(rng: np.random.Generator, 개수: int, 새_식당: int) -> pd.DataFrame:
    음식 = rng.integers(0, len(음식들), 개수)
    지역 = rng.integers(0, len(지역들), 개수)
    개업일 = np.zeros(개수, dtype=int)
    개업일[-새_식당:] = rng.integers(300, 350, 새_식당)   # 마지막 몇 곳은 나중에 문을 연다
    이름 = [f"{지역들[j]} {음식들[c]} {i:03d}" for i, (j, c) in enumerate(zip(지역, 음식))]
    return pd.DataFrame({
        "식당": np.arange(개수), "이름": 이름, "지역": 지역, "음식": 음식,
        "가격대": rng.integers(1, 4, 개수), "개업일": 개업일,
        # '숨은_'으로 시작하는 열은 정답 확인용이다. 모델에는 절대 주지 않는다
        "숨은_매운맛": np.clip(음식별_매운맛[음식] + rng.normal(0, 0.25, 개수), 0, 1),
        "숨은_분위기": rng.uniform(-1, 1, 개수),             # -1 조용함 ~ +1 시끌벅적
        "숨은_품질": rng.normal(0, 1, 개수),
    })


def 사용자_만들기(rng: np.random.Generator, 개수: int, 새_사용자: int) -> pd.DataFrame:
    가입일 = np.zeros(개수, dtype=int)
    가입일[-새_사용자:] = rng.integers(300, 340, 새_사용자)   # 마지막 몇 명은 늦게 가입한다
    return pd.DataFrame({
        "사용자": np.arange(개수), "동네": rng.integers(0, len(지역들), 개수),
        "가입일": 가입일,
        "숨은_직장": rng.integers(0, len(지역들), 개수),
        "숨은_매운맛선호": rng.normal(0, 1, 개수),
        "숨은_분위기선호": rng.normal(0, 1, 개수),
        "숨은_가격민감": rng.uniform(0, 1, 개수),
        "숨은_활동량": rng.lognormal(np.log(18), 0.6, 개수),
    })


def 끌림_계산(식당: pd.DataFrame, 사용자: pd.DataFrame, 음식_선호: np.ndarray) -> np.ndarray:
    """사용자 × 식당 끌림 점수. 숨은 취향과 식당의 숨은 성질이 맞을수록 크다."""
    u, r = 사용자, 식당
    끌림 = (1.5 * 음식_선호[:, r["음식"]]
          + 1.6 * np.outer(u["숨은_매운맛선호"], r["숨은_매운맛"] - 0.4)
          + 1.2 * np.outer(u["숨은_분위기선호"], r["숨은_분위기"])
          - 1.0 * np.outer(u["숨은_가격민감"], r["가격대"] - 2)
          + 0.8 * r["숨은_품질"].to_numpy())
    끌림 += 2.2 * (u["동네"].to_numpy()[:, None] == r["지역"].to_numpy())
    끌림 += 1.6 * (u["숨은_직장"].to_numpy()[:, None] == r["지역"].to_numpy())
    return 끌림


def 데이터_만들기(씨앗: int = 0, 식당_수: int = 400, 사용자_수: int = 3000) -> 맛집데이터:
    rng = np.random.default_rng(씨앗)
    식당 = 식당_만들기(rng, 식당_수, 새_식당=40)
    사용자 = 사용자_만들기(rng, 사용자_수, 새_사용자=300)
    끌림 = 끌림_계산(식당, 사용자, rng.normal(0, 1, (사용자_수, len(음식들))))
    개업일 = 식당["개업일"].to_numpy()
    기록 = []
    for u, 가입 in enumerate(사용자["가입일"]):
        횟수 = max(3, int(사용자["숨은_활동량"][u] * (기간 - 가입) / 기간))
        날짜 = np.sort(rng.integers(가입, 기간, 횟수))
        # 날마다 그날 문을 연 식당 중에서 끌림이 큰 곳을 확률적으로 고른다 (굼벨 트릭)
        점수 = 끌림[u] + rng.gumbel(size=(횟수, 식당_수))
        점수[개업일[None, :] > 날짜[:, None]] = -np.inf
        고른_곳 = 점수.argmax(axis=1)
        기록.append(pd.DataFrame({"사용자": u, "식당": 고른_곳, "날짜": 날짜, "끌림": 끌림[u, 고른_곳]}))
    방문 = pd.concat(기록).sort_values(["날짜", "사용자"]).reset_index(drop=True)
    # 평점: 끌림이 클수록 높게, 잡음을 섞어 1~5점으로
    z = (방문["끌림"] - 방문["끌림"].mean()) / 방문["끌림"].std()
    방문["평점"] = np.clip(np.round(3.6 + 0.9 * z + rng.normal(0, 0.8, len(방문))), 1, 5).astype(int)
    방문 = 방문.drop(columns="끌림")
    return 맛집데이터(식당, 사용자, 방문)


def 시간으로_나누기(방문: pd.DataFrame, 검증_시작: int = 300,
                  시험_시작: int = 330) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """날짜로 자른다(2장 2.9절): 학습 < 검증_시작 <= 검증 < 시험_시작 <= 시험."""
    학습 = 방문[방문["날짜"] < 검증_시작]
    검증 = 방문[(방문["날짜"] >= 검증_시작) & (방문["날짜"] < 시험_시작)]
    시험 = 방문[방문["날짜"] >= 시험_시작]
    return 학습, 검증, 시험
