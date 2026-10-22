# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.2 한국어가 어려운 이유 · manuscript-vol2/chapters/13-korean-nlp.md:206]
import unicodedata

완성형 = "한글"
분해형 = unicodedata.normalize("NFD", 완성형)     # 초성·중성·종성으로 쪼갠 형태
print(완성형 == 분해형, len(완성형), len(분해형))
print("분해형이 '글'로 끝나나?", 분해형.endswith("글"))
print(unicodedata.normalize("NFC", 분해형) == 완성형)   # 다시 합치면 같아진다


def 정규화(문장: str) -> str:
    """처리하기 전에 언제나 완성형(NFC)으로 맞춘다."""
    return unicodedata.normalize("NFC", 문장)


print([정규화(s) == "한글" for s in [완성형, 분해형]])

# 자판으로 친 'ㅋ'(호환용 자모)과 NFKC로 바뀐 'ㅋ'(첫소리 자모)도 다른 문자다
print(hex(ord("ㅋ")), "→", hex(ord(unicodedata.normalize("NFKC", "ㅋ"))))
