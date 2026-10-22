# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.12 실습: 맛집 추천 API 완성하기 · manuscript-vol2/chapters/21-capstone-recommender.md:1376]
"""미리 계산한 벡터로 추천한다 (torch 없이 NumPy만 쓴다)."""
import json
from pathlib import Path
from typing import Protocol

import numpy as np

추천목록 = list[tuple[int, float]]                    # (식당 번호, 점수)를 점수 높은 순으로


class 추천기(Protocol):
    지역들: list[str]
    식당: list[dict]

    def 사용자_수(self) -> int: ...
    def 추천(self, 사용자: int, k: int, 지역: str | None = None) -> tuple[str, 추천목록]: ...
    def 새_사용자_추천(self, 동네: str, 가본_곳: list[int], k: int, 지역: str | None = None) -> 추천목록: ...
    def 비슷한_식당(self, 식당: int, k: int) -> 추천목록: ...


class 벡터추천기:
    def __init__(self, 폴더: Path) -> None:
        벡터 = np.load(폴더 / "vectors.npz")
        self.사용자_벡터, self.식당_벡터 = 벡터["user_vectors"], 벡터["restaurant_vectors"]
        self.아는_사용자 = 벡터["known_users"]
        목록 = json.loads((폴더 / "catalog.json").read_text(encoding="utf-8"))
        self.지역들, self.식당, self.사용자 = 목록["areas"], 목록["restaurants"], 목록["users"]
        self.영업중 = np.array([r["open"] for r in self.식당])
        self.식당_지역 = np.array([self.지역들.index(r["area"]) for r in self.식당])
        self.인기 = np.log1p([r["visits"] for r in self.식당])
        단위 = self.식당_벡터 / np.linalg.norm(self.식당_벡터, axis=1, keepdims=True)
        self.비슷함 = 단위 @ 단위.T                       # 식당 × 식당 코사인 유사도, 미리 한 번

    def 사용자_수(self) -> int:
        return len(self.사용자)

    def _상위(self, 점수: np.ndarray, 뺄_곳: list[int], k: int, 지역: str | None) -> 추천목록:
        점수 = np.where(self.영업중, 점수, -np.inf)       # 문을 닫았거나 아직 안 연 곳은 빼고
        점수[뺄_곳] = -np.inf                              # 이미 가 본 곳(또는 자기 자신)도 빼고
        if 지역 is not None:
            점수[self.식당_지역 != self.지역들.index(지역)] = -np.inf
        상위 = np.argsort(-점수, kind="stable")[:k]
        return [(int(i), round(float(점수[i]), 4)) for i in 상위 if np.isfinite(점수[i])]

    def 추천(self, 사용자: int, k: int, 지역: str | None = None) -> tuple[str, 추천목록]:
        정보 = self.사용자[사용자]
        if not self.아는_사용자[사용자]:                  # 학습 기록이 없으면 새 사용자처럼
            return "new_user", self.새_사용자_추천(정보["home"], 정보["visited"], k, 지역)
        점수 = self.식당_벡터 @ self.사용자_벡터[사용자]
        return "personal", self._상위(점수, 정보["visited"], k, 지역)

    def 새_사용자_추천(self, 동네: str, 가본_곳: list[int], k: int, 지역: str | None = None) -> 추천목록:
        점수 = self.인기 + 3.0 * (self.식당_지역 == self.지역들.index(동네))     # 동네 인기순
        if 가본_곳:                                                          # + 다녀온 곳과 비슷한 곳
            점수 = 점수 + 2.0 * self.비슷함[가본_곳].mean(axis=0)
        return self._상위(점수, 가본_곳, k, 지역)

    def 비슷한_식당(self, 식당: int, k: int) -> 추천목록:
        return self._상위(self.비슷함[식당], [식당], k, None)
