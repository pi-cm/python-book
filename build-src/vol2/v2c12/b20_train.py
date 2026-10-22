import torch

from 법전 import 데이터_폴더, 준비
from 작은GPT import 설정, 장치_고르기, 학습

표, 학습_데이터, 검증_데이터 = 준비()
장치 = 장치_고르기()
print("장치:", 장치)
모델 = 학습(설정(어휘_크기=len(표)), 학습_데이터, 검증_데이터, 단계_수=3000, 장치=장치)
torch.save(모델.state_dict(), 데이터_폴더 / "작은GPT.pt")
print("저장:", 데이터_폴더 / "작은GPT.pt")
