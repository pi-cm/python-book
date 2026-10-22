# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.8 확산 모델: 잡음을 걷어 내며 그리기 · manuscript-vol2/chapters/15-generative-models.md:1058]
import torch

from 생성도구 import 격자_저장
from 확산도구 import 그리기, 작은UNet


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


장치 = 장치_고르기()
모델 = 작은UNet().to(장치)
모델.load_state_dict(torch.load("확산.pt", map_location=장치))

# 1) 잡음이 사진으로 바뀌어 가는 과정: 8장을 그리며 중간 단계를 기록
torch.manual_seed(3)
기록_단계 = (999, 800, 600, 400, 300, 200, 100, 0)
_, 기록 = 그리기(모델, 8, 장치, 기록_단계=기록_단계)
for 단계, x in zip(기록_단계, 기록):
    print(f"t={단계:3}: 값 범위 {x.min():6.2f} ~ {x.max():5.2f}, 표준편차 {x.std():.2f}")
과정 = torch.stack(기록, dim=1).flatten(0, 1)      # (8장 × 8단계, 1, 28, 28): 한 줄이 한 장의 과정
격자_저장((과정 + 1) / 2, "diffusion_reverse.png")

# 2) 새 그림 1,000장: 64장은 그림으로, 전부는 15.9절 채점용으로 저장
torch.manual_seed(0)
그림, _ = 그리기(모델, 1000, 장치)
그림 = ((그림.cpu() + 1) / 2).clamp(0, 1)
격자_저장(그림[:64], "diffusion_samples.png")
torch.save(그림, "확산_1000.pt")
print("저장한 그림:", tuple(그림.shape))
