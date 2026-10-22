# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.9 텐서 저장하고 불러오기 · manuscript-vol2/chapters/04-tensors.md:1186]
import tempfile
from pathlib import Path

import torch


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


x = torch.arange(3.0, device=장치_고르기())
with tempfile.TemporaryDirectory() as 폴더:
    경로 = Path(폴더) / "x.pt"
    torch.save(x, 경로)
    print(torch.load(경로).device)                         # 저장할 때의 장치로 돌아온다
    print(torch.load(경로, map_location="cpu").device)     # 불러오면서 CPU로
