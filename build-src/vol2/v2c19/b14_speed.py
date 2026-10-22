import platform

import torch

from 배포도구 import (ONNX로_내보내기, 불러오기, 세션_만들기, 시간_재기, 시험_데이터,
                     옷CNN, 작은_ResNet)

torch.set_num_threads(4)                          # PyTorch와 ONNX Runtime 모두 스레드 4개
print("환경:", platform.machine(), platform.python_version(), "torch", torch.__version__)
X, _ = 시험_데이터()

print(f"{'모델':6} {'묶음':>4} {'PyTorch':>10} {'ORT':>10} {'배':>5}")
for 이름, 설계도, 파일 in [("CNN", 옷CNN, "fashion_cnn.pt"),
                          ("ResNet", 작은_ResNet, "fashion_resnet.pt")]:
    모델 = 불러오기(설계도, 파일)
    ONNX로_내보내기(모델, "speed.onnx")
    세션 = 세션_만들기("speed.onnx", 스레드=4)
    for 장수 in [1, 64]:
        x = X[:장수]
        x_np = x.numpy()
        with torch.inference_mode():
            파이토치 = 시간_재기(lambda: 모델(x))
        런타임 = 시간_재기(lambda: 세션.run(None, {"사진": x_np}))
        print(f"{이름:6} {장수:>4} {파이토치:8.3f}ms {런타임:8.3f}ms {파이토치 / 런타임:5.1f}")
