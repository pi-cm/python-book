# [2권 Chapter 8. 학습 잘 시키기 · 8.4 배치 정규화 · manuscript-vol2/chapters/08-training-well.md:525]
import torch

from 학습도구 import 깊은_모델, 데이터_준비, 로더_만들기, 평가, 한_에폭_학습

# 이번에는 정답을 바꾸지 않은 깨끗한 데이터 1,000개로
(X_학습, y_학습), (X_검증, y_검증), _ = 데이터_준비(잡음_비율=0.0, 학습_개수=1000)
for 배치정규화 in (False, True):
    torch.manual_seed(0)
    로더 = 로더_만들기(X_학습, y_학습)
    모델 = 깊은_모델(배치정규화=배치정규화)
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.05)
    기록 = []
    for 에폭 in range(1, 21):
        한_에폭_학습(모델, 로더, 옵티마이저)
        if 에폭 in (1, 3, 5, 10, 20):
            기록.append(f"{에폭}에폭 {평가(모델, X_검증, y_검증)[1]:.0%}")
    print("배치 정규화", "있음:" if 배치정규화 else "없음:", ", ".join(기록))
