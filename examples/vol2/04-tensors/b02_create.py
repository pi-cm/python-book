# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.1 텐서 만들기 · manuscript-vol2/chapters/04-tensors.md:65]
import torch

기온 = torch.tensor([12.5, 14.1, 13.0])      # 실수 목록 → 실수 텐서
인원 = torch.tensor([3, 5, 2])               # 정수 목록 → 정수 텐서
합격 = torch.tensor([True, False, True])     # 참/거짓 목록 → 불리언 텐서

print(기온, 기온.dtype)
print(인원, 인원.dtype)
print(합격, 합격.dtype)
