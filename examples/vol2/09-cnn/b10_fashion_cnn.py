# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.5 첫 CNN으로 옷 사진 분류하기 · manuscript-vol2/chapters/09-cnn.md:542]
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from 옷도구 import 옷CNN, 평가하기, 한_에폭_학습

torch.manual_seed(0)
변환 = transforms.ToTensor()
학습셋 = datasets.FashionMNIST("data", train=True, download=True, transform=변환)
시험셋 = datasets.FashionMNIST("data", train=False, download=True, transform=변환)
학습_로더 = DataLoader(학습셋, batch_size=64, shuffle=True)
시험_로더 = DataLoader(시험셋, batch_size=256)

장치 = torch.device("cpu")      # 6장처럼 재현을 위해 CPU. 장치_고르기()로 바꾸면 더 빠르다
모델 = 옷CNN().to(장치)
손실함수 = nn.CrossEntropyLoss()
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
print(f"파라미터 {sum(p.numel() for p in 모델.parameters()):,}개")

for 에폭 in range(1, 6):
    학습_손실 = 한_에폭_학습(모델, 학습_로더, 손실함수, 옵티마이저, 장치)
    시험_손실, 정확도 = 평가하기(모델, 시험_로더, 손실함수, 장치)
    print(f"에폭 {에폭}: 학습 손실 {학습_손실:.4f}, 시험 손실 {시험_손실:.4f}, 시험 정확도 {정확도:.2%}")

torch.save(모델.state_dict(), "fashion_cnn.pt")
print("저장했습니다: fashion_cnn.pt")
