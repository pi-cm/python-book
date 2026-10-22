# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.9 사전학습 인코더 미세조정 · manuscript-vol2/chapters/13-korean-nlp.md:835]
from transformers import AutoModelForSequenceClassification

모델 = AutoModelForSequenceClassification.from_pretrained("klue/bert-base", num_labels=2)

for 이름, 부품 in 모델.named_children():
    print(f"{이름}: {type(부품).__name__}")
for 이름, 부품 in 모델.bert.named_children():
    print(f"  {'bert.' + 이름:16}{sum(p.numel() for p in 부품.parameters()):>12,}개")
print(f"  {'classifier':16}{sum(p.numel() for p in 모델.classifier.parameters()):>12,}개")
print("인코더 층 수:", len(모델.bert.encoder.layer))

전체 = sum(p.numel() for p in 모델.parameters())
바이트 = sum(p.element_size() * p.numel() for p in 모델.parameters())
print(f"전체 {전체:,}개, float32로 {바이트 / 1024**2:.0f} MB")
# AdamW로 학습하면 파라미터 + 기울기 + 옵티마이저 상태 2개 = 파라미터의 4배
print(f"학습 중 최소 {4 * 바이트 / 1024**3:.2f} GB (중간 계산값은 별도)")
