# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.10 평가: 숫자 너머를 보기 · manuscript-vol2/chapters/13-korean-nlp.md:1026]
import torch
from sklearn.metrics import classification_report, confusion_matrix
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from 한국어도구 import NSMC_읽기

토크나이저 = AutoTokenizer.from_pretrained("data/감성모델")          # 13.9절에서 저장한 폴더
모델 = AutoModelForSequenceClassification.from_pretrained("data/감성모델").eval()
시험 = NSMC_읽기("ratings_test.txt", 5000)

확률들 = []
with torch.no_grad():
    for i in range(0, len(시험), 250):
        입력 = 토크나이저([s for s, _ in 시험[i:i + 250]], padding=True, truncation=True,
                         max_length=64, return_tensors="pt")
        확률들.append(모델(**입력).logits.softmax(-1))
확률 = torch.cat(확률들)
예측 = 확률.argmax(-1)
정답 = torch.tensor([y for _, y in 시험])

print(confusion_matrix(정답, 예측))
print(classification_report(정답, 예측, target_names=["부정", "긍정"], digits=3))

# 가장 자신 있게 틀린 리뷰 다섯 개 (원문은 시험[i][0]을 출력해 직접 읽어 보세요)
틀림 = (예측 != 정답).nonzero().squeeze(1)
자신감 = 확률[틀림].max(-1).values
for i in 틀림[자신감.argsort(descending=True)[:5]].tolist():
    print(f"{i}번: 정답 {정답[i].item()} / 예측 {예측[i].item()} ({확률[i].max():.3f}), {len(시험[i][0])}글자")
print(f"틀린 리뷰 {len(틀림)}개 중 확률 0.95 이상으로 틀린 것: {(자신감 >= 0.95).sum().item()}개")
