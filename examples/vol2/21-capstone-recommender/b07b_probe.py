# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.7 학습된 임베딩 들여다보기 · manuscript-vol2/chapters/21-capstone-recommender.md:749]
import numpy as np
import torch

from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 추천학습 import 행렬분해, 학습설정, 학습하기, 좋았던_쌍

데이터 = 데이터_만들기(씨앗=0)
학습, _, _ = 시간으로_나누기(데이터.방문)
식당 = 데이터.식당
torch.manual_seed(0)
모델 = 행렬분해(len(데이터.사용자), len(식당), 차원=32)
학습하기(모델, 좋았던_쌍(학습), torch.tensor(np.flatnonzero(식당["개업일"] < 300)),
        학습설정(손실="bpr"))


def 설명력(X: torch.Tensor, y: torch.Tensor, 배울: np.ndarray, 볼: np.ndarray) -> float:
    """배울 식당들로 X → y 직선을 맞추고(최소 제곱), 볼 식당들에서 R²를 잰다(3장 3.8절)."""
    X = torch.cat([X, torch.ones(len(X), 1)], dim=1)       # 절편 칸
    w = torch.linalg.lstsq(X[배울], y[배울, None]).solution
    오차 = y[볼] - (X[볼] @ w)[:, 0]
    return (1 - 오차.pow(2).sum() / (y[볼] - y[볼].mean()).pow(2).sum()).item()


아는 = np.flatnonzero(식당["개업일"] < 300)
배울, 볼 = 아는[아는 % 2 == 0], 아는[아는 % 2 == 1]              # 짝수 번호로 배우고 홀수로 확인
원핫 = torch.nn.functional.one_hot
보이는_특징 = torch.cat([원핫(torch.tensor(식당["지역"].to_numpy()), 8),
                     원핫(torch.tensor(식당["음식"].to_numpy()), 8),
                     torch.tensor(식당["가격대"].to_numpy())[:, None]], dim=1).float()
임베딩 = 모델.식당.weight.detach()
편향 = 모델.편향.weight.detach()

print("보이는 특징  학습된 임베딩  임베딩+편향 | 맞힐 숨은 성질")
for 열 in ["숨은_매운맛", "숨은_분위기", "숨은_품질"]:
    y = torch.tensor(식당[열].to_numpy()).float()
    결과 = [설명력(X, y, 배울, 볼) for X in (보이는_특징, 임베딩, torch.cat([임베딩, 편향], dim=1))]
    print(f"{결과[0]:11.3f} {결과[1]:14.3f} {결과[2]:12.3f} | {열}")

방문수 = np.bincount(학습["식당"], minlength=len(식당))[아는]
print(f"편향과 log(방문 수)의 상관계수: {np.corrcoef(편향[아는, 0], np.log1p(방문수))[0, 1]:.3f}")
