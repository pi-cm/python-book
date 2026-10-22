# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.2 모양과 차원 · manuscript-vol2/chapters/04-tensors.md:256]
import torch

# 컬러 사진 32장 묶음: (장 수, 색 채널, 세로, 가로)
사진_묶음 = torch.zeros(32, 3, 224, 224)
print(사진_묶음.shape)
print(f"숫자 {사진_묶음.numel():,}개, 차원 {사진_묶음.ndim}개")
print("첫 사진의 모양:", 사진_묶음[0].shape)
