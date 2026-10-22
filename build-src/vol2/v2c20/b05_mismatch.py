import numpy as np
import torch
from PIL import Image, ImageOps
from torchvision import datasets

from 서빙도구 import 모델_불러오기

모델 = 모델_불러오기()
시험셋 = datasets.FashionMNIST("data", train=False, download=True)
사진들 = [시험셋[i][0] for i in range(1000)]
정답 = torch.tensor([시험셋[i][1] for i in range(1000)])


def 정확도(전처리, 사진_목록: list[Image.Image]) -> float:
    x = torch.stack([전처리(사진) for 사진 in 사진_목록])
    with torch.no_grad():
        return (모델(x).argmax(dim=1) == 정답).float().mean().item()


def 학습때와_같이(사진: Image.Image) -> torch.Tensor:
    배열 = np.asarray(사진.convert("L").resize((28, 28)), dtype=np.float32) / 255
    return torch.from_numpy(배열).unsqueeze(0)


def 나누기_빠뜨림(사진: Image.Image) -> torch.Tensor:
    배열 = np.asarray(사진.convert("L").resize((28, 28)), dtype=np.float32)   # 0~255 그대로
    return torch.from_numpy(배열).unsqueeze(0)


def 배경_맞추기(사진: Image.Image) -> torch.Tensor:
    x = 학습때와_같이(사진)
    테두리 = torch.cat([x[0, 0], x[0, -1], x[0, :, 0], x[0, :, -1]])
    return 1 - x if 테두리.mean() > 0.5 else x      # 배경이 밝으면 뒤집어 검은 배경으로


흰_배경 = [ImageOps.invert(사진) for 사진 in 사진들]   # 쇼핑몰 사진처럼 흰 배경에 어두운 옷
print(f"학습 때와 같은 전처리         : {정확도(학습때와_같이, 사진들):.1%}")
print(f"255로 나누기를 빠뜨림         : {정확도(나누기_빠뜨림, 사진들):.1%}")
print(f"흰 배경 사진, 그대로          : {정확도(학습때와_같이, 흰_배경):.1%}")
print(f"흰 배경 사진, 배경 맞추기     : {정확도(배경_맞추기, 흰_배경):.1%}")
print(f"원래 사진에 배경 맞추기를 써도: {정확도(배경_맞추기, 사진들):.1%}")
