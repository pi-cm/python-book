# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.10 평가: 숫자 너머를 보기 · manuscript-vol2/chapters/13-korean-nlp.md:1092]
from transformers import pipeline

분류기 = pipeline("text-classification", model="data/감성모델")
예문들 = ["배우들 연기가 정말 좋았어요",
         "표값이 아까운 두 시간이었다",
         "재미없지는 않았다",                       # 이중 부정
         "와 정말 대단하다 두 시간을 이렇게 버리게 해 주다니",   # 비꼬기
         "ㄹㅇ 개꿀잼 인정"]                        # 줄임말
for 예문, 결과 in zip(예문들, 분류기(예문들)):
    print(f"{결과['label']} {결과['score']:.3f}  {예문}")
