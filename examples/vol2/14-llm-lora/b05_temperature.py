# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.3 디코딩: 다음 토큰을 고르는 방법 · manuscript-vol2/chapters/14-llm-lora.md:187]
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()

입력 = 토크나이저("점심 메뉴로 추천하는 음식은", return_tensors="pt")
with torch.no_grad():
    로짓 = 모델(**입력).logits[0, -1]

후보 = 로짓.topk(5).indices                           # 원래 점수 기준 상위 5개 후보
print("후보:", [토크나이저.decode([n]) for n in 후보.tolist()])
for 온도 in [0.5, 1.0, 2.0]:
    확률 = torch.softmax(로짓 / 온도, dim=-1)        # 점수를 온도로 나눈 뒤 확률로
    print(f"온도 {온도}: 상위 5개 {[round(p, 3) for p in 확률[후보].tolist()]}"
          f"  나머지 합 {1 - 확률[후보].sum().item():.3f}")
