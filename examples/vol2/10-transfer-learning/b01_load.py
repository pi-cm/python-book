# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.1 사전학습 모델 불러오기 · manuscript-vol2/chapters/10-transfer-learning.md:33]
import torch
from torchvision import models

가중치 = models.ResNet18_Weights.DEFAULT        # ImageNet으로 미리 학습한 가중치
모델 = models.resnet18(weights=가중치)           # 처음 한 번은 약 45MB를 내려받는다
print(가중치)

개수 = sum(p.numel() for p in 모델.parameters())
바이트 = sum(p.numel() * p.element_size() for p in 모델.parameters())
print(f"파라미터 {개수:,}개, float32로 {바이트 / 1024**2:.1f}MB")
print(f"모델 카드에 적힌 개수 {가중치.meta['num_params']:,}개, 파일 {가중치.meta['_file_size']}MB")
print("ImageNet 검증 데이터 정확도(top-1):", 가중치.meta["_metrics"]["ImageNet-1K"]["acc@1"], "%")
범주 = 가중치.meta["categories"]
print(f"알아보는 범주 {len(범주)}가지:", 범주[:3], "...", 범주[-2:])
