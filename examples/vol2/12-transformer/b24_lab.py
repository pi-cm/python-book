# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.10 실습: 부품을 하나씩 빼 보기 · manuscript-vol2/chapters/12-transformer.md:1429]
import torch

from 법전 import 준비
from 작은GPT import 설정, 장치_고르기, 학습

표, 학습_데이터, 검증_데이터 = 준비()
장치 = 장치_고르기()
실험들 = {
    "기본": 설정(어휘_크기=len(표)),
    "위치 임베딩 없음": 설정(어휘_크기=len(표), 위치_사용=False),
    "인과 마스크 없음": 설정(어휘_크기=len(표), 인과_마스크=False),
}
for 이름, s in 실험들.items():
    print(f"[{이름}]")
    모델 = 학습(s, 학습_데이터, 검증_데이터, 단계_수=1000, 장치=장치, 보고_간격=1000)
    torch.manual_seed(0)
    글 = 표.디코딩(모델.생성(표.인코딩("제5조 ").unsqueeze(0), 개수=60)[0])
    print("  생성:", 글.replace("\n", " / "))
