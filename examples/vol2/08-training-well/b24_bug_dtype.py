# [2권 Chapter 8. 학습 잘 시키기 · 8.11 손실이 안 줄 때 디버깅 · manuscript-vol2/chapters/08-training-well.md:1280]
import torch
from torch import nn

출력 = torch.randn(4, 10)                     # 샘플 4개 × 클래스 10개
정답_실수 = torch.tensor([3.0, 1.0, 0.0, 7.0])   # 예: pandas에서 실수로 읽힌 정답
try:
    nn.CrossEntropyLoss()(출력, 정답_실수)
except RuntimeError as e:
    print("오류:", e)
print("고친 뒤:", nn.CrossEntropyLoss()(출력, 정답_실수.long()).item() > 0)

# 회귀에서는 모양이 어긋나도 오류 없이 계산된다
torch.manual_seed(0)
예측 = torch.randn(4, 1)                      # 모델 출력은 (4, 1)
정답 = torch.randn(4)                         # 정답은 (4,)
print(f"모양이 어긋난 손실: {nn.functional.mse_loss(예측, 정답).item():.4f}")
print(f"모양을 맞춘 손실  : {nn.functional.mse_loss(예측.squeeze(1), 정답).item():.4f}")
print("(예측 - 정답)의 모양:", tuple((예측 - 정답).shape))
