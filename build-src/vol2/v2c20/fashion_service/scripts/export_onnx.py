"""models/fashion_cnn.pt를 ONNX로 내보내고, 두 결과가 같은지 확인한다."""
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch

from app.fashion_model import 모델_불러오기

폴더 = Path("models")
모델 = 모델_불러오기(폴더 / "fashion_cnn.pt")
배치 = torch.export.Dim("batch", min=1, max=1024)
torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), 폴더 / "fashion_cnn.onnx", dynamo=True,
                  input_names=["image"], output_names=["logits"], dynamic_shapes={"x": {0: 배치}},
                  external_data=False, verbose=False)

x = torch.rand(16, 1, 28, 28, generator=torch.Generator().manual_seed(0))
with torch.no_grad():
    기대값 = 모델(x).numpy()
세션 = ort.InferenceSession(폴더 / "fashion_cnn.onnx", providers=["CPUExecutionProvider"])
오차 = np.abs(세션.run(["logits"], {"image": x.numpy()})[0] - 기대값).max()
assert 오차 < 1e-4, f"PyTorch와 ONNX 결과가 다릅니다: {오차}"
print(f"내보내기 완료: {폴더 / 'fashion_cnn.onnx'} (최대 오차 {오차:.1e})")
