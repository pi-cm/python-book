import copy
import io

import torch
from torchao.quantization import (Int8DynamicActivationInt8WeightConfig, Int8WeightOnlyConfig,
                                  quantize_)

from 배포도구 import 불러오기, 시간_재기, 시험_데이터, 옷CNN

torch.set_num_threads(4)
X, y = 시험_데이터()
원본 = 불러오기(옷CNN, "fashion_cnn.pt")


def 저장_크기(모델: torch.nn.Module) -> float:
    """state_dict를 torch.save했을 때의 크기(KB). 파일 대신 메모리 버퍼에 써 본다."""
    버퍼 = io.BytesIO()
    torch.save(모델.state_dict(), 버퍼)
    return len(버퍼.getvalue()) / 1024


for 이름, 설정 in [("float32 (원본)", None),
                   ("가중치만 int8", Int8WeightOnlyConfig()),
                   ("가중치·입력 int8", Int8DynamicActivationInt8WeightConfig())]:
    모델 = copy.deepcopy(원본)
    if 설정 is not None:
        quantize_(모델, 설정)                      # 모델 안의 nn.Linear를 제자리에서 바꾼다
    with torch.inference_mode():
        정확도 = (모델(X).argmax(dim=1) == y).float().mean().item()
        한장 = 시간_재기(lambda: 모델(X[:1]))
        묶음 = 시간_재기(lambda: 모델(X[:64]))
    print(f"{이름}: {저장_크기(모델):,.0f}KB, 정확도 {정확도:.2%}, 1장 {한장:.3f}ms, 64장 {묶음:.3f}ms")

w = 모델.분류[1].weight                            # 마지막으로 바꾼 모델의 큰 Linear
print(type(w).__name__, "정수:", w.qdata.dtype, tuple(w.qdata.shape),
      "배율:", tuple(w.scale.shape))
