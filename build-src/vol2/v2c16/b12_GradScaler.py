import math

import torch
from torch import nn

torch.manual_seed(0)
모델 = nn.Linear(1024, 1024).to("cuda")
x = torch.randn(256, 1024, device="cuda")


def 기울기_구하기(배율: float) -> torch.Tensor:
    """float16 autocast로 계산하고, 손실에 배율을 곱해 backward한 뒤 배율로 다시 나눈다."""
    모델.zero_grad()
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        출력 = 모델(x)
    손실 = 출력.float().pow(2).mean() * 1e-3        # 학습 막바지처럼 아주 작은 손실
    (손실 * 배율).backward()
    return 모델.weight.grad / 배율


# 기준: autocast 없이 float32로만 계산한 기울기
모델.zero_grad()
(모델(x).pow(2).mean() * 1e-3).backward()
기준 = 모델.weight.grad.clone()

for 배율 in [1.0, 2.0 ** 16]:
    기울기 = 기울기_구하기(배율)
    print(f"배율 {배율:>7.0f}: 0이 된 기울기 {(기울기 == 0).float().mean():6.1%}, "
          f"float32 기준과의 상대 오차 {((기울기 - 기준).norm() / 기준.norm()).item():.4f}")

# 실제 학습에서는 GradScaler가 배율을 알아서 관리한다
옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.1)
스케일러 = torch.amp.GradScaler("cuda", init_scale=2.0 ** 40)   # 일부러 너무 큰 배율로 시작
걸음, 갱신_횟수 = 0, 0
while 갱신_횟수 < 2:                                # 가중치를 두 번 갱신할 때까지
    옵티마이저.zero_grad()
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        손실 = 모델(x).float().pow(2).mean() * 1e-3
    스케일러.scale(손실).backward()                 # 손실에 배율을 곱해 backward
    배율 = 스케일러.get_scale()
    스케일러.step(옵티마이저)                       # 기울기를 배율로 나누고, inf가 있으면 건너뛴다
    스케일러.update()                               # inf가 있었으면 배율을 반으로
    결과 = "inf 발견, 이번 걸음은 건너뜀" if 스케일러.get_scale() < 배율 else "정상, 가중치 갱신"
    print(f"걸음 {걸음}: 배율 2^{math.log2(배율):.0f} → {결과}")
    갱신_횟수 += 결과.startswith("정상")
    걸음 += 1
