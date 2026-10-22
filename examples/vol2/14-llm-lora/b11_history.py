# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.4 프롬프트와 채팅 템플릿 · manuscript-vol2/chapters/14-llm-lora.md:466]
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()


def 묻기(대화: list[dict], 최대: int = 40) -> str:
    """대화 기록을 채팅 템플릿에 맞춰 넣고 모델의 답만 돌려준다."""
    입력 = 토크나이저.apply_chat_template(대화, add_generation_prompt=True,
                                         return_tensors="pt", return_dict=True)
    with torch.no_grad():
        결과 = 모델.generate(**입력, max_new_tokens=최대, do_sample=False,
                             repetition_penalty=1.1)      # 모델 기본값의 반복 억제는 켜 둔다
    return 토크나이저.decode(결과[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True)


기록 = [{"role": "user", "content": "내 이름은 민준이야."}]
기록.append({"role": "assistant", "content": 묻기(기록)})
print("첫 답:", 기록[-1]["content"])

새_질문 = {"role": "user", "content": "내 이름이 뭐라고 했지?"}
print("기록 없이:", 묻기([새_질문]))
print("기록 함께:", 묻기(기록 + [새_질문]))
print("모델에 들어간 메시지 수:", len(기록 + [새_질문]))
