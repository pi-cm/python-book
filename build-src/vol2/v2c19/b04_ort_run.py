import numpy as np
import onnxruntime as ort
import torch

from 옷도구 import 옷CNN, 시험_데이터

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))
모델.eval()

세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
입력, 출력 = 세션.get_inputs()[0], 세션.get_outputs()[0]
print("입력:", 입력.name, 입력.shape, 입력.type)
print("출력:", 출력.name, 출력.shape, 출력.type)

X, y = 시험_데이터()
사진 = X[:1]                                      # 시험 사진 첫 장, (1, 1, 28, 28)
점수_onnx = 세션.run(None, {입력.name: 사진.numpy()})[0]    # 넘파이 배열로 넣고 넘파이로 받는다
with torch.no_grad():
    점수_torch = 모델(사진).numpy()

이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트", "샌들", "셔츠", "운동화", "가방", "앵클부츠"]
np.set_printoptions(precision=3, suppress=True)
print("ONNX Runtime:", 점수_onnx[0])
print("PyTorch     :", 점수_torch[0])
print("가장 큰 차이:", np.abs(점수_onnx - 점수_torch).max())
print("예측:", 이름[점수_onnx.argmax()], "/ 정답:", 이름[y[0]])
