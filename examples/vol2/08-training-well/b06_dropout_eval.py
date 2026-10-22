# [2권 Chapter 8. 학습 잘 시키기 · 8.3 드롭아웃 · manuscript-vol2/chapters/08-training-well.md:391]
import torch

from 학습도구 import 데이터_준비, 로더_만들기, 모델_만들기, 한_에폭_학습

(X_학습, y_학습), (X_검증, y_검증), _ = 데이터_준비()
torch.manual_seed(0)
로더 = 로더_만들기(X_학습, y_학습)
모델 = 모델_만들기(드롭아웃=0.5)
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
for 에폭 in range(150):
    한_에폭_학습(모델, 로더, 옵티마이저)

숫자 = X_검증[:1]                             # 검증 데이터의 첫 숫자 하나
with torch.no_grad():
    모델.train()                              # eval()을 깜빡했다면
    print("train 모드:", [round(모델(숫자).softmax(dim=1).max().item(), 4) for _ in range(3)])
    모델.eval()
    print("eval 모드 :", [round(모델(숫자).softmax(dim=1).max().item(), 4) for _ in range(3)])

    for 모드 in ("train", "eval"):
        getattr(모델, 모드)()
        정확도 = (모델(X_검증).argmax(dim=1) == y_검증).float().mean().item()
        print(f"{모드} 모드 검증 정확도: {정확도:.1%}")
