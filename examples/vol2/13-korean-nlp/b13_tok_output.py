# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.6 사전학습 토크나이저 쓰기 · manuscript-vol2/chapters/13-korean-nlp.md:539]
from transformers import AutoTokenizer

토크나이저 = AutoTokenizer.from_pretrained("klue/bert-base")

인코딩 = 토크나이저("재밌었어요")
print(인코딩)
print(토크나이저.convert_ids_to_tokens(인코딩["input_ids"]))
print(토크나이저.decode(인코딩["input_ids"]))
print(토크나이저.decode(인코딩["input_ids"], skip_special_tokens=True))

# 여러 문장을 한꺼번에: 패딩·자르기·텐서로 바꾸기까지
배치 = 토크나이저(["최고", "배우들 연기가 너무 어색해서 몰입이 안 됨", "두 시간이 순식간에 지나갔다"],
                 padding=True, truncation=True, max_length=10, return_tensors="pt")
print(배치["input_ids"])
print(배치["attention_mask"])
print(토크나이저.convert_ids_to_tokens(배치["input_ids"][1]))
