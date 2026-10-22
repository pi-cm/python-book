from collections import Counter

import numpy as np
import onnx
from onnxruntime.quantization import (CalibrationDataReader, QuantFormat, QuantType,
                                      quantize_static)
from onnxruntime.quantization.shape_inference import quant_pre_process
from torchvision import datasets

from 배포도구 import (ONNX로_내보내기, 불러오기, 세션_만들기, 세션_정확도, 시간_재기,
                     시험_데이터, 옷CNN, 파일_크기)


class 보정_데이터(CalibrationDataReader):
    """보정용 사진 묶음을 32장씩 하나씩 건네주는 읽개."""

    def __init__(self, 사진: np.ndarray, 크기: int = 32) -> None:
        self.묶음들 = iter([{"사진": 사진[i:i + 크기]} for i in range(0, len(사진), 크기)])

    def get_next(self) -> dict[str, np.ndarray] | None:
        return next(self.묶음들, None)              # 다 건네면 None


# 보정에는 시험 데이터가 아니라 학습 데이터의 일부를 쓴다
학습셋 = datasets.FashionMNIST("data", train=True, download=True)
보정용 = (학습셋.data[:512].float().unsqueeze(1) / 255).numpy()

ONNX로_내보내기(불러오기(옷CNN, "fashion_cnn.pt"), "fashion_cnn.onnx")
quant_pre_process("fashion_cnn.onnx", "fashion_cnn_pre.onnx")
quantize_static("fashion_cnn_pre.onnx", "fashion_cnn_static.onnx", 보정_데이터(보정용),
                quant_format=QuantFormat.QDQ, per_channel=True,
                activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8)

X, y = 시험_데이터()
X, y = X.numpy(), y.numpy()
for 경로 in ["fashion_cnn.onnx", "fashion_cnn_static.onnx"]:
    세션 = 세션_만들기(경로)
    print(f"{경로:24} {파일_크기(경로):7.1f}KB  정확도 {세션_정확도(세션, X, y):.2%}  "
          f"1장 {시간_재기(lambda: 세션.run(None, {'사진': X[:1]})):.3f}ms  "
          f"64장 {시간_재기(lambda: 세션.run(None, {'사진': X[:64]})):.3f}ms")
연산 = Counter(노드.op_type for 노드 in onnx.load("fashion_cnn_static.onnx").graph.node)
print(dict(연산.most_common()))
