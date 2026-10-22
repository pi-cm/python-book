# [2권 Chapter 8. 학습 잘 시키기 · 8.9 그래디언트 클리핑 · manuscript-vol2/chapters/08-training-well.md:847]
import torch
from torch import nn

torch.manual_seed(0)
X = torch.randn(64, 10)
y = X @ torch.randn(10, 1)                    # 예제용 회귀 데이터
y[:2] = 300.0                                 # 잘못 들어간 값 두 개 (이상치)


def 학습(자를까: bool) -> None:
    torch.manual_seed(0)
    모델 = nn.Sequential(nn.Linear(10, 32), nn.ReLU(), nn.Linear(32, 1))
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.05)
    for 단계 in range(1, 201):
        옵티마이저.zero_grad()
        손실 = nn.functional.mse_loss(모델(X), y)
        손실.backward()
        # 자르기 전의 전체 그래디언트 크기를 돌려준다 (자르지 않을 때는 max_norm을 무한대로)
        크기 = nn.utils.clip_grad_norm_(모델.parameters(),
                                        max_norm=1.0 if 자를까 else float("inf"))
        옵티마이저.step()
        if 단계 in (1, 10, 12, 13, 14, 15, 200):
            print(f"  {단계:3d}단계 손실 {손실.item():12.4g}  그래디언트 크기 {크기.item():10.4g}")


print("그래디언트 클리핑 없음")
학습(자를까=False)
print("그래디언트 클리핑 (max_norm=1.0)")
학습(자를까=True)
