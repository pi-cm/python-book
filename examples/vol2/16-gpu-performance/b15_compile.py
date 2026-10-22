# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.8 torch.compile: 모델을 미리 번역해 두기 · manuscript-vol2/chapters/16-gpu-performance.md:865]
import statistics
import time

import torch
import torch.nn.functional as F
from torch import nn

어휘, 길이, 배치 = 1000, 256, 32


class 작은_GPT(nn.Module):
    """16.6절과 같은 작은 GPT."""

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


def 걸음_시간들(모델: nn.Module, 걸음_수: int = 60) -> list[float]:
    """bfloat16 autocast로 학습 걸음을 밟으며 걸음마다 걸린 시간(ms)을 모은다."""
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=3e-4)
    생성기 = torch.Generator(device="cuda").manual_seed(0)
    시간들 = []
    for _ in range(걸음_수):
        시작 = time.perf_counter()
        데이터 = torch.randint(0, 어휘, (배치, 길이 + 1), device="cuda", generator=생성기)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            손실 = F.cross_entropy(모델(데이터[:, :-1]).flatten(0, 1), 데이터[:, 1:].flatten())
        옵티마이저.zero_grad(set_to_none=True)
        손실.backward()
        옵티마이저.step()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return 시간들


torch.manual_seed(0)
보통 = 걸음_시간들(작은_GPT().to("cuda"))
torch.manual_seed(0)
컴파일 = 걸음_시간들(torch.compile(작은_GPT().to("cuda")))   # 모델을 감싸기만 하면 된다

print(f"보통(eager) : 첫 걸음 {보통[0] / 1000:5.1f}초, 이후 걸음당 {statistics.median(보통[10:]):5.1f} ms")
print(f"compile     : 첫 걸음 {컴파일[0] / 1000:5.1f}초, 이후 걸음당 {statistics.median(컴파일[10:]):5.1f} ms")
print(f"걸음당 {statistics.median(보통[10:]) / statistics.median(컴파일[10:]):.2f}배 빨라짐")
