# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.1 사전학습 언어 모델 불러오기 · manuscript-vol2/chapters/14-llm-lora.md:70]
from transformers import AutoTokenizer

토크나이저 = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")

문장 = "파이썬은 재미있다"
번호 = 토크나이저.encode(문장)
print(번호)
print([토크나이저.decode([n]) for n in 번호])      # 번호 하나하나가 어떤 조각인지
print(토크나이저.decode(번호))                     # 번호를 다시 글자로

# 같은 뜻의 문장, 토큰은 몇 개일까?
for 글 in ["오늘 날씨가 정말 좋네요.", "The weather is really nice today."]:
    print(f"{len(글):2}글자 → {len(토크나이저.encode(글)):2}토큰: {글}")
