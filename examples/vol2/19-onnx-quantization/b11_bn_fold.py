# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.6 그래프 들여다보기 · manuscript-vol2/chapters/19-onnx-quantization.md:611]
from collections import Counter

import numpy as np
import onnx
import torch

from 배포도구 import ONNX로_내보내기, 불러오기, 세션_만들기, 작은_ResNet

모델 = 불러오기(작은_ResNet, "fashion_resnet.pt")        # 9장 9.10절의 작은 ResNet (93.04%)
x = torch.randn(8, 1, 28, 28)
with torch.no_grad():
    기준 = 모델(x).numpy()

for 최적화 in [False, True]:
    경로 = f"fashion_resnet_opt{int(최적화)}.onnx"
    ONNX로_내보내기(모델, 경로, 최적화=최적화)
    연산 = Counter(노드.op_type for 노드 in onnx.load(경로).graph.node)
    차이 = np.abs(세션_만들기(경로).run(None, {"사진": x.numpy()})[0] - 기준).max()
    print(f"optimize={최적화}: 노드 {sum(연산.values())}개, 최대 차이 {차이:.1e}")
    print("  ", dict(연산.most_common(6)))
