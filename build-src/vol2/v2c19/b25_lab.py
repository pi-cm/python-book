import numpy as np
import torch
from onnxruntime.quantization import (CalibrationDataReader, QuantFormat, QuantType,
                                      quantize_static)
from onnxruntime.quantization.shape_inference import quant_pre_process
from torchvision import datasets

from 배포도구 import (ONNX로_내보내기, 불러오기, 세션_만들기, 시간_재기, 시험_데이터,
                     작은_ResNet, 파일_크기)
from 옷도구 import 오른쪽으로_밀기


class 보정_데이터(CalibrationDataReader):
    """19.10절과 같은 읽개."""

    def __init__(self, 사진: np.ndarray, 크기: int = 32) -> None:
        self.묶음들 = iter([{"사진": 사진[i:i + 크기]} for i in range(0, len(사진), 크기)])

    def get_next(self) -> dict[str, np.ndarray] | None:
        return next(self.묶음들, None)


torch.set_num_threads(4)
X, y = 시험_데이터()
X_np, y_np = X.numpy(), y.numpy()
밀린_np = 오른쪽으로_밀기(X, 4).numpy()                 # 4칸 밀어 본 시험 사진

# 1) 내보내고 확인하기
모델 = 불러오기(작은_ResNet, "fashion_resnet.pt")
ONNX로_내보내기(모델, "fashion_resnet.onnx")
with torch.inference_mode():
    기준 = 모델(X).numpy()
원본 = 세션_만들기("fashion_resnet.onnx")
print(f"[확인] PyTorch와 최대 차이 {np.abs(원본.run(None, {'사진': X_np})[0] - 기준).max():.1e}")

# 2) 학습 사진 512장으로 보정해 정적 양자화
학습셋 = datasets.FashionMNIST("data", train=True, download=True)
보정용 = (학습셋.data[:512].float().unsqueeze(1) / 255).numpy()
quant_pre_process("fashion_resnet.onnx", "fashion_resnet_pre.onnx")
quantize_static("fashion_resnet_pre.onnx", "fashion_resnet_int8.onnx", 보정_데이터(보정용),
                quant_format=QuantFormat.QDQ, per_channel=True,
                activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8)
정수 = 세션_만들기("fashion_resnet_int8.onnx")

# 3) 세 가지 실행 방법을 같은 잣대로 비교
후보 = {
    "PyTorch float32": ("fashion_resnet.pt", lambda x: 모델(torch.from_numpy(x)).numpy()),
    "ONNX float32": ("fashion_resnet.onnx", lambda x: 원본.run(None, {"사진": x})[0]),
    "ONNX int8": ("fashion_resnet_int8.onnx", lambda x: 정수.run(None, {"사진": x})[0]),
}
print(f"{'방법':16}{'크기':>8}{'정확도':>8}{'셔츠':>7}{'일치':>8}{'4칸':>7}{'1장':>9}{'64장':>9}")
for 이름, (파일, 실행) in 후보.items():
    with torch.inference_mode():
        예측 = 실행(X_np).argmax(axis=1)
        밀림 = (실행(밀린_np).argmax(axis=1) == y_np).mean()
        한장 = 시간_재기(lambda: 실행(X_np[:1]))
        묶음 = 시간_재기(lambda: 실행(X_np[:64]))
    셔츠 = (예측[y_np == 6] == 6).mean()
    일치 = (예측 == 기준.argmax(axis=1)).mean()             # float32 PyTorch와 같은 답의 비율
    print(f"{이름:16}{파일_크기(파일):6.0f}KB{(예측 == y_np).mean():8.2%}{셔츠:7.1%}"
          f"{일치:8.2%}{밀림:7.1%}{한장:7.3f}ms{묶음:7.2f}ms")
