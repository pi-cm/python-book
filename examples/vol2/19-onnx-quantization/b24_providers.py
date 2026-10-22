# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.12 휴대폰과 작은 기기에서: 런타임 고르기 · manuscript-vol2/chapters/19-onnx-quantization.md:1266]
import onnxruntime as ort

print("ONNX Runtime", ort.__version__)
print("이 컴퓨터에서 쓸 수 있는 실행 장치:", ort.get_available_providers())
