# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.7 임베딩: 번호를 화살표로 · manuscript-vol2/chapters/13-korean-nlp.md:596]
import torch
from transformers import AutoModel, AutoTokenizer

토크나이저 = AutoTokenizer.from_pretrained("klue/bert-base")
모델 = AutoModel.from_pretrained("klue/bert-base")
표 = 모델.get_input_embeddings().weight.detach()      # (사전 크기, 768): 토큰마다 화살표 하나
print(tuple(표.shape), f"{표.element_size() * 표.numel() / 1024**2:.1f} MB")

단위 = 표 / 표.norm(dim=1, keepdim=True)              # 4장 4.11절처럼 길이를 1로 맞추고
for 단어 in ["영화", "최고", "지루", "배우", "서울"]:
    번호 = 토크나이저.convert_tokens_to_ids(단어)
    유사도 = 단위 @ 단위[번호]                          # 모든 토큰과의 코사인 유사도를 한 번에
    상위 = 유사도.topk(6).indices[1:]                   # 1등은 자기 자신이라 뺀다
    print(단어, "→", 토크나이저.convert_ids_to_tokens(상위.tolist()))
