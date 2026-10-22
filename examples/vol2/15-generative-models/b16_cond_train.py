# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.10 실습: 주문한 옷을 그리는 조건부 확산 모델 · manuscript-vol2/chapters/15-generative-models.md:1224]
import torch
import torch.nn.functional as F

from 생성도구 import 격자_저장, 사진_불러오기
from 확산도구 import T, 그리기, 작은UNet, 잡음_더하기


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


장치 = 장치_고르기()
torch.manual_seed(0)
X, y = 사진_불러오기(학습=True)
X, y = (X * 2 - 1).to(장치), y.to(장치)

모델 = 작은UNet(클래스_수=10).to(장치)            # 바뀐 곳 (1): 종류 10가지를 알려 줄 수 있게
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=2e-3)
손실_합 = 0.0
for 걸음 in range(1, 5001):
    번호 = torch.randint(0, len(X), (128,), device=장치)
    x0, 종류 = X[번호], y[번호]
    t = torch.randint(0, T, (128,), device=장치)
    잡음 = torch.randn_like(x0)
    손실 = F.mse_loss(모델(잡음_더하기(x0, t, 잡음), t, 종류), 잡음)   # 바뀐 곳 (2): 정답 종류도 넘긴다
    옵티마이저.zero_grad()
    손실.backward()
    옵티마이저.step()
    손실_합 += 손실.item()
    if 걸음 % 1000 == 0:
        print(f"{걸음:5}걸음: 평균 손실 {손실_합 / 1000:.4f}")
        손실_합 = 0.0
torch.save(모델.state_dict(), "조건부_확산.pt")

# 종류마다 8장씩: 한 줄이 한 종류 (T셔츠, 바지, … 앵클부츠)
torch.manual_seed(0)
종류 = torch.arange(10, device=장치).repeat_interleave(8)
그림, _ = 그리기(모델, 80, 장치, 클래스=종류)
격자_저장((그림.cpu() + 1) / 2, "conditional.png")
