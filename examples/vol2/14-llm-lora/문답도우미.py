# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.9 실습: 1권 도우미로 미세조정하기 · manuscript-vol2/chapters/14-llm-lora.md:1032]
"""14.9절 실습에서 함께 쓰는 준비 코드."""
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from 일권문답 import 시스템

모델_이름 = "Qwen/Qwen2.5-0.5B-Instruct"
어댑터_경로 = "data/lora_1권도우미"


def 불러오기() -> tuple:
    """토크나이저와 float32 모델을 불러온다. 결과를 재현하기 쉽게 CPU에서 쓴다."""
    토크나이저 = AutoTokenizer.from_pretrained(모델_이름)
    모델 = AutoModelForCausalLM.from_pretrained(모델_이름, dtype=torch.float32).eval()
    return 토크나이저, 모델


def 프롬프트(토크나이저, 질문: str) -> str:
    """시스템 지시와 질문을 채팅 템플릿에 맞춘 글로 만든다."""
    대화 = [{"role": "system", "content": 시스템}, {"role": "user", "content": 질문}]
    return 토크나이저.apply_chat_template(대화, tokenize=False, add_generation_prompt=True)


def 예제_만들기(토크나이저, 질문: str, 답: str) -> tuple[torch.Tensor, torch.Tensor]:
    """입력 번호와 정답 번호를 만든다. 질문 부분의 정답은 -100으로 가려 손실에서 뺀다."""
    앞 = 토크나이저(프롬프트(토크나이저, 질문), add_special_tokens=False)["input_ids"]
    뒤 = 토크나이저(답 + "<|im_end|>", add_special_tokens=False)["input_ids"]
    return torch.tensor(앞 + 뒤), torch.tensor([-100] * len(앞) + 뒤)


def 답하기(모델, 토크나이저, 질문: str, 최대: int = 60) -> str:
    """탐욕 디코딩(반복 억제 1.1)으로 답을 만든다."""
    입력 = 토크나이저(프롬프트(토크나이저, 질문), return_tensors="pt", add_special_tokens=False)
    with torch.no_grad():
        결과 = 모델.generate(**입력, max_new_tokens=최대, do_sample=False,
                             repetition_penalty=1.1)      # 모델 기본값의 반복 억제는 켜 둔다
    return 토크나이저.decode(결과[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True)


def 평가(모델, 토크나이저, 문답: list[tuple[str, str]]) -> tuple[float, float, float]:
    """정답을 보여 주며(교사 강요) 세 가지를 잰다.

    답 전체의 평균 손실, '1권 N장'의 N 자리 평균 손실, N을 1등으로 맞힌 비율.
    """
    손실합, 번호손실합, 맞힘 = 0.0, 0.0, 0
    for 질문, 답 in 문답:
        입력, 정답 = 예제_만들기(토크나이저, 질문, 답)
        with torch.no_grad():
            출력 = 모델(input_ids=입력[None], labels=정답[None])
        손실합 += 출력.loss.item()
        # 답 속 "1권 N장"의 N이 몇 번째 토큰인지 찾는다 (숫자는 한 글자씩 토큰이 된다)
        시작 = (정답 != -100).nonzero()[0].item()
        조각 = 토크나이저(답, add_special_tokens=False, return_offsets_mapping=True)
        처음, 끝 = re.search(r"1권 (\d+)장", 답).span(1)
        자리 = [시작 + i for i, (s, e) in enumerate(조각["offset_mapping"])
                if s < 끝 and e > 처음]
        점수 = 출력.logits[0, [j - 1 for j in 자리]]          # 그 토큰을 맞혀야 하는 자리의 점수
        번호손실합 += torch.nn.functional.cross_entropy(점수, 입력[자리]).item()
        맞힘 += bool((점수.argmax(dim=-1) == 입력[자리]).all())
    n = len(문답)
    return 손실합 / n, 번호손실합 / n, 맞힘 / n
