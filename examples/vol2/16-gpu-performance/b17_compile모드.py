# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.8 torch.compile: 모델을 미리 번역해 두기 · manuscript-vol2/chapters/16-gpu-performance.md:996]
import statistics
import time

import torch
from torch import nn


def 재기(함수, 반복: int = 200) -> float:
    """준비 운동 뒤 동기화하며 재고 중앙값(ms)을 돌려준다."""
    for _ in range(10):
        함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


# 작은 모델, 작은 배치: 계산보다 "GPU에 일을 맡기는 비용"이 큰 경우
torch.manual_seed(0)
층들 = []
for _ in range(8):
    층들 += [nn.Linear(256, 256), nn.LayerNorm(256), nn.GELU()]
모델 = nn.Sequential(*층들).to("cuda").eval()
x = torch.randn(16, 256, device="cuda")

for 모드 in [None, "default", "reduce-overhead"]:
    torch.compiler.reset()                             # 앞에서 컴파일한 것을 지운다
    실행 = 모델 if 모드 is None else torch.compile(모델, mode=모드)
    with torch.no_grad():
        시작 = time.perf_counter()
        실행(x)
        torch.cuda.synchronize()
        준비 = time.perf_counter() - 시작
        ms = 재기(lambda: 실행(x))
    print(f"{모드 or 'eager':<16} 첫 호출 {준비:5.2f}초 | 그다음부터 한 번에 {ms:6.3f} ms")
