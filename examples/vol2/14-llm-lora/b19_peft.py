# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.8 peft로 LLM에 LoRA 붙이기 · manuscript-vol2/chapters/14-llm-lora.md:893]
import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()
입력 = 토크나이저("LoRA를 붙여도 처음에는 출력이 같을까?", return_tensors="pt")
with torch.no_grad():
    붙이기_전 = 모델(**입력).logits

설정 = LoraConfig(
    r=8,                                                   # 작은 행렬의 랭크
    lora_alpha=16,                                         # 배율 = lora_alpha / r = 2
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # 어텐션의 선형층 네 개
    task_type="CAUSAL_LM",
)
모델 = get_peft_model(모델, 설정)
모델.print_trainable_parameters()

층0 = 모델.base_model.model.model.layers[0].self_attn
print(층0.k_proj)

# 손으로 세어 보기: 층마다 r × (입력 + 출력)
손계산 = sum(8 * (층.in_features + 층.out_features)
           for 층 in [층0.q_proj.base_layer, 층0.k_proj.base_layer,
                     층0.v_proj.base_layer, 층0.o_proj.base_layer]) * 24
print(f"손으로 센 LoRA 숫자: {손계산:,}개")

모델.eval()
with torch.no_grad():
    붙인_뒤 = 모델(**입력).logits
print("붙이기 전후 출력이 같은가:", torch.allclose(붙이기_전, 붙인_뒤))
