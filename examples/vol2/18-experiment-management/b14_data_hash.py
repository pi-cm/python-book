# [2권 Chapter 18. 실험 관리와 재현성 · 18.7 데이터·코드·환경 버전 기록 · manuscript-vol2/chapters/18-experiment-management.md:1095]
import hashlib
import os
from pathlib import Path

import torch

from 실험도구 import 옷_데이터


def 파일_지문(파일: Path, 조각: int = 1 << 20) -> str:
    """큰 파일도 1MB씩 읽어 가며 SHA-256 해시를 낸다."""
    해시 = hashlib.sha256()
    with 파일.open("rb") as f:
        while 덩어리 := f.read(조각):
            해시.update(덩어리)
    return 해시.hexdigest()


def 텐서_지문(*텐서들: torch.Tensor) -> str:
    """텐서 안의 숫자(와 모양)가 같으면 같은 지문."""
    해시 = hashlib.sha256()
    for t in 텐서들:
        해시.update(str(tuple(t.shape)).encode())
        해시.update(t.contiguous().numpy().tobytes())
    return 해시.hexdigest()


for 파일 in sorted(Path(os.environ.get("BOOK_DATA_DIR", "data"), "FashionMNIST", "raw").glob("*-ubyte")):
    print(f"{파일.name:28} {파일.stat().st_size:>10,}바이트  {파일_지문(파일)[:16]}")

(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(학습_개수=10_000)
print("학습 데이터 지문      :", 텐서_지문(X_학습, y_학습)[:16])
print("다시 나눠도           :", 텐서_지문(*옷_데이터(학습_개수=10_000)[0])[:16])
X_한점 = X_학습.clone()
X_한점[0, 0, 14, 14] += 1 / 255                     # 사진 한 장의 점 하나를 한 단계 밝게
print("점 하나만 바꿔도      :", 텐서_지문(X_한점, y_학습)[:16])
print("검증 데이터 지문      :", 텐서_지문(X_검증, y_검증)[:16])
