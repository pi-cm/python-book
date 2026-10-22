# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.5 토큰화 ③: 서브워드 · manuscript-vol2/chapters/13-korean-nlp.md:443]
from tokenizers import Tokenizer, models, pre_tokenizers, trainers

from 한국어도구 import NSMC_읽기

학습 = [문장 for 문장, _ in NSMC_읽기("ratings_train.txt")]
시험 = [문장 for 문장, _ in NSMC_읽기("ratings_test.txt", 5000)]
예문 = "시간 가는 줄 모르고 봤네요 끝까지 재밌었어요"

for 크기 in [500, 4000, 32000]:
    토크나이저 = Tokenizer(models.BPE(unk_token="[UNK]"))
    토크나이저.pre_tokenizer = pre_tokenizers.Whitespace()       # 먼저 공백·문장부호로 자른다
    훈련 = trainers.BpeTrainer(vocab_size=크기, special_tokens=["[PAD]", "[UNK]"],
                              show_progress=False)
    토크나이저.train_from_iterator(학습, 훈련)
    평균 = sum(len(토크나이저.encode(s).ids) for s in 시험) / len(시험)
    print(f"사전 {토크나이저.get_vocab_size():>6,}개: 문장당 {평균:4.1f}토큰 | "
          + " ".join(토크나이저.encode(예문).tokens))

토크나이저.save("data/nsmc_bpe.json")            # 마지막(32,000개) 토크나이저를 파일로 저장
print(Tokenizer.from_file("data/nsmc_bpe.json").encode("재미없어요").tokens)
