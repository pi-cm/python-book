# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.6 메모리 계산과 양자화 맛보기 · manuscript-vol2/chapters/14-llm-lora.md:665]
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def 양자화_왕복(w: torch.Tensor, 비트: int) -> torch.Tensor:
    """행마다 가장 큰 절댓값을 기준으로 정수 칸에 맞춰 반올림했다가 다시 실수로 되돌린다."""
    최대정수 = 2 ** (비트 - 1) - 1                          # int8이면 127, int4면 7
    배율 = w.abs().amax(dim=1, keepdim=True) / 최대정수        # 행마다 하나 (keepdim: 4장 4.6절)
    정수 = (w / 배율).round().clamp(-최대정수, 최대정수)       # 이 정수만 저장하면 된다
    return 정수 * 배율


w = torch.tensor([[0.12, -0.50, 0.33, 0.07]])
print("원래   :", w)
print("int8   :", 양자화_왕복(w, 8))
print("int4   :", 양자화_왕복(w, 4))

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
문장 = ("파이썬은 배우기 쉬운 프로그래밍 언어입니다. "
        "많은 사람들이 데이터 분석과 인공지능에 파이썬을 씁니다.")
번호 = 토크나이저(문장, return_tensors="pt")["input_ids"]
for 비트 in [None, 8, 4]:
    모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()
    if 비트:
        with torch.no_grad():
            for 층 in 모델.model.layers.modules():          # 트랜스포머 층 안의 선형층만
                if isinstance(층, torch.nn.Linear):
                    층.weight.copy_(양자화_왕복(층.weight, 비트))
    with torch.no_grad():
        손실 = 모델(번호, labels=번호).loss.item()
    print(f"{'원래 float32' if 비트 is None else f'int{비트} 흉내':12} 손실 {손실:.3f}  "
          f"(다음 토큰 정답 확률의 기하평균 {torch.exp(torch.tensor(-손실)):.3f})")
