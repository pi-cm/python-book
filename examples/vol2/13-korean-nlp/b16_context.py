# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.7 임베딩: 번호를 화살표로 · manuscript-vol2/chapters/13-korean-nlp.md:633]
import torch
from transformers import AutoModel, AutoTokenizer

토크나이저 = AutoTokenizer.from_pretrained("klue/bert-base")
모델 = AutoModel.from_pretrained("klue/bert-base").eval()

문장들 = ["배가 고파서 밥을 먹었다", "점심을 굶었더니 배가 아프다",      # 몸
         "배를 타고 섬에 갔다", "항구에 큰 배가 들어왔다",               # 탈것
         "깎아 놓은 배가 달고 시원하다", "사과와 배를 한 상자씩 샀다"]    # 과일
배_번호 = 토크나이저.convert_tokens_to_ids("배")

벡터들 = []
with torch.no_grad():
    for 문장 in 문장들:
        입력 = 토크나이저(문장, return_tensors="pt")
        출력 = 모델(**입력).last_hidden_state[0]                 # (토큰 수, 768)
        자리 = (입력["input_ids"][0] == 배_번호).nonzero()[0, 0]  # '배' 토큰의 위치
        벡터들.append(출력[자리])

단위 = torch.stack(벡터들)
단위 = 단위 / 단위.norm(dim=1, keepdim=True)
print("문맥을 거친 '배'끼리의 코사인 유사도:")
print((단위 @ 단위.T).numpy().round(2))
