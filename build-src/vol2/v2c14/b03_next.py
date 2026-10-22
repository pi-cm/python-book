import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()

입력 = 토크나이저("대한민국의 수도는", return_tensors="pt")
print("입력 번호:", 입력["input_ids"])
with torch.no_grad():
    로짓 = 모델(**입력).logits                       # (배치, 토큰 수, 어휘 크기)
print("로짓 모양:", tuple(로짓.shape))

마지막 = 로짓[0, -1]                                # 마지막 자리의 점수 = 다음 토큰 후보
확률 = torch.softmax(마지막, dim=-1)
상위 = 확률.topk(5)
for p, n in zip(상위.values, 상위.indices):
    print(f"{p.item():.3f}  {토크나이저.decode([n.item()])!r}")
