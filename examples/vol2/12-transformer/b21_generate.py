# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.9 글 만들기와 들여다보기 · manuscript-vol2/chapters/12-transformer.md:1281]
import torch

from 법전 import 준비
from 작은GPT import 학습된_모델

모델, 표 = 학습된_모델()                    # data/작은GPT.pt를 불러온다 (없으면 학습부터)
torch.manual_seed(0)
for 시작 in ["대한민국은", "제850조(", "국민은"]:
    번호들 = 모델.생성(표.인코딩(시작).unsqueeze(0), 개수=100)
    print(표.디코딩(번호들[0]))
    print("-" * 20)

학습_글 = 표.디코딩(준비()[1])               # 학습용 앞 90%를 다시 글로
for 구절 in ["제83조제3호, 제851조 및 제925조의 규정에 위반하거나", "혼인신고의 방법"]:
    print(f"학습 데이터에 있나? {구절 in 학습_글}  ← {구절!r}")
