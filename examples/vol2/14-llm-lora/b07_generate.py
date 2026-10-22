# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.3 디코딩: 다음 토큰을 고르는 방법 · manuscript-vol2/chapters/14-llm-lora.md:279]
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()
입력 = 토크나이저("비 오는 날 창밖을 보며", return_tensors="pt")
길이 = 입력["input_ids"].shape[1]

# 모델의 기본값(top_k=20, top_p=0.8, 반복 억제 1.1)이 끼어들지 않게 손잡이를 모두 직접 적는다
끄기 = dict(top_k=0, top_p=1.0, repetition_penalty=1.0)
설정들 = {
    "탐욕": dict(do_sample=False, repetition_penalty=1.0),
    "온도 0.7, top-p 0.9": dict(끄기, do_sample=True, temperature=0.7, top_p=0.9),
    "온도 1.5": dict(끄기, do_sample=True, temperature=1.5),
}
for 설명, 옵션 in 설정들.items():
    for 씨앗 in [1, 2]:
        torch.manual_seed(씨앗)
        결과 = 모델.generate(**입력, max_new_tokens=25, **옵션)
        글 = 토크나이저.decode(결과[0, 길이:], skip_special_tokens=True)
        print(f"[{설명} / 씨앗 {씨앗}] {글!r}")
