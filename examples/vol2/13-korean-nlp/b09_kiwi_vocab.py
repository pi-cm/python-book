# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.4 토큰화 ②: 형태소 분석 · manuscript-vol2/chapters/13-korean-nlp.md:325]
from collections import Counter

from kiwipiepy import Kiwi

from 한국어도구 import NSMC_읽기

kiwi = Kiwi()
학습 = NSMC_읽기("ratings_train.txt", 20000)
시험 = [문장 for 문장, _ in NSMC_읽기("ratings_test.txt", 5000)]


def 형태소(문장들: list[str]) -> list[list[str]]:
    """문장마다 '형태/품사' 목록. 문장 목록을 한꺼번에 넘기면 kiwi가 여러 개를 함께 처리한다."""
    return [[f"{t.form}/{t.tag}" for t in 결과]
            for 결과 in kiwi.tokenize(문장들, compatible_jamo=True)]


학습_형태소 = 형태소([문장 for 문장, _ in 학습])
사전 = {토큰 for 토큰들 in 학습_형태소 for 토큰 in 토큰들}
시험_형태소 = 형태소(시험)
전체 = sum(len(t) for t in 시험_형태소)
모름 = sum(1 for t in 시험_형태소 for 토큰 in t if 토큰 not in 사전)
print(f"형태소: 사전 {len(사전):>6,}개, 문장당 {전체 / len(시험):5.1f}토큰, 모르는 토큰 {모름 / 전체:5.1%}")

# 긍정·부정 리뷰에서 유난히 자주 나오는 형용사(VA)
세기 = {0: Counter(), 1: Counter()}
for (_, 라벨), 토큰들 in zip(학습, 학습_형태소):
    세기[라벨].update(t for t in 토큰들 if t.endswith("/VA"))
for 라벨, 이름 in [(1, "긍정"), (0, "부정")]:
    상대 = 세기[1 - 라벨]
    점수 = {w: n / (상대[w] + 1) for w, n in 세기[라벨].items() if n >= 30}
    print(이름, [w.split("/")[0] for w in sorted(점수, key=점수.get, reverse=True)[:6]])
