# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.2 활성화 함수: 직선을 구부리는 장치 · manuscript-vol2/chapters/06-nn-module.md:198]
import torch

# 사진 2장 × 클래스 3개(고양이, 개, 새)에 대한 모델의 점수
로짓 = torch.tensor([[2.0, 1.0, 0.1],
                    [0.5, 0.5, 3.0]])

확률 = torch.softmax(로짓, dim=1)      # 클래스 방향(dim=1)으로 합이 1
print(확률)
print("줄마다 합:", 확률.sum(dim=1))
print("고른 클래스:", 확률.argmax(dim=1), 로짓.argmax(dim=1))

print(torch.softmax(로짓 * 10, dim=1).round(decimals=4))   # 점수 차이를 10배로
print(torch.softmax(torch.tensor([1000.0, 0.0]), dim=0))    # 큰 숫자도 안전
