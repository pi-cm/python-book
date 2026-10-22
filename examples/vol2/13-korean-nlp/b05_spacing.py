# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.2 한국어가 어려운 이유 · manuscript-vol2/chapters/13-korean-nlp.md:172]
from kiwipiepy import Kiwi

from 한국어도구 import NSMC_읽기

학습 = NSMC_읽기("ratings_train.txt")
for 변형들 in [["볼만한", "볼 만한"], ["재미없다", "재미 없다"], ["시간가는줄", "시간 가는 줄"]]:
    print(" / ".join(f"'{v}' {sum(v in 문장 for 문장, _ in 학습)}번" for v in 변형들))

붙여쓴 = [문장 for 문장, _ in 학습 if " " not in 문장 and len(문장) >= 15]
print(f"15글자 이상인데 띄어쓰기가 하나도 없는 리뷰: {len(붙여쓴):,}개")

kiwi = Kiwi()
for 문장 in ["어제동생이랑보러갔는데생각보다훨씬재밌었어요", "배우들연기는좋은데결말이너무허무해서아쉬움"]:   # 예제용으로 지은 문장
    print(문장, "→", kiwi.space(문장))
