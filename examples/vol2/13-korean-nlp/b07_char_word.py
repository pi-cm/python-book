# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.3 토큰화 ①: 글자와 어절 · manuscript-vol2/chapters/13-korean-nlp.md:247]
from collections.abc import Callable

from 한국어도구 import NSMC_읽기

학습 = [문장 for 문장, _ in NSMC_읽기("ratings_train.txt", 20000)]
시험 = [문장 for 문장, _ in NSMC_읽기("ratings_test.txt", 5000)]


def 비교(이름: str, 자르기: Callable[[str], list[str]]) -> None:
    """학습 문장으로 사전을 만들고, 시험 문장의 평균 길이와 모르는 토큰 비율을 잰다."""
    사전 = {토큰 for 문장 in 학습 for 토큰 in 자르기(문장)}
    토큰들 = [자르기(문장) for 문장 in 시험]
    전체 = sum(len(t) for t in 토큰들)
    모름 = sum(1 for t in 토큰들 for 토큰 in t if 토큰 not in 사전)
    print(f"{이름}: 사전 {len(사전):>6,}개, 문장당 {전체 / len(시험):5.1f}토큰, 모르는 토큰 {모름 / 전체:5.1%}")


비교("글자", lambda s: list(s.replace(" ", "")))
비교("어절", str.split)
