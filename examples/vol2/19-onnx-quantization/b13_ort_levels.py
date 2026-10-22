# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.6 그래프 들여다보기 · manuscript-vol2/chapters/19-onnx-quantization.md:678]
from collections import Counter

import onnx
import onnxruntime as ort

from 배포도구 import ONNX로_내보내기, 불러오기, 작은_ResNet

ONNX로_내보내기(불러오기(작은_ResNet, "fashion_resnet.pt"), "fashion_resnet.onnx")
단계들 = {"끄기": ort.GraphOptimizationLevel.ORT_DISABLE_ALL,
          "기본": ort.GraphOptimizationLevel.ORT_ENABLE_BASIC,
          "확장": ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED,
          "전부": ort.GraphOptimizationLevel.ORT_ENABLE_ALL}            # 세션의 기본값
for 이름, 단계 in 단계들.items():
    설정 = ort.SessionOptions()
    설정.graph_optimization_level = 단계
    설정.optimized_model_filepath = "fashion_resnet_ort.onnx"    # 실제로 돌릴 그래프를 저장
    ort.InferenceSession("fashion_resnet.onnx", 설정, providers=["CPUExecutionProvider"])
    연산 = Counter(노드.op_type for 노드 in onnx.load("fashion_resnet_ort.onnx").graph.node)
    print(f"{이름}: 노드 {sum(연산.values()):2}개 {dict(연산.most_common(4))}")
