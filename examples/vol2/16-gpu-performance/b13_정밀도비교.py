# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.6 혼합 정밀도: 16비트로 계산하기 · manuscript-vol2/chapters/16-gpu-performance.md:715]
import statistics
import time

import torch
import torch.nn.functional as F
from torch import nn

어휘, 길이, 배치 = 1000, 256, 32


class 작은_GPT(nn.Module):
    """12장의 작은 GPT와 같은 모양을 PyTorch 부품(nn.TransformerEncoder)으로 짧게 쓴 것."""

    def __init__(self, 차원: int = 512, 층: int = 6, 헤드: int = 8) -> None:
        super().__init__()
        self.글자 = nn.Embedding(어휘, 차원)
        self.위치 = nn.Embedding(길이, 차원)
        블록 = nn.TransformerEncoderLayer(차원, 헤드, 4 * 차원, dropout=0.0,
                                          batch_first=True, norm_first=True)
        self.몸통 = nn.TransformerEncoder(블록, 층, enable_nested_tensor=False)
        self.머리 = nn.Linear(차원, 어휘)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        T = x.shape[1]
        h = self.글자(x) + self.위치(torch.arange(T, device=x.device))
        마스크 = nn.Transformer.generate_square_subsequent_mask(T, device=x.device)
        return self.머리(self.몸통(h, mask=마스크, is_causal=True))


def 배치_만들기() -> torch.Tensor:
    """예제용으로 만든 규칙 데이터: 줄마다 시작 글자와 간격을 정해 일정하게 늘어나는 번호."""
    시작 = torch.randint(0, 어휘, (배치, 1), device="cuda")
    간격 = torch.randint(1, 20, (배치, 1), device="cuda")
    return (시작 + 간격 * torch.arange(길이 + 1, device="cuda")) % 어휘


def 학습(방식: str, 걸음_수: int = 200) -> tuple[float, float, float]:
    """방식대로 학습하고 (걸음당 ms, 최고 메모리 GB, 마지막 20걸음 평균 손실)을 돌려준다."""
    torch.manual_seed(0)
    모델 = 작은_GPT().to("cuda")
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=3e-4)
    자료형 = {"float32": None, "float16": torch.float16, "bfloat16": torch.bfloat16}[방식]
    스케일러 = torch.amp.GradScaler("cuda", enabled=(방식 == "float16"))  # float16일 때만 켠다
    torch.cuda.reset_peak_memory_stats()
    시간들, 손실들 = [], []
    for _ in range(걸음_수):
        시작 = time.perf_counter()
        데이터 = 배치_만들기()
        x, y = 데이터[:, :-1], 데이터[:, 1:]
        with torch.autocast("cuda", dtype=자료형, enabled=자료형 is not None):
            손실 = F.cross_entropy(모델(x).flatten(0, 1), y.flatten())
        옵티마이저.zero_grad(set_to_none=True)
        스케일러.scale(손실).backward()
        스케일러.step(옵티마이저)
        스케일러.update()
        손실들.append(손실.item())                   # .item()이 GPU를 기다려 준다
        시간들.append((time.perf_counter() - 시작) * 1000)
    return (statistics.median(시간들[10:]), torch.cuda.max_memory_allocated() / 1024 ** 3,
            statistics.mean(손실들[-20:]))


for 방식 in ["float32", "float16", "bfloat16"]:
    ms, 메모리, 손실 = 학습(방식)
    print(f"{방식:<9} 걸음당 {ms:5.1f} ms | 최고 메모리 {메모리:5.2f} GB | 마지막 손실 {손실:.4f}")
