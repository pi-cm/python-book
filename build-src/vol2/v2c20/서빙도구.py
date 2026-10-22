"""20장 예제에서 함께 쓰는 도구: 9장 9.5절 CNN을 추론용으로 불러오기, 시험 사진을 파일로 만들기."""
import io
from pathlib import Path

import torch
from torchvision import datasets

from 옷도구 import 옷CNN

클래스_이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트",
          "샌들", "셔츠", "운동화", "가방", "앵클부츠"]


def 모델_불러오기(경로: str | Path = "fashion_cnn.pt") -> 옷CNN:
    """저장된 가중치를 CPU로 불러와(4장 4.9절) 평가 모드로 돌려준다(6장 6.8절)."""
    모델 = 옷CNN()
    모델.load_state_dict(torch.load(경로, map_location="cpu", weights_only=True))
    return 모델.eval()


def 시험_사진_파일(개수: int) -> list[tuple[bytes, int]]:
    """FashionMNIST 시험 사진을 앞에서부터 개수만큼, PNG 파일 내용과 정답 번호로 돌려준다."""
    시험셋 = datasets.FashionMNIST("data", train=False, download=True)
    파일들 = []
    for i in range(개수):
        사진, 정답 = 시험셋[i]
        버퍼 = io.BytesIO()                       # 디스크 대신 메모리에 파일을 쓴다
        사진.save(버퍼, format="PNG")
        파일들.append((버퍼.getvalue(), 정답))
    return 파일들
