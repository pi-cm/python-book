# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.11 실습: FashionMNIST 옷 사진 분류기 · manuscript-vol2/chapters/06-nn-module.md:1094]
import torch
from torchvision import datasets, transforms

변환 = transforms.ToTensor()            # 사진 → (1, 28, 28) 실수 텐서, 값은 0~1
학습셋 = datasets.FashionMNIST("data", train=True, download=True, transform=변환)
시험셋 = datasets.FashionMNIST("data", train=False, download=True, transform=변환)
print("학습", len(학습셋), "장 / 시험", len(시험셋), "장")
print(학습셋.classes)
print("클래스별 학습 사진 수:", torch.bincount(학습셋.targets).tolist())

사진, 정답 = 학습셋[0]
print(사진.shape, 사진.dtype, f"값 범위 {사진.min():.1f}~{사진.max():.1f}", "정답:", 정답, 학습셋.classes[정답])

# 글자로 그려 보기: 밝을수록 진한 글자, 두 줄에 한 줄만
글자 = " .:-=+*#%@"
for 줄 in 사진[0, ::2]:
    print("".join(글자[min(int(v * 10), 9)] for v in 줄))
