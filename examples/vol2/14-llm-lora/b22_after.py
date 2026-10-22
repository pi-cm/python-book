# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.9 실습: 1권 도우미로 미세조정하기 · manuscript-vol2/chapters/14-llm-lora.md:1212]
import torch
from peft import PeftModel

from 문답도우미 import 답하기, 불러오기, 어댑터_경로, 평가
from 일권문답 import 시험_문답, 학습_문답

토크나이저, 모델 = 불러오기()
모델 = PeftModel.from_pretrained(모델, 어댑터_경로).eval()   # 원래 모델 + 저장한 LoRA

for 이름, 문답 in [("학습", 학습_문답), ("시험", 시험_문답)]:
    손실, 번호손실, 맞힘 = 평가(모델, 토크나이저, 문답)
    print(f"[미세조정 후] {이름} 문답: 답 손실 {손실:.3f}, "
          f"장 번호 자리 손실 {번호손실:.3f}, 장 번호 맞힘 {맞힘:.0%}")

for 질문, 기준 in 학습_문답[:2] + 시험_문답:
    print(f"\nQ. {질문}\n기준. {기준}\n모델. {답하기(모델, 토크나이저, 질문)}")

# LoRA를 원래 가중치에 합쳐 보통 모델로 만들기 (14.7절의 W + 배율·BA)
합친_모델 = 모델.merge_and_unload()
print("\n합친 뒤에도 같은 답인가:",
      답하기(합친_모델, 토크나이저, 시험_문답[0][0]) == 답하기(모델, 토크나이저, 시험_문답[0][0]))
print(type(합친_모델).__name__)
