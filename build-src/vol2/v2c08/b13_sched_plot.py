import matplotlib.pyplot as plt
import torch
from torch.optim.lr_scheduler import CosineAnnealingLR, OneCycleLR, StepLR

에폭_수 = 100


def 학습률_기록(스케줄러_만들기) -> list[float]:
    가짜_가중치 = torch.zeros(1, requires_grad=True)
    옵티마이저 = torch.optim.SGD([가짜_가중치], lr=0.1)
    스케줄러 = 스케줄러_만들기(옵티마이저)
    기록 = []
    for 에폭 in range(에폭_수):
        기록.append(옵티마이저.param_groups[0]["lr"])
        옵티마이저.step()
        스케줄러.step()
    return 기록


plt.rcParams["font.family"] = "AppleGothic"
plt.figure(figsize=(7, 3.5))
plt.plot(학습률_기록(lambda o: StepLR(o, step_size=30, gamma=0.5)), label="StepLR")
plt.plot(학습률_기록(lambda o: CosineAnnealingLR(o, T_max=에폭_수)), label="CosineAnnealingLR")
plt.plot(학습률_기록(lambda o: OneCycleLR(o, max_lr=0.1, total_steps=에폭_수)), label="OneCycleLR")
plt.xlabel("에폭")
plt.ylabel("학습률")
plt.legend()
plt.tight_layout()
plt.savefig("lr_schedules.png", dpi=200)
