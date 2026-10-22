# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.8 확산 모델: 잡음을 걷어 내며 그리기 · manuscript-vol2/chapters/15-generative-models.md:985]
import torch
import torch.nn.functional as F

from 생성도구 import 격자_저장, 사진_불러오기
from 확산도구 import T, 그리기, 작은UNet, 잡음_더하기


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


장치 = 장치_고르기()
torch.manual_seed(0)
X, _ = 사진_불러오기(학습=True)
X = (X * 2 - 1).to(장치)                       # -1~1로 바꿔 통째로 장치에 올린다 (약 188MB)

모델 = 작은UNet().to(장치)
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=2e-3)
스케줄러 = torch.optim.lr_scheduler.CosineAnnealingLR(옵티마이저, T_max=5000)   # 8장 8.7절
print(f"장치 {장치}, 파라미터 {sum(p.numel() for p in 모델.parameters()):,}개")

중간_그림 = []
손실_합 = 0.0
for 걸음 in range(1, 5001):
    x0 = X[torch.randint(0, len(X), (128,), device=장치)]     # 사진 128장 무작위로
    t = torch.randint(0, T, (128,), device=장치)              # 사진마다 단계도 무작위로
    잡음 = torch.randn_like(x0)
    손실 = F.mse_loss(모델(잡음_더하기(x0, t, 잡음), t), 잡음)   # 섞은 잡음을 맞혀라
    옵티마이저.zero_grad()
    손실.backward()
    옵티마이저.step()
    스케줄러.step()                                 # 걸음마다 학습률을 조금씩 줄인다
    손실_합 += 손실.item()
    if 걸음 % 1000 == 0:
        print(f"{걸음:5}걸음: 최근 1000걸음 평균 손실 {손실_합 / 1000:.4f}")
        손실_합 = 0.0
    if 걸음 in (200, 1000, 5000):                  # 학습 중간중간 그림 8장씩 그려 보기
        torch.manual_seed(1)
        그림, _ = 그리기(모델, 8, 장치)
        중간_그림.append(그림.cpu())
        모델.train()

torch.save(모델.state_dict(), "확산.pt")
격자_저장((torch.cat(중간_그림) + 1) / 2, "diffusion_progress.png")
