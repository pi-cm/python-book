# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.6 메모리 계산과 양자화 맛보기 · manuscript-vol2/chapters/14-llm-lora.md:627]
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
입력 = 토크나이저.apply_chat_template([{"role": "user", "content": "1 더하기 1은?"}],
                                     add_generation_prompt=True,
                                     return_tensors="pt", return_dict=True)
결과 = {}
for 자료형 in [torch.float32, torch.bfloat16]:
    모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=자료형).eval()
    with torch.no_grad():
        로짓 = 모델(**입력).logits[0, -1].float()
        생성 = 모델.generate(**입력, max_new_tokens=20, do_sample=False,
                             repetition_penalty=1.1)
    결과[자료형] = 로짓
    print(f"{str(자료형):15} {모델.get_memory_footprint() / 1024**3:.2f} GB  "
          f"{토크나이저.decode(생성[0, 입력['input_ids'].shape[1]:], skip_special_tokens=True)!r}")

차이 = (결과[torch.float32] - 결과[torch.bfloat16]).abs()
print(f"다음 토큰 점수 차이: 평균 {차이.mean():.3f}, 최대 {차이.max():.3f}")
print("1등 토큰이 같은가:", (결과[torch.float32].argmax() == 결과[torch.bfloat16].argmax()).item())
