# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.9 생성 모델은 어떻게 평가할까 · manuscript-vol2/chapters/15-generative-models.md:1145]
import torch

from 생성도구 import 격자_저장, 사진_불러오기, 채점기_만들기


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


장치 = 장치_고르기()
X_학습, _ = 사진_불러오기(학습=True)
X_시험, y_시험 = 사진_불러오기(학습=False)
채점기 = 채점기_만들기(장치)
with torch.no_grad():
    정확도 = (채점기(X_시험.to(장치)).argmax(1).cpu() == y_시험).float().mean()
print(f"채점기의 시험 정확도: {정확도:.2%}\n")

묶음 = {
    "진짜 사진": X_시험[:1000],
    "VAE": torch.load("vae_1000.pt"),
    "확산 모델": torch.load("확산_1000.pt"),
}
print("            확신도   종류별 개수 (T셔츠 … 앵클부츠)")
for 이름_, 사진 in 묶음.items():
    with torch.no_grad():
        확률 = 채점기(사진.to(장치)).softmax(dim=1).cpu()
    확신도 = 확률.max(dim=1).values.mean()            # 채점기가 얼마나 뚜렷하게 알아보나
    개수 = torch.bincount(확률.argmax(dim=1), minlength=10)   # 종류가 골고루 나오나
    print(f"{이름_:8}  {확신도:6.1%}   {개수.tolist()}")


# 외워서 베낀 건 아닐까? 가장 가까운 학습 사진까지의 거리
def 가장_가까운(사진: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """사진마다 픽셀 거리가 가장 가까운 학습 사진의 거리와 번호를 돌려준다."""
    거리 = torch.cdist(사진.flatten(1).to(장치), X_학습.flatten(1).to(장치))   # (200, 60000)
    최소 = 거리.min(dim=1)
    return 최소.values.cpu(), 최소.indices.cpu()


진짜_거리, _ = 가장_가까운(X_시험[:200])
확산_거리, 번호 = 가장_가까운(묶음["확산 모델"][:200])
print(f"\n가장 가까운 학습 사진까지 평균 거리: 진짜 시험 사진 {진짜_거리.mean():.2f}, "
      f"확산 모델 {확산_거리.mean():.2f}")
격자_저장(torch.cat([묶음["확산 모델"][:8], X_학습[번호[:8]]]), "nearest.png")
