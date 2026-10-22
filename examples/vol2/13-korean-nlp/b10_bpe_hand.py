# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.5 토큰화 ③: 서브워드 · manuscript-vol2/chapters/13-korean-nlp.md:379]
from collections import Counter

# 예제용 어절과 등장 횟수. 처음에는 모든 어절을 글자 단위로 쪼개 둔다
어절_수 = {"재밌다": 5, "재밌어요": 6, "재밌네요": 3, "재미없다": 4, "재미없어요": 3, "좋네요": 4}
쪼갬 = {어절: list(어절) for 어절 in 어절_수}


def 짝_세기() -> Counter:
    """붙어 있는 두 조각의 쌍이 전체에서 몇 번 나오는지 센다(어절의 등장 횟수만큼)."""
    세기 = Counter()
    for 어절, 조각 in 쪼갬.items():
        for 짝 in zip(조각, 조각[1:]):
            세기[짝] += 어절_수[어절]
    return 세기


def 합치기(짝: tuple[str, str]) -> None:
    """모든 어절에서 그 쌍을 한 조각으로 붙인다."""
    for 어절, 조각 in 쪼갬.items():
        새 = []
        i = 0
        while i < len(조각):
            if i + 1 < len(조각) and (조각[i], 조각[i + 1]) == 짝:
                새.append(조각[i] + 조각[i + 1])
                i += 2
            else:
                새.append(조각[i])
                i += 1
        쪼갬[어절] = 새


for 단계 in range(1, 7):
    짝, 횟수 = 짝_세기().most_common(1)[0]
    합치기(짝)
    print(f"{단계}단계: {짝[0]} + {짝[1]} ({횟수}번)")

for 어절, 조각 in 쪼갬.items():
    print(f"{어절} → {조각}")
