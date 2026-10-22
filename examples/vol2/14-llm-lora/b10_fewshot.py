# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.4 프롬프트와 채팅 템플릿 · manuscript-vol2/chapters/14-llm-lora.md:408]
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()


def 묻기(대화: list[dict], 최대: int) -> str:
    """대화 기록을 채팅 템플릿에 맞춰 넣고 모델의 답만 돌려준다."""
    입력 = 토크나이저.apply_chat_template(대화, add_generation_prompt=True,
                                         return_tensors="pt", return_dict=True)
    with torch.no_grad():
        결과 = 모델.generate(**입력, max_new_tokens=최대, do_sample=False,
                             repetition_penalty=1.1)      # 모델 기본값의 반복 억제는 켜 둔다
    return 토크나이저.decode(결과[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True)


# 예시 두 개를 "이미 주고받은 대화"처럼 넣어 둔다 (예제용 후기)
예시 = [
    {"role": "system", "content": "상품 후기를 읽고 '긍정' 또는 '부정' 한 단어로만 답해."},
    {"role": "user", "content": "배송이 빠르고 품질도 좋아요."},
    {"role": "assistant", "content": "긍정"},
    {"role": "user", "content": "한 번 빨았더니 색이 다 빠졌어요."},
    {"role": "assistant", "content": "부정"},
]
후기들 = ["가격 대비 정말 만족합니다.", "사이즈가 너무 작아서 반품했어요.",
        "포장은 꼼꼼했는데 맛이 별로네요.", "생각보다 튼튼하고 예뻐요."]
for 후기 in 후기들:
    예시없이 = 묻기([{"role": "user", "content": f"다음 후기는 긍정이야 부정이야? {후기}"}], 20)
    예시있게 = 묻기(예시 + [{"role": "user", "content": 후기}], 5)
    print(f"{후기}\n  예시 없이: {예시없이!r}\n  예시 두 개: {예시있게!r}")
