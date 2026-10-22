# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.4 입력 모양 정하기 · manuscript-vol2/chapters/19-onnx-quantization.md:255]
import numpy as np
import onnxruntime as ort

세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
입력이름 = 세션.get_inputs()[0].name

for 설명, 입력 in [("64장 묶음", np.zeros((64, 1, 28, 28), dtype=np.float32)),
                   ("float64", np.zeros((1, 1, 28, 28), dtype=np.float64))]:
    try:
        세션.run(None, {입력이름: 입력})
    except Exception as e:
        print(f"[{설명}] {type(e).__name__}")
        print(" ", str(e).replace("\n", " ").split(" : ")[-1])
