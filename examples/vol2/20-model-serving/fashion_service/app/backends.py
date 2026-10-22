# [2권 Chapter 20. FastAPI로 모델 서빙: 내 모델을 웹 서비스로 · 20.11 실습: 옷 사진 분류 서비스 완성하기 · manuscript-vol2/chapters/20-model-serving.md:1089]
"""모델 계산을 맡는 백엔드: 같은 약속(점수)을 지키는 두 가지 구현."""
import os
from pathlib import Path
from typing import Protocol

import numpy as np


class 예측기(Protocol):
    """(N, 1, 28, 28) float32 배열을 받아 (N, 10) 점수를 돌려준다."""
    이름: str
    모델_파일: Path

    def 점수(self, x: np.ndarray) -> np.ndarray: ...


class ONNX예측기:
    이름 = "onnx"

    def __init__(self, 폴더: Path) -> None:
        import onnxruntime as ort

        self.모델_파일 = 폴더 / "fashion_cnn.onnx"
        옵션 = ort.SessionOptions()
        옵션.intra_op_num_threads = int(os.environ.get("ORT_THREADS", "0"))   # 0이면 코어 수만큼
        self.세션 = ort.InferenceSession(self.모델_파일, 옵션, providers=["CPUExecutionProvider"])

    def 점수(self, x: np.ndarray) -> np.ndarray:
        return self.세션.run(["logits"], {"image": x})[0]


class 파이토치예측기:
    이름 = "torch"

    def __init__(self, 폴더: Path) -> None:
        import torch                            # torch 백엔드를 고를 때만 필요하다

        from app.fashion_model import 모델_불러오기

        self.모델_파일 = 폴더 / "fashion_cnn.pt"
        self.torch, self.모델 = torch, 모델_불러오기(self.모델_파일)

    def 점수(self, x: np.ndarray) -> np.ndarray:
        with self.torch.no_grad():
            return self.모델(self.torch.from_numpy(x)).numpy()


def 예측기_만들기(이름: str, 폴더: Path) -> 예측기:
    백엔드들 = {"onnx": ONNX예측기, "torch": 파이토치예측기}
    if 이름 not in 백엔드들:
        raise ValueError(f"알 수 없는 백엔드: {이름} (가능: {', '.join(백엔드들)})")
    return 백엔드들[이름](폴더)
