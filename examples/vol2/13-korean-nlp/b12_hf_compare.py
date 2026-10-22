# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.6 사전학습 토크나이저 쓰기 · manuscript-vol2/chapters/13-korean-nlp.md:501]
from transformers import AutoTokenizer

from 한국어도구 import NSMC_읽기

시험 = [문장 for 문장, _ in NSMC_읽기("ratings_test.txt", 1000)]
예문 = "이 영화 진짜 재밌었어요 배우들 연기도 최고!"

for 이름 in ["klue/bert-base", "google-bert/bert-base-multilingual-cased", "FacebookAI/xlm-roberta-base"]:
    토크나이저 = AutoTokenizer.from_pretrained(이름)        # 처음 한 번만 내려받고, 다음부터는 캐시에서
    번호들 = [토크나이저(s, add_special_tokens=False)["input_ids"] for s in 시험]
    전체 = sum(len(b) for b in 번호들)
    모름 = sum(1 for b in 번호들 for i in b if i == 토크나이저.unk_token_id)
    print(f"{이름} (사전 {토크나이저.vocab_size:,}개)")
    print(f"  문장당 {전체 / len(시험):.1f}토큰, [UNK] {모름 / 전체:.2%}")
    print(" ", 토크나이저.tokenize(예문))
