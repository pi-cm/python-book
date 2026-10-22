# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.2 한국어가 어려운 이유 · manuscript-vol2/chapters/13-korean-nlp.md:135]
from collections import Counter

from 한국어도구 import NSMC_읽기

학습 = NSMC_읽기("ratings_train.txt")
어절_수 = Counter(어절 for 문장, _ in 학습 for 어절 in 문장.split())
한번 = sum(1 for n in 어절_수.values() if n == 1)
print(f"서로 다른 어절: {len(어절_수):,}개")
print(f"딱 한 번 나온 어절: {한번:,}개 ({한번 / len(어절_수):.1%})")

재밌_계열 = sorted((a for a in 어절_수 if a.startswith("재밌")), key=lambda a: -어절_수[a])
print(f"'재밌'으로 시작하는 어절: {len(재밌_계열):,}가지")
print("  자주 나온 것:", ", ".join(f"{a}({어절_수[a]})" for a in 재밌_계열[:8]))

# 학습 데이터로 만든 어절 사전으로 시험 데이터를 읽으면?
시험_어절 = [a for 문장, _ in NSMC_읽기("ratings_test.txt") for a in 문장.split()]
모름 = sum(1 for a in 시험_어절 if a not in 어절_수)
print(f"시험 어절 중 사전에 없는 것: {모름 / len(시험_어절):.1%}")
