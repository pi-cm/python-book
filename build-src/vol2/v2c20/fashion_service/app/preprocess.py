"""올라온 사진 파일을 모델 입력 배열로 바꾼다 (torch 없이 NumPy와 Pillow만 쓴다)."""
import io

import numpy as np
from PIL import Image, UnidentifiedImageError

최대_바이트 = 1_000_000                  # 파일 크기 한도: 1MB
최대_픽셀 = 4096 * 4096                  # 가로 × 세로 한도: 압축 폭탄 막기


class 사진오류(ValueError):
    """사진으로 읽을 수 없거나 받을 수 없는 파일."""


def 사진_전처리(데이터: bytes) -> np.ndarray:
    """사진 파일을 학습 때와 같은 (1, 28, 28) float32 배열로 바꾼다."""
    try:
        사진 = Image.open(io.BytesIO(데이터))
        if 사진.width * 사진.height > 최대_픽셀:
            raise 사진오류("사진의 가로·세로가 너무 큽니다")
        사진 = 사진.convert("L").resize((28, 28))
    except Image.DecompressionBombError as e:      # 아주 큰 그림은 Image.open이 먼저 알아채고 멈춘다
        raise 사진오류("사진의 가로·세로가 너무 큽니다") from e
    except (UnidentifiedImageError, OSError) as e:
        raise 사진오류("사진 파일이 아닙니다") from e
    배열 = np.asarray(사진, dtype=np.float32) / 255
    테두리 = np.concatenate([배열[0], 배열[-1], 배열[:, 0], 배열[:, -1]])
    if 테두리.mean() > 0.5:              # 배경이 밝으면 뒤집어서 학습 데이터처럼 검은 배경으로
        배열 = 1 - 배열
    return 배열[None]
