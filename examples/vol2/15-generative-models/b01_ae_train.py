# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.1 오토인코더: 줄였다가 되살리기 · manuscript-vol2/chapters/15-generative-models.md:151]
import torch
import torch.nn.functional as F

from 생성도구 import 격자_저장, 사진_불러오기, 오토인코더, 오토인코더_학습

torch.manual_seed(0)
X_학습, _ = 사진_불러오기(학습=True)
X_시험, _ = 사진_불러오기(학습=False)
print("학습 사진:", tuple(X_학습.shape), "시험 사진:", tuple(X_시험.shape))

모델 = 오토인코더(잠재_크기=32)
print(f"파라미터 {sum(p.numel() for p in 모델.parameters()):,}개")
오토인코더_학습(모델, X_학습, 에폭=5)

모델.eval()
with torch.no_grad():
    잠재 = 모델.인코더(X_시험[:8])          # 사진 8장을 32칸으로 줄이고
    복원 = 모델.디코더(잠재)                # 다시 784칸으로 되살린다
    시험_손실 = F.mse_loss(모델(X_시험), X_시험).item()
print("잠재 벡터 모양:", tuple(잠재.shape))
print("첫 사진의 잠재 벡터 앞 6칸:", [round(v, 2) for v in 잠재[0, :6].tolist()])
print(f"시험 사진 재구성 손실: {시험_손실:.4f}")
print(f"줄인 비율: 784 → 32 (약 {784 / 32:.1f}분의 1)")

격자_저장(torch.cat([X_시험[:8], 복원]), "ae_recon.png")   # 위: 원본, 아래: 복원
