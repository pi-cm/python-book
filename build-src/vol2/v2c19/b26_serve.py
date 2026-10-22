import sys

import numpy as np
import onnxruntime as ort

이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트", "샌들", "셔츠", "운동화", "가방", "앵클부츠"]


class 옷_분류기:
    """ONNX 파일 하나와 넘파이만으로 옷 사진을 분류한다 (torch 없이)."""

    def __init__(self, 경로: str) -> None:
        설정 = ort.SessionOptions()
        설정.intra_op_num_threads = 4
        self.세션 = ort.InferenceSession(경로, 설정, providers=["CPUExecutionProvider"])

    def 예측(self, 사진: np.ndarray, 몇_개: int = 3) -> list[list[tuple[str, float]]]:
        """0~255 정수 사진 (장 수, 28, 28)을 받아 장마다 확률 높은 순서로 몇_개를 돌려준다."""
        x = 사진.reshape(-1, 1, 28, 28).astype(np.float32) / 255     # 학습 때와 같은 전처리
        점수 = self.세션.run(None, {"사진": x})[0]
        확률 = np.exp(점수 - 점수.max(axis=1, keepdims=True))         # 소프트맥스 (6장 6.2절)
        확률 /= 확률.sum(axis=1, keepdims=True)
        순서 = np.argsort(-확률, axis=1)[:, :몇_개]
        return [[(이름[k], float(p[k])) for k in 줄] for p, 줄 in zip(확률, 순서)]


사진 = np.fromfile("data/FashionMNIST/raw/t10k-images-idx3-ubyte", dtype=np.uint8, offset=16)
정답 = np.fromfile("data/FashionMNIST/raw/t10k-labels-idx1-ubyte", dtype=np.uint8, offset=8)
사진 = 사진.reshape(-1, 28, 28)

분류기 = 옷_분류기("fashion_resnet_int8.onnx")
for 번호, 후보 in zip([0, 4, 7], 분류기.예측(사진[[0, 4, 7]])):
    print(f"{번호}번 (정답 {이름[정답[번호]]}): " + ", ".join(f"{n} {p:.1%}" for n, p in 후보))
print("torch를 불러왔나:", "torch" in sys.modules)
