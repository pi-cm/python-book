# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.6 VAE: 점 대신 구름으로 · manuscript-vol2/chapters/15-generative-models.md:671]
import torch
from torch import nn

from 생성도구 import 격자_저장, 사진_불러오기, 이름


class VAE(nn.Module):
    """15.6절에서 학습한 VAE와 같은 설계도."""

    def __init__(self, 잠재_크기: int = 2) -> None:
        super().__init__()
        self.몸통 = nn.Sequential(nn.Flatten(), nn.Linear(784, 256), nn.ReLU())
        self.평균 = nn.Linear(256, 잠재_크기)
        self.로그분산 = nn.Linear(256, 잠재_크기)
        self.디코더 = nn.Sequential(nn.Linear(잠재_크기, 256), nn.ReLU(),
                                  nn.Linear(256, 784), nn.Unflatten(1, (1, 28, 28)))


모델 = VAE()
모델.load_state_dict(torch.load("vae.pt"))
모델.eval()

# 1) 잠재 공간 지도: -2.5~2.5 사이를 가로세로 12칸씩 나눠 모든 점을 그려 본다
눈금 = torch.linspace(-2.5, 2.5, 12)
격자_점 = torch.stack(torch.meshgrid(눈금, -눈금, indexing="xy"), dim=-1).reshape(-1, 2)
with torch.no_grad():
    격자_저장(torch.sigmoid(모델.디코더(격자_점)), "vae_map.png", 한_줄=12)

# 2) 보간: T셔츠 한 장에서 바지 한 장으로 조금씩 옮겨 가기
X, y = 사진_불러오기(학습=False)
A, B = X[y == 0][0:1], X[y == 1][0:1]
with torch.no_grad():
    za, zb = 모델.평균(모델.몸통(A)), 모델.평균(모델.몸통(B))
    print(f"{이름[0]}의 잠재 위치: {[round(v, 2) for v in za[0].tolist()]}")
    print(f"{이름[1]}의 잠재 위치: {[round(v, 2) for v in zb[0].tolist()]}")
    비율 = torch.linspace(0, 1, 8).view(-1, 1)
    픽셀_섞기 = (1 - 비율.view(-1, 1, 1, 1)) * A + 비율.view(-1, 1, 1, 1) * B
    잠재_보간 = torch.sigmoid(모델.디코더((1 - 비율) * za + 비율 * zb))
격자_저장(torch.cat([픽셀_섞기, 잠재_보간]), "interp.png")
