# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.4 재구성 오차로 이상한 것 찾기 · manuscript-vol2/chapters/15-generative-models.md:410]
import torch

from 생성도구 import 사진_불러오기, 오토인코더, 오토인코더_학습, 이름

X_학습, y_학습 = 사진_불러오기(학습=True)
X_시험, y_시험 = 사진_불러오기(학습=False)

# 가방(8번)을 한 장도 보여 주지 않고 나머지 아홉 종류로만 학습한다
torch.manual_seed(0)
모델 = 오토인코더_학습(오토인코더(잠재_크기=8), X_학습[y_학습 != 8], 에폭=5, 출력=False).eval()

with torch.no_grad():
    오차 = ((모델(X_시험) - X_시험) ** 2).flatten(1).mean(dim=1)   # 사진 한 장마다 재구성 오차

for 번호 in range(10):
    print(f"{이름[번호]:5} 평균 재구성 오차 {오차[y_시험 == 번호].mean():.4f}")

# 문턱: 학습한 종류의 시험 사진 중 95%가 넘지 않는 오차
문턱 = 오차[y_시험 != 8].quantile(0.95)
print(f"\n문턱 {문턱:.4f}를 넘으면 '이상'으로 판정")
print(f"가방이 이상으로 잡힌 비율: {(오차[y_시험 == 8] > 문턱).float().mean():.1%}")
print(f"다른 옷이 이상으로 잡힌 비율: {(오차[y_시험 != 8] > 문턱).float().mean():.1%}")
