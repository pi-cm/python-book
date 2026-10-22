# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.9 사전학습 인코더 미세조정 · manuscript-vol2/chapters/13-korean-nlp.md:877]
from transformers import AutoTokenizer

from 한국어도구 import NSMC_읽기

토크나이저 = AutoTokenizer.from_pretrained("klue/bert-base")
학습 = [문장 for 문장, _ in NSMC_읽기("ratings_train.txt", 20000)]
길이 = sorted(len(토크나이저(s)["input_ids"]) for s in 학습)     # [CLS], [SEP] 포함

for 비율 in [0.5, 0.9, 0.99]:
    print(f"{비율:.0%} 지점: {길이[int(len(길이) * 비율)]}토큰")
print("가장 긴 리뷰:", 길이[-1], "토큰")
for 자르기 in [32, 64, 128]:
    잘림 = sum(1 for n in 길이 if n > 자르기) / len(길이)
    print(f"max_length={자르기}: 잘리는 리뷰 {잘림:.1%}")
print("모델이 받을 수 있는 최대 길이:", 토크나이저.model_max_length)
