# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.2 torch.onnx.export로 내보내기 · manuscript-vol2/chapters/19-onnx-quantization.md:76]
from pathlib import Path

import torch

from 옷도구 import 옷CNN

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))   # 9장 9.5절의 CNN
모델.eval()                                       # 내보내기 전에 꼭 평가 모드로 (6장 6.8절)

예시_입력 = torch.zeros(1, 1, 28, 28)              # 사진 한 장 모양이면 값은 무엇이든 된다
결과 = torch.onnx.export(모델, (예시_입력,), "fashion_cnn_first.onnx", verbose=False)
print(type(결과).__name__)

for 파일 in ["fashion_cnn.pt", "fashion_cnn_first.onnx", "fashion_cnn_first.onnx.data"]:
    print(f"{파일:28} {Path(파일).stat().st_size / 1024:7.1f} KB")
