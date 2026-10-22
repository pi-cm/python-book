import onnxruntime as ort

print("ONNX Runtime", ort.__version__)
print("이 컴퓨터에서 쓸 수 있는 실행 장치:", ort.get_available_providers())
