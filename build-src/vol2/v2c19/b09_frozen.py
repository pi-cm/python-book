import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn


class 굳는_모델(nn.Module):
    """forward 안에 파이썬 코드가 섞인 모델."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        print("  (forward 실행됨)")
        잡음 = torch.from_numpy(np.random.rand(3).astype(np.float32))   # 넘파이 난수
        for _ in range(3):                                            # 파이썬 반복문
            x = x + 1
        return x + 잡음


print("내보내는 중:")
torch.onnx.export(굳는_모델().eval(), (torch.zeros(3),), "frozen.onnx",
                  verbose=False, external_data=False)
그래프 = onnx.load("frozen.onnx").graph
print("연산:", [노드.op_type for 노드 in 그래프.node])
print("저장된 상수:", [(값.name, list(값.dims)) for 값 in 그래프.initializer])

세션 = ort.InferenceSession("frozen.onnx", providers=["CPUExecutionProvider"])
입력이름 = 세션.get_inputs()[0].name
for 회 in range(1, 3):
    print(f"{회}번째 실행:", 세션.run(None, {입력이름: np.zeros(3, dtype=np.float32)})[0])
