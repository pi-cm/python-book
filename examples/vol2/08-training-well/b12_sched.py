# [2권 Chapter 8. 학습 잘 시키기 · 8.7 학습률 스케줄러 · manuscript-vol2/chapters/08-training-well.md:670]
import torch
from torch.optim.lr_scheduler import CosineAnnealingLR, OneCycleLR, StepLR

에폭_수 = 10


def 학습률_기록(스케줄러_만들기) -> list[float]:
    """에폭마다 옵티마이저의 학습률을 적어 둔다."""
    가짜_가중치 = torch.zeros(1, requires_grad=True)   # 학습률만 볼 것이라 아무 값이나
    옵티마이저 = torch.optim.SGD([가짜_가중치], lr=0.1)
    스케줄러 = 스케줄러_만들기(옵티마이저)
    기록 = []
    for 에폭 in range(에폭_수):
        기록.append(옵티마이저.param_groups[0]["lr"])
        옵티마이저.step()                     # (실제로는 여기서 한 에폭 학습)
        스케줄러.step()                       # 그다음에 학습률 갱신
    return 기록


기록들 = {
    "StepLR": 학습률_기록(lambda o: StepLR(o, step_size=3, gamma=0.5)),
    "Cosine": 학습률_기록(lambda o: CosineAnnealingLR(o, T_max=에폭_수)),
    "OneCycle": 학습률_기록(lambda o: OneCycleLR(o, max_lr=0.1, total_steps=에폭_수)),
}
print("에폭  " + "".join(f"{이름:>10}" for 이름 in 기록들))
for 에폭 in range(에폭_수):
    print(f"{에폭:4d}  " + "".join(f"{값[에폭]:10.4f}" for 값 in 기록들.values()))
