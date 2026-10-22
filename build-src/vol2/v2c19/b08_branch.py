import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn


class 파이썬_if(nn.Module):
    """합이 양수면 두 배, 아니면 1을 뺀다: 파이썬 if로."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.sum() > 0:
            return x * 2
        return x - 1


class 텐서_where(nn.Module):
    """같은 일을 torch.where로: 두 결과를 다 계산하고 칸마다 고른다 (4장 4.4절)."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.where(x.sum() > 0, x * 2, x - 1)


class 텐서_cond(nn.Module):
    """같은 일을 torch.cond로: 조건에 따라 둘 중 한 갈래만 계산한다."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.cond(x.sum() > 0, lambda x: x * 2, lambda x: x - 1, (x,))


for 모델 in [파이썬_if(), 텐서_where(), 텐서_cond()]:
    이름 = type(모델).__name__
    try:
        torch.onnx.export(모델.eval(), (torch.ones(3),), "branch.onnx",
                          verbose=False, external_data=False)
    except Exception as e:
        print(f"{이름}: 내보내기 실패 ({type(e).__name__} ← {type(e.__cause__).__name__})")
        continue
    연산 = [노드.op_type for 노드 in onnx.load("branch.onnx").graph.node]
    세션 = ort.InferenceSession("branch.onnx", providers=["CPUExecutionProvider"])
    입력이름 = 세션.get_inputs()[0].name
    결과 = [세션.run(None, {입력이름: np.array(v, dtype=np.float32)})[0].tolist()
            for v in ([1, 2, 3], [-1, -2, -3])]
    print(f"{이름}: {연산} → {결과}")
