import statistics
import time

import torch


def 재기(함수, 반복: int = 20) -> float:
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


n = 8192
torch.manual_seed(0)
a64 = torch.randn(n, n, device="cuda", dtype=torch.float64)
b64 = torch.randn(n, n, device="cuda", dtype=torch.float64)
정답 = a64 @ b64                                         # float64로 구한 기준 답

for 이름, 자료형, 정밀도 in [("float32 (highest)", torch.float32, "highest"),
                             ("float32 + TF32 (high)", torch.float32, "high"),
                             ("bfloat16", torch.bfloat16, "highest"),
                             ("float16", torch.float16, "highest")]:
    torch.set_float32_matmul_precision(정밀도)          # float32 행렬 곱에 TF32를 쓸지
    a, b = a64.to(자료형), b64.to(자료형)
    ms = 재기(lambda: a @ b)
    오차 = ((a @ b).double() - 정답).norm() / 정답.norm()
    print(f"{이름:<22} {ms:6.2f} ms | {2 * n ** 3 / ms / 1e9:5.1f} TFLOPS | 상대 오차 {오차.item():.1e}")
torch.set_float32_matmul_precision("highest")           # 기본값으로 되돌리기
