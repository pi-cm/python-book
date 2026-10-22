# [2권 Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기 · 17.3 활성화 체크포인팅: 적어 두지 말고 다시 계산하기 · manuscript-vol2/chapters/17-distributed-training.md:280]
import statistics
import time

import torch
from torch import nn
from torch.utils.checkpoint import checkpoint

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 있어야 합니다"
장치 = torch.device("cuda")
GB = 1024 ** 3


class 트랜스포머(nn.Module):
    """12장의 인코더 층을 쌓은 모델. 체크포인트=True면 층마다 활성화를 버리고 다시 계산한다."""

    def __init__(self, 층수: int, 체크포인트: bool) -> None:
        super().__init__()
        self.층들 = nn.ModuleList(
            nn.TransformerEncoderLayer(1024, 16, 4096, dropout=0.1, batch_first=True)
            for _ in range(층수))
        self.체크포인트 = 체크포인트

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for 층 in self.층들:
            if self.체크포인트 and self.training:
                x = checkpoint(층, x, use_reentrant=False)   # 층의 중간 결과를 저장하지 않는다
            else:
                x = 층(x)
        return x


x = torch.randn(16, 512, 1024, device=장치)       # 예제용 입력: 16문장 × 512토큰
결과 = {}
for 체크포인트 in (False, True):
    torch.manual_seed(0)
    모델 = 트랜스포머(12, 체크포인트).to(장치)
    시간들 = []
    for 번째 in range(6):
        모델.zero_grad()
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        시작 = time.perf_counter()
        torch.manual_seed(번째)                       # 드롭아웃 난수를 두 방식에서 똑같이
        모델(x).pow(2).mean().backward()
        torch.cuda.synchronize()
        시간들.append(time.perf_counter() - 시작)
    결과[체크포인트] = [p.grad.clone() for p in 모델.parameters()]
    개수 = sum(p.numel() for p in 모델.parameters())
    print(f"체크포인팅 {'켬' if 체크포인트 else '끔'}: 최고 메모리 "
          f"{torch.cuda.max_memory_allocated() / GB:5.2f} GB, "
          f"forward+backward {statistics.median(시간들[1:]) * 1000:4.0f} ms")
    del 모델

print(f"파라미터 {개수:,}개 (float32로 {개수 * 4 / GB:.2f} GB)")
같은가 = all(torch.allclose(a, b, atol=1e-6) for a, b in zip(결과[False], 결과[True]))
print("두 방식의 기울기가 같은가:", 같은가)
