# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.2 다음 토큰 예측: LLM이 하는 일은 하나뿐 · manuscript-vol2/chapters/14-llm-lora.md:143]
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()

번호 = 토크나이저("대한민국의 수도는", return_tensors="pt")["input_ids"]
시작_길이 = 번호.shape[1]

# 직접 만든 생성 루프: 가장 점수가 높은 토큰을 골라 뒤에 붙이고 다시 넣기
with torch.no_grad():
    for _ in range(15):
        다음 = 모델(번호).logits[0, -1].argmax()        # 탐욕(greedy): 1등만 고른다
        번호 = torch.cat([번호, 다음.view(1, 1)], dim=1)
직접 = 토크나이저.decode(번호[0, 시작_길이:])
print(repr(직접))

# 같은 일을 generate 한 줄로 (반복 억제 기본값 1.1을 꺼서 직접 만든 루프와 똑같은 규칙으로)
입력 = 토크나이저("대한민국의 수도는", return_tensors="pt")
with torch.no_grad():
    결과 = 모델.generate(**입력, max_new_tokens=15, do_sample=False, repetition_penalty=1.0)
자동 = 토크나이저.decode(결과[0, 시작_길이:])
print(repr(자동))
print("같은가:", 직접 == 자동)
