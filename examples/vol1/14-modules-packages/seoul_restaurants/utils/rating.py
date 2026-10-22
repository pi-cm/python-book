# [1권 Chapter 14: 모듈과 패키지 · 14.4 패키지 기초 · manuscript/chapters/14-modules-packages.md:686]
# seoul_restaurants/utils/rating.py
"""
평점 분석 유틸리티
"""
from collections import Counter
from typing import Dict, List


class RatingAnalyzer:
    """평점 목록을 요약하는 분석기"""

    def average(self, ratings: List[float]) -> float:
        """평균 평점 (평점이 없으면 0.0)"""
        if not ratings:
            return 0.0
        return round(sum(ratings) / len(ratings), 1)

    def distribution(self, ratings: List[float]) -> Dict[int, int]:
        """1~5점 각각의 개수 (소수점 아래는 버림)"""
        counts = Counter(int(r) for r in ratings)
        return {score: counts.get(score, 0) for score in range(1, 6)}
