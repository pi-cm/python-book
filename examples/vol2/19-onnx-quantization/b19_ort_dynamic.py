# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.10 ONNX Runtime으로 양자화하기 · manuscript-vol2/chapters/19-onnx-quantization.md:976]
from collections import Counter

import onnx
from onnxruntime.quantization import QuantType, quantize_dynamic
from onnxruntime.quantization.shape_inference import quant_pre_process

from 배포도구 import (ONNX로_내보내기, 불러오기, 세션_만들기, 세션_정확도, 시간_재기,
                     시험_데이터, 옷CNN, 파일_크기)

ONNX로_내보내기(불러오기(옷CNN, "fashion_cnn.pt"), "fashion_cnn.onnx")
quant_pre_process("fashion_cnn.onnx", "fashion_cnn_pre.onnx")          # 양자화 전 준비(모양 추론 등)
quantize_dynamic("fashion_cnn_pre.onnx", "fashion_cnn_dynamic.onnx",
                 weight_type=QuantType.QInt8)                           # 가중치를 int8로

X, y = 시험_데이터()
X, y = X.numpy(), y.numpy()
for 경로 in ["fashion_cnn.onnx", "fashion_cnn_dynamic.onnx"]:
    세션 = 세션_만들기(경로)
    print(f"{경로:26} {파일_크기(경로):7.1f}KB  정확도 {세션_정확도(세션, X, y):.2%}  "
          f"64장 {시간_재기(lambda: 세션.run(None, {'사진': X[:64]})):.3f}ms")
연산 = Counter(노드.op_type for 노드 in onnx.load("fashion_cnn_dynamic.onnx").graph.node)
print(dict(연산.most_common()))
