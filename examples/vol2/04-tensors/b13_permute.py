# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.5 모양 바꾸기 · manuscript-vol2/chapters/04-tensors.md:630]
import torch

# 사진 파일을 읽으면 보통 (세로, 가로, 색) 순서
사진 = torch.zeros(224, 224, 3)
파이토치용 = 사진.permute(2, 0, 1)     # (색, 세로, 가로)로 순서 바꾸기
print(사진.shape, "→", 파이토치용.shape)

행렬 = torch.arange(6).reshape(2, 3)
print(행렬.T)                          # 2차원은 .T로 전치
print(행렬.T.is_contiguous())          # 순서만 바꿔 본 것이라 메모리는 그대로

try:
    행렬.T.view(6)
except RuntimeError as e:
    print("view 오류:", str(e).split(".")[0])
print(행렬.T.reshape(6))               # reshape는 필요하면 복사해서 해결
