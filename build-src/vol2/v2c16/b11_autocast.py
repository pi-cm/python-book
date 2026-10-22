import torch
import torch.nn.functional as F
from torch import nn


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


장치 = 장치_고르기()
반정밀도 = torch.bfloat16 if 장치.type == "cpu" else torch.float16
torch.manual_seed(0)
모델 = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10)).to(장치)
x = torch.randn(8, 64, device=장치)
y = torch.randint(0, 10, (8,), device=장치)

with torch.autocast(device_type=장치.type, dtype=반정밀도):   # 이 안에서만 16비트로
    은닉 = 모델[0](x)
    점수 = 모델(x)
    확률 = 점수.softmax(dim=1)
    손실 = F.cross_entropy(점수, y)
print("입력:", x.dtype, "| Linear 출력:", 은닉.dtype, "| 점수:", 점수.dtype)
print("softmax:", 확률.dtype, "| 손실:", 손실.dtype)

손실.backward()                                                # backward는 with 밖에서
print("가중치:", 모델[0].weight.dtype, "| 기울기:", 모델[0].weight.grad.dtype)
print("autocast 밖의 Linear 출력:", 모델[0](x).dtype)
