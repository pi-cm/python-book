# [2권 Chapter 8. 학습 잘 시키기 · 8.2 가중치 감쇠(weight decay) · manuscript-vol2/chapters/08-training-well.md:304]
import torch

from 학습도구 import 데이터_준비, 로더_만들기, 모델_만들기, 평가, 한_에폭_학습

(X_학습, y_학습), (X_검증, y_검증), _ = 데이터_준비()

print("weight_decay  가중치크기  학습손실  검증손실  검증정확도")
for wd in [0.0, 0.01, 0.1, 1.0, 3.0, 10.0]:
    torch.manual_seed(0)
    로더 = 로더_만들기(X_학습, y_학습)
    모델 = 모델_만들기()
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=1e-3, weight_decay=wd)
    for 에폭 in range(150):
        한_에폭_학습(모델, 로더, 옵티마이저)
    크기 = sum((p ** 2).sum() for p in 모델.parameters()).sqrt().item()
    학습_손실, _ = 평가(모델, X_학습, y_학습)
    검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
    print(f"{wd:12}  {크기:10.2f}  {학습_손실:8.3f}  {검증_손실:8.3f}  {검증_정확도:9.1%}")
