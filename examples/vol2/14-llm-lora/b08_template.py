# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.4 프롬프트와 채팅 템플릿 · manuscript-vol2/chapters/14-llm-lora.md:328]
from transformers import AutoTokenizer

토크나이저 = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")

대화 = [
    {"role": "system", "content": "너는 친절한 파이썬 선생님이야."},
    {"role": "user", "content": "리스트가 뭐예요?"},
]
글 = 토크나이저.apply_chat_template(대화, tokenize=False, add_generation_prompt=True)
print(글)
print("특수 토큰:", 토크나이저.convert_ids_to_tokens(토크나이저.encode("<|im_start|><|im_end|>")))
