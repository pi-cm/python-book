# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.5 작은 모델의 한계를 정직하게 보기 · manuscript-vol2/chapters/14-llm-lora.md:510]
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()


def 묻기(질문: str, 최대: int = 45) -> str:
    """질문 하나를 채팅 형식으로 묻고 답을 한 줄로 돌려준다."""
    입력 = 토크나이저.apply_chat_template([{"role": "user", "content": 질문}],
                                         add_generation_prompt=True,
                                         return_tensors="pt", return_dict=True)
    with torch.no_grad():
        결과 = 모델.generate(**입력, max_new_tokens=최대, do_sample=False,
                             repetition_penalty=1.1)      # 모델 기본값의 반복 억제는 켜 둔다
    답 = 토크나이저.decode(결과[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True)
    return 답.replace("\n", " ")


for 질문 in ["파이썬에서 리스트와 튜플의 차이를 한 문장으로 설명해 줘.",
           "In one sentence, what is the difference between a list and a tuple in Python?",
           "37 곱하기 24는 얼마야? 숫자만 답해.",
           "세종대왕이 만든 문자는?",
           "대한민국에서 가장 높은 산은?"]:
    print(f"Q. {질문}\nA. {묻기(질문)}\n")
