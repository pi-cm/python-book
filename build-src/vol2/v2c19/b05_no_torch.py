import sys

import numpy as np
import onnxruntime as ort

# torch 없이 FashionMNIST 원본 파일을 넘파이로 읽는다 (앞부분 16바이트, 8바이트는 머리말)
사진 = np.fromfile("data/FashionMNIST/raw/t10k-images-idx3-ubyte", dtype=np.uint8, offset=16)
정답 = np.fromfile("data/FashionMNIST/raw/t10k-labels-idx1-ubyte", dtype=np.uint8, offset=8)
사진 = 사진.reshape(-1, 1, 28, 28).astype(np.float32) / 255     # ToTensor()와 같은 0~1 실수

세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
입력이름 = 세션.get_inputs()[0].name
예측 = np.array([세션.run(None, {입력이름: 사진[i:i + 1]})[0].argmax()
                 for i in range(len(사진))])               # 한 장씩 1만 번
print(f"사진 {len(사진):,}장, 정확도 {(예측 == 정답).mean():.2%}")
print("torch를 불러왔나:", "torch" in sys.modules)
