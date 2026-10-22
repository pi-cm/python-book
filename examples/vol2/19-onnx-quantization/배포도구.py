# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.6 그래프 들여다보기 · manuscript-vol2/chapters/19-onnx-quantization.md:456]
"""19장 예제에서 함께 쓰는 모델 설계도·내보내기·시간 재기 도구."""
import statistics
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
import torch.nn.functional as F
from torch import nn

from 옷도구 import 옷CNN, 시험_데이터  # noqa: F401  (9장 9.5절의 CNN과 시험 데이터)


class 잔차블록(nn.Module):
    """9장 9.8절의 잔차 블록."""

    def __init__(self, 입력: int, 출력: int, 보폭: int = 1) -> None:
        super().__init__()
        self.합성곱1 = nn.Conv2d(입력, 출력, 3, stride=보폭, padding=1, bias=False)
        self.정규화1 = nn.BatchNorm2d(출력)
        self.합성곱2 = nn.Conv2d(출력, 출력, 3, padding=1, bias=False)
        self.정규화2 = nn.BatchNorm2d(출력)
        if 보폭 != 1 or 입력 != 출력:
            self.지름길 = nn.Sequential(nn.Conv2d(입력, 출력, 1, stride=보폭, bias=False),
                                        nn.BatchNorm2d(출력))
        else:
            self.지름길 = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        고칠양 = self.정규화2(self.합성곱2(F.relu(self.정규화1(self.합성곱1(x)))))
        return F.relu(고칠양 + self.지름길(x))


def 작은_ResNet() -> nn.Sequential:
    """9장 9.10절의 작은 ResNet 설계도."""
    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1, bias=False), nn.BatchNorm2d(32), nn.ReLU(),
        잔차블록(32, 32), 잔차블록(32, 64, 보폭=2), 잔차블록(64, 128, 보폭=2),
        nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(0.3), nn.Linear(128, 10),
    )


def 불러오기(설계도: Callable[[], nn.Module], 파일: str) -> nn.Module:
    """저장한 가중치를 설계도에 채우고 평가 모드로 돌려준다."""
    모델 = 설계도()
    모델.load_state_dict(torch.load(파일, weights_only=True))
    return 모델.eval()


def ONNX로_내보내기(모델: nn.Module, 경로: str, 최적화: bool = True) -> None:
    """19.2~19.4절의 정리: 묶음 크기가 자유로운 한 파일짜리 ONNX로 내보낸다."""
    torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), 경로, verbose=False,
                      external_data=False, optimize=최적화,
                      input_names=["사진"], output_names=["점수"],
                      dynamic_shapes=({0: torch.export.Dim("batch")},))


def 세션_만들기(경로: str, 스레드: int = 4) -> ort.InferenceSession:
    """스레드 수를 정해 CPU에서 돌리는 ONNX Runtime 세션."""
    설정 = ort.SessionOptions()
    설정.intra_op_num_threads = 스레드
    return ort.InferenceSession(경로, 설정, providers=["CPUExecutionProvider"])


def 세션_정확도(세션: ort.InferenceSession, X: np.ndarray, y: np.ndarray) -> float:
    """사진 묶음 전체를 한 번에 넣어 정확도를 잰다."""
    점수 = 세션.run(None, {"사진": X})[0]
    return float((점수.argmax(axis=1) == y).mean())


def 시간_재기(함수: Callable[[], object], 반복: int = 50, 준비: int = 5) -> float:
    """준비 운동 뒤 여러 번 재서 한 번 실행 시간의 중앙값(밀리초)을 돌려준다."""
    for _ in range(준비):
        함수()
    기록 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        기록.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(기록)


def 파일_크기(*경로: str) -> float:
    """파일 크기의 합(KB). .onnx와 옆의 .onnx.data를 함께 셀 때 쓴다."""
    return sum(Path(p).stat().st_size for p in 경로 if Path(p).exists()) / 1024
