import math
import statistics
import time

import torch
import torch.nn.functional as F
from torch.nn.attention import SDPBackend, sdpa_kernel


def 재기(함수, 반복: int = 10) -> float:
    """준비 운동 뒤 동기화하며 재고 중앙값(ms)을 돌려준다."""
    함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


def 직접_어텐션(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    """12장에서 직접 쓴 인과 어텐션: 점수 표를 통째로 만든다."""
    점수 = q @ k.transpose(-2, -1) / math.sqrt(q.shape[-1])
    T = q.shape[-2]
    미래 = torch.ones(T, T, dtype=torch.bool, device=q.device).triu(1)
    return 점수.masked_fill(미래, float("-inf")).softmax(dim=-1) @ v


def SDPA(백엔드: SDPBackend):
    """계산법(백엔드)을 하나로 정해서 scaled_dot_product_attention을 부르는 함수."""
    def 실행(q, k, v):
        with sdpa_kernel(백엔드):
            return F.scaled_dot_product_attention(q, k, v, is_causal=True)
    return 실행


방법들 = {"직접 계산": 직접_어텐션, "SDPA 수학": SDPA(SDPBackend.MATH),
          "SDPA 메모리 효율": SDPA(SDPBackend.EFFICIENT_ATTENTION),
          "SDPA 플래시": SDPA(SDPBackend.FLASH_ATTENTION)}
if torch.cuda.get_device_capability() < (8, 0):     # 플래시는 계산 능력 8.0 이상에서만 돈다
    del 방법들["SDPA 플래시"]                         # (Colab의 T4 같은 GPU에서는 빼고 잰다)
GB = 1024 ** 3
torch.manual_seed(0)
for T in [1024, 4096]:
    q, k, v = (torch.randn(8, 16, T, 64, device="cuda", dtype=torch.float16) for _ in range(3))
    기준 = 직접_어텐션(q, k, v)
    print(f"[글자 {T}개] 배치 8, 헤드 16, 헤드 크기 64, float16")
    for 이름, 함수 in 방법들.items():
        torch.cuda.reset_peak_memory_stats()
        전 = torch.cuda.memory_allocated()
        ms = 재기(lambda: 함수(q, k, v))
        추가 = (torch.cuda.max_memory_allocated() - 전) / GB
        같은가 = torch.allclose(함수(q, k, v), 기준, atol=1e-2)
        print(f"  {ms:7.2f} ms | 추가 메모리 {추가:5.2f} GB | 결과 같음 {같은가} ← {이름}")
