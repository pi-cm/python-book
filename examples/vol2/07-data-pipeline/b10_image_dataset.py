# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.5 직접 만든 Dataset ②: 이미지 폴더 · manuscript-vol2/chapters/07-data-pipeline.md:493]
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision.datasets import ImageFolder

from 도형_만들기 import 도형_폴더_만들기

뿌리 = Path("data/shapes")
도형_폴더_만들기(뿌리, {"circle": 20, "square": 20, "triangle": 20})


class 그림폴더_데이터셋(Dataset):
    """뿌리/클래스이름/파일.png 구조의 폴더를 읽는다."""

    def __init__(self, 뿌리: Path) -> None:
        self.클래스들 = sorted(p.name for p in 뿌리.iterdir() if p.is_dir())
        self.클래스_번호 = {이름: i for i, 이름 in enumerate(self.클래스들)}
        # 그림을 읽지 않고 (경로, 정답) 목록만 만들어 둔다
        self.목록 = [(경로, self.클래스_번호[이름])
                     for 이름 in self.클래스들
                     for 경로 in sorted((뿌리 / 이름).glob("*.png"))]

    def __len__(self) -> int:
        return len(self.목록)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, int]:
        경로, 정답 = self.목록[i]
        with Image.open(경로) as 그림:                   # 필요한 그 순간에 파일을 연다
            배열 = np.array(그림.convert("RGB"))          # (세로, 가로, 색), 0~255 정수
        텐서 = torch.from_numpy(배열).permute(2, 0, 1)   # (색, 세로, 가로)
        return 텐서.float() / 255, 정답


우리것 = 그림폴더_데이터셋(뿌리)
print("클래스:", 우리것.클래스_번호, "샘플 수:", len(우리것))
그림, 정답 = 우리것[25]
print("25번:", tuple(그림.shape), 그림.dtype, "정답", 정답, "경로", 우리것.목록[25][0].name)

기성품 = ImageFolder(뿌리)                               # torchvision이 준비해 둔 같은 기능
print("ImageFolder:", 기성품.class_to_idx, len(기성품))
그림2, 정답2 = 기성품[25]
print("25번:", type(그림2).__name__, 그림2.size, "정답", 정답2, 기성품.samples[25][0])
