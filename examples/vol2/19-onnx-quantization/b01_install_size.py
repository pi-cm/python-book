# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 들어가며: 모델을 다 만들었는데, 어디서 돌리죠? · manuscript-vol2/chapters/19-onnx-quantization.md:21]
from importlib import metadata

# 설치된 패키지 파일이 디스크에서 차지하는 크기 (이 책의 맥, 파이썬 3.12)
for 이름 in ["torch", "onnxruntime", "onnx", "numpy"]:
    배포판 = metadata.distribution(이름)
    크기 = sum(파일.size or 0 for 파일 in 배포판.files or [])
    print(f"{이름:12} {배포판.version:8} {크기 / 1024**2:6.1f} MB")
