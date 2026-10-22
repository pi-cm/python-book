from dataclasses import asdict, replace

import torch
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from torch.utils.tensorboard import SummaryWriter

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

기준 = 학습설정(에폭=4, 학습_개수=10_000)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(기준.학습_개수)

for 학습률 in (1e-3, 1e-2):
    설정 = replace(기준, 학습률=학습률)
    씨앗_고정(설정.씨앗)
    모델 = 모델_만들기(설정)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=설정.학습률)
    로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
    with SummaryWriter(f"tb/lr{학습률:g}") as 쓰개:           # 실험마다 폴더 하나
        for 에폭 in range(1, 설정.에폭 + 1):
            학습_손실 = 한_에폭_학습(모델, 로더, 옵티마이저)
            검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
            쓰개.add_scalar("손실/학습", 학습_손실, 에폭)       # 이름의 / 앞이 같으면 한 칸에 모인다
            쓰개.add_scalar("손실/검증", 검증_손실, 에폭)
            쓰개.add_scalar("정확도/검증", 검증_정확도, 에폭)
        쓰개.add_histogram("가중치/첫층", 모델[1].weight, 에폭)
        쓰개.add_hparams(asdict(설정), {"최종/검증_정확도": 검증_정확도}, run_name=".")

# 파일에 무엇이 들어갔는지 TensorBoard의 읽기 도구로 확인
for 폴더 in ("tb/lr0.001", "tb/lr0.01"):
    읽개 = EventAccumulator(폴더).Reload()
    print(폴더, "→", 읽개.Tags()["scalars"])
    print("  검증 정확도:", [round(e.value, 4) for e in 읽개.Scalars("정확도/검증")])
