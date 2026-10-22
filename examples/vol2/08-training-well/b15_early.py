# [2권 Chapter 8. 학습 잘 시키기 · 8.8 조기 종료 · manuscript-vol2/chapters/08-training-well.md:773]
import copy

import torch
from torch import nn

from 학습도구 import 데이터_준비, 로더_만들기, 모델_만들기, 평가, 한_에폭_학습


class 조기_종료:
    """검증 손실이 참을성(patience) 에폭 동안 나아지지 않으면 멈추라고 알려 준다."""

    def __init__(self, 참을성: int = 10, 최소_개선: float = 0.0) -> None:
        self.참을성 = 참을성
        self.최소_개선 = 최소_개선
        self.최고_손실 = float("inf")
        self.최고_에폭 = 0
        self.최고_가중치: dict | None = None
        self.나빠진_횟수 = 0

    def 확인(self, 에폭: int, 검증_손실: float, 모델: nn.Module) -> bool:
        """멈춰야 하면 True를 돌려준다."""
        if 검증_손실 < self.최고_손실 - self.최소_개선:
            self.최고_손실 = 검증_손실
            self.최고_에폭 = 에폭
            self.최고_가중치 = copy.deepcopy(모델.state_dict())   # 복사해서 보관
            self.나빠진_횟수 = 0
        else:
            self.나빠진_횟수 += 1
        return self.나빠진_횟수 >= self.참을성


(X_학습, y_학습), (X_검증, y_검증), _ = 데이터_준비()
torch.manual_seed(0)
로더 = 로더_만들기(X_학습, y_학습)
모델 = 모델_만들기()
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
멈춤이 = 조기_종료(참을성=20)

for 에폭 in range(1, 501):
    한_에폭_학습(모델, 로더, 옵티마이저)
    검증_손실, _ = 평가(모델, X_검증, y_검증)
    if 멈춤이.확인(에폭, 검증_손실, 모델):
        print(f"{에폭}에폭에서 멈춤 (최고 기록: {멈춤이.최고_에폭}에폭, 손실 {멈춤이.최고_손실:.4f})")
        break

print("멈춘 시점 검증 (손실, 정확도):", [round(v, 4) for v in 평가(모델, X_검증, y_검증)])
모델.load_state_dict(멈춤이.최고_가중치)       # 가장 좋았던 가중치로 되돌리기
print("되돌린 뒤 검증 (손실, 정확도):", [round(v, 4) for v in 평가(모델, X_검증, y_검증)])
