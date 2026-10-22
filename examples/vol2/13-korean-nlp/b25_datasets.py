# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.11 Hugging Face datasets로 데이터 다루기 · manuscript-vol2/chapters/13-korean-nlp.md:1121]
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, DataCollatorWithPadding

from 한국어도구 import NSMC_받기

NSMC_받기()
자료 = load_dataset("csv", data_files={"train": "data/nsmc/ratings_train.txt",
                                       "test": "data/nsmc/ratings_test.txt"},
                   delimiter="\t")
print(자료)

자료 = 자료.filter(lambda 줄: 줄["document"] is not None and 줄["document"].strip() != "")
print("빈 리뷰를 걸러 낸 뒤:", 자료["train"].num_rows, 자료["test"].num_rows)
작은_학습 = 자료["train"].shuffle(seed=0).select(range(5000))
print(작은_학습.features)

토크나이저 = AutoTokenizer.from_pretrained("klue/bert-base")
토큰화 = 작은_학습.map(lambda 줄: 토크나이저(줄["document"], truncation=True, max_length=64),
                      batched=True, remove_columns=["id", "document"])
토큰화 = 토큰화.rename_column("label", "labels")
print(토큰화)

로더 = DataLoader(토큰화, batch_size=4, collate_fn=DataCollatorWithPadding(토크나이저))
배치 = next(iter(로더))
print({k: tuple(v.shape) for k, v in 배치.items()})
print("문장별 실제 토큰 수:", 배치["attention_mask"].sum(1).tolist())
