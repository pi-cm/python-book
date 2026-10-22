# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.10 ONNX Runtime으로 양자화하기 · manuscript-vol2/chapters/19-onnx-quantization.md:1076]
import numpy as np
from onnxruntime.quantization import (CalibrationDataReader, QuantFormat, QuantType,
                                      quantize_static)
from onnxruntime.quantization.shape_inference import quant_pre_process
from torchvision import datasets

from 배포도구 import ONNX로_내보내기, 불러오기, 세션_만들기, 세션_정확도, 시험_데이터, 작은_ResNet


class 보정_데이터(CalibrationDataReader):
    """19.10절과 같은 읽개."""

    def __init__(self, 사진: np.ndarray, 크기: int = 32) -> None:
        self.묶음들 = iter([{"사진": 사진[i:i + 크기]} for i in range(0, len(사진), 크기)])

    def get_next(self) -> dict[str, np.ndarray] | None:
        return next(self.묶음들, None)


학습셋 = datasets.FashionMNIST("data", train=True, download=True)
진짜 = (학습셋.data[:512].float().unsqueeze(1) / 255).numpy()
보정_후보 = {
    "학습 사진 512장": 진짜,
    "학습 사진 8장": 진짜[:8],
    "새까만 사진 64장": np.zeros_like(진짜[:64]),
    "0~255 그대로 64장": 진짜[:64] * 255,         # 전처리(/255)를 빼먹은 실수
}

ONNX로_내보내기(불러오기(작은_ResNet, "fashion_resnet.pt"), "fashion_resnet.onnx")
quant_pre_process("fashion_resnet.onnx", "fashion_resnet_pre.onnx")
X, y = 시험_데이터()
X, y = X.numpy(), y.numpy()
print(f"float32 원본: 정확도 {세션_정확도(세션_만들기('fashion_resnet.onnx'), X, y):.2%}")
for 이름, 사진 in 보정_후보.items():
    quantize_static("fashion_resnet_pre.onnx", "fashion_resnet_calib.onnx", 보정_데이터(사진),
                    quant_format=QuantFormat.QDQ, per_channel=True,
                    activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8)
    정확도 = 세션_정확도(세션_만들기("fashion_resnet_calib.onnx"), X, y)
    print(f"[{이름}] 보정 후 정확도 {정확도:.2%}")
