# [2권 Chapter 20. FastAPI로 모델 서빙: 내 모델을 웹 서비스로 · 20.5 여러 장을 한 번에: 배치 추론 · manuscript-vol2/chapters/20-model-serving.md:451]
import statistics
import time

import torch

from 서빙도구 import 모델_불러오기

torch.manual_seed(0)
모델 = 모델_불러오기()
사진들 = torch.rand(512, 1, 28, 28)                      # 시간만 잴 것이라 아무 사진이나


def 시간_재기(배치_크기: int, 반복: int = 7) -> float:
    """사진 512장을 배치_크기씩 나눠 처리할 때, 사진 한 장당 걸린 시간(ms)의 중앙값."""
    기록 = []
    with torch.no_grad():
        모델(사진들[:배치_크기])                           # 준비 운동 (4장 4.8절)
        for _ in range(반복):
            시작 = time.perf_counter()
            for i in range(0, len(사진들), 배치_크기):
                모델(사진들[i:i + 배치_크기])
            기록.append((time.perf_counter() - 시작) * 1000 / len(사진들))
    return statistics.median(기록)


print("배치 크기  한 장당 시간  한 장씩 대비")
기준 = 시간_재기(1)
for 크기 in [1, 8, 32, 128, 512]:
    걸림 = 기준 if 크기 == 1 else 시간_재기(크기)
    print(f"{크기:>7}  {걸림:9.3f}ms  {기준 / 걸림:8.1f}배")
