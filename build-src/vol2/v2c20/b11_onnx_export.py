from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch

from 서빙도구 import 모델_불러오기

모델 = 모델_불러오기("fashion_cnn.pt")
배치 = torch.export.Dim("batch", min=1, max=1024)          # 첫 차원(장 수)은 바뀔 수 있다
torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), "fashion_cnn.onnx", dynamo=True,
                  input_names=["image"], output_names=["logits"],
                  dynamic_shapes={"x": {0: 배치}},
                  external_data=False, verbose=False)   # 가중치까지 한 파일에, 진행 메시지 끄기
for 파일 in sorted(Path(".").glob("fashion_cnn.*")):
    print(f"{파일.name:17} {파일.stat().st_size / 1024:7.1f} KB")

세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
print("입력:", [(i.name, i.shape) for i in 세션.get_inputs()])
print("출력:", [(o.name, o.shape) for o in 세션.get_outputs()])

torch.manual_seed(0)
for 장수 in [1, 64]:
    x = torch.rand(장수, 1, 28, 28)
    with torch.no_grad():
        파이토치 = 모델(x).numpy()
    런타임 = 세션.run(["logits"], {"image": x.numpy()})[0]
    같은_답 = (파이토치.argmax(1) == 런타임.argmax(1)).all()
    print(f"{장수:2}장: 최대 오차 {np.abs(파이토치 - 런타임).max():.2e}, 예측 모두 같음 {같은_답}")
