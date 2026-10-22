# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.1 오토인코더: 줄였다가 되살리기 · manuscript-vol2/chapters/15-generative-models.md:205]
import torch
import torch.nn.functional as F

from 생성도구 import 사진_불러오기, 오토인코더, 오토인코더_학습

X_학습, _ = 사진_불러오기(학습=True)
X_시험, _ = 사진_불러오기(학습=False)

# 비교 대상: 직선(선형)으로만 줄이는 PCA. 학습 사진의 평균과 주성분 방향을 구한다
평균 = X_학습.flatten(1).mean(dim=0)
_, _, V = torch.linalg.svd(X_학습.flatten(1) - 평균, full_matrices=False)


def pca_재구성_손실(k: int) -> float:
    """주성분 k개로 줄였다가 되살렸을 때의 시험 사진 MSE."""
    방향 = V[:k].T                                  # (784, k)
    줄임 = (X_시험.flatten(1) - 평균) @ 방향         # (10000, k)
    복원 = 줄임 @ 방향.T + 평균                      # (10000, 784)
    return F.mse_loss(복원, X_시험.flatten(1)).item()


print("잠재 크기  오토인코더  PCA")
for k in [2, 8, 32, 128]:
    torch.manual_seed(0)
    모델 = 오토인코더_학습(오토인코더(잠재_크기=k), X_학습, 에폭=5, 출력=False).eval()
    with torch.no_grad():
        손실 = F.mse_loss(모델(X_시험), X_시험).item()
    print(f"{k:8}  {손실:10.4f}  {pca_재구성_손실(k):.4f}")
