# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.2 torch.onnx.export로 내보내기 · manuscript-vol2/chapters/19-onnx-quantization.md:120]
from pathlib import Path

import onnx
import torch

from 옷도구 import 옷CNN

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))
모델.eval()
torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), "fashion_cnn.onnx",
                  verbose=False, external_data=False)        # 가중치까지 한 파일에
print(f"fashion_cnn.onnx {Path('fashion_cnn.onnx').stat().st_size / 1024:.1f} KB")

모형 = onnx.load("fashion_cnn.onnx")
onnx.checker.check_model(모형)                    # ONNX 규격에 맞는지 검사 (틀리면 예외)
print("규격 검사 통과")
print("만든 도구:", 모형.producer_name, 모형.producer_version)
print("연산자 판(opset):", [(o.domain or "ai.onnx", o.version) for o in 모형.opset_import])


def 모양(값: onnx.ValueInfoProto) -> list[int | str]:
    """입출력 정보에서 차원 크기(또는 이름)를 꺼낸다."""
    return [d.dim_value or d.dim_param for d in 값.type.tensor_type.shape.dim]


print("입력:", [(i.name, 모양(i)) for i in 모형.graph.input])
print("출력:", [(o.name, 모양(o)) for o in 모형.graph.output])
