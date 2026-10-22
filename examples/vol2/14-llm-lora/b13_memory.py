# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.6 메모리 계산과 양자화 맛보기 · manuscript-vol2/chapters/14-llm-lora.md:577]
import torch
from transformers import AutoConfig, AutoModelForCausalLM

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32)
GB = 1024 ** 3

# 4장 4.3절: 메모리 = 칸 크기(element_size) × 칸 개수(numel)
바이트 = sum(p.element_size() * p.numel() for p in 모델.parameters())
print(f"float32로 올린 이 모델: {바이트 / GB:.2f} GB")
print("입력 임베딩과 출력층이 같은 가중치인가:",
      모델.get_input_embeddings().weight is 모델.get_output_embeddings().weight)

# 같은 계산을 크기별·자료형별로: 칸당 바이트 수만 바꾸면 된다
for 크기, 개수 in [("0.5B", 494_032_768), ("7B", 7_000_000_000), ("70B", 70_000_000_000)]:
    칸 = {"float32": 4, "bfloat16": 2, "int8": 1, "int4": 0.5}
    print(f"{크기:>4}: " + ", ".join(f"{k} {개수 * v / GB:6.1f}GB" for k, v in 칸.items()))

# 생성할 때 따로 쌓이는 메모리: KV 캐시 (토큰마다 층마다 키와 값을 저장)
설정 = AutoConfig.from_pretrained(이름)
헤드_크기 = 설정.hidden_size // 설정.num_attention_heads
토큰당 = 2 * 설정.num_hidden_layers * 설정.num_key_value_heads * 헤드_크기 * 2   # bfloat16 기준
print(f"키·값 헤드 {설정.num_key_value_heads}개, 헤드 크기 {헤드_크기}, 토큰당 {토큰당:,}바이트")
print(f"토큰 32,768개를 기억하면 KV 캐시 {토큰당 * 32_768 / GB:.2f} GB")
print(f"키·값 헤드가 쿼리 헤드처럼 {설정.num_attention_heads}개였다면 "
      f"{토큰당 * 설정.num_attention_heads // 설정.num_key_value_heads * 32_768 / GB:.2f} GB")
