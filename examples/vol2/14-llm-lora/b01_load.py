# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.1 사전학습 언어 모델 불러오기 · manuscript-vol2/chapters/14-llm-lora.md:37]
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"                 # Hugging Face에 올라 있는 모델 이름
토크나이저 = AutoTokenizer.from_pretrained(이름)     # 글자 ↔ 번호 변환기
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32)

print(type(모델).__name__)
print(f"파라미터: {sum(p.numel() for p in 모델.parameters()):,}개")
설정 = 모델.config
print("층 수:", 설정.num_hidden_layers, "/ 은닉 크기:", 설정.hidden_size,
      "/ 어텐션 헤드:", 설정.num_attention_heads)
print("어휘 크기:", 설정.vocab_size, "/ 한 번에 읽는 최대 길이:", 설정.max_position_embeddings)
print(isinstance(모델, torch.nn.Module))           # 6장의 nn.Module 그대로
