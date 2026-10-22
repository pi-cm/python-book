# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.8 torch.compile: 모델을 미리 번역해 두기 · manuscript-vol2/chapters/16-gpu-performance.md:940]
import statistics
import time

import torch


def 재기(함수, 반복: int = 30) -> float:
    """준비 운동 뒤 동기화하며 재고 중앙값(ms)을 돌려준다."""
    for _ in range(3):
        함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


def 손으로_쓴_GELU(x: torch.Tensor) -> torch.Tensor:
    """GELU 근사식: 곱하기·더하기·tanh가 여러 번 이어지는 원소별 계산."""
    return 0.5 * x * (1 + torch.tanh(0.7978845608 * (x + 0.044715 * x ** 3)))


x = torch.randn(64 * 1024 * 1024, device="cuda")       # 숫자 6,700만 개 (256MB)
합친_GELU = torch.compile(손으로_쓴_GELU)
print("결과 같음:", torch.allclose(손으로_쓴_GELU(x), 합친_GELU(x), atol=1e-6))

보통 = 재기(lambda: 손으로_쓴_GELU(x))
합침 = 재기(lambda: 합친_GELU(x))
내장 = 재기(lambda: torch.nn.functional.gelu(x, approximate="tanh"))
print(f"보통(eager)   : {보통:6.2f} ms")
print(f"torch.compile : {합침:6.2f} ms ({보통 / 합침:.1f}배)")
print(f"내장 F.gelu   : {내장:6.2f} ms")
대역폭 = 1008e9                                         # RTX 4090 메모리 대역폭 사양: 초당 1008GB
print(f"256MB를 한 번 읽고 한 번 쓰는 최소 시간: {2 * x.numel() * 4 / 대역폭 * 1000:.2f} ms")
