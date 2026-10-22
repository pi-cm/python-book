# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.2 잠재 공간 들여다보기 · manuscript-vol2/chapters/15-generative-models.md:255]
import matplotlib.pyplot as plt
import torch

from 생성도구 import 사진_불러오기, 오토인코더, 오토인코더_학습, 이름

X_학습, _ = 사진_불러오기(학습=True)
X_시험, y_시험 = 사진_불러오기(학습=False)

torch.manual_seed(0)
모델 = 오토인코더_학습(오토인코더(잠재_크기=2), X_학습, 에폭=5, 출력=False).eval()
with torch.no_grad():
    점 = 모델.인코더(X_시험)                  # 시험 사진 1만 장 → 점 1만 개 (10000, 2)

for 번호, 클래스 in enumerate(이름):
    중심 = 점[y_시험 == 번호].mean(dim=0)
    print(f"{클래스:5}: 중심 ({중심[0]:6.1f}, {중심[1]:6.1f})")

plt.rcParams["font.family"] = "AppleGothic"     # macOS 한글 글꼴 (윈도우는 8장 참고)
plt.rcParams["axes.unicode_minus"] = False
plt.figure(figsize=(8, 6))
for 번호, 클래스 in enumerate(이름):
    고른 = 점[y_시험 == 번호]
    plt.scatter(고른[:, 0], 고른[:, 1], s=2, alpha=0.5, label=클래스)
plt.legend(markerscale=6, fontsize=9, loc="upper left", bbox_to_anchor=(1.01, 1))
plt.xlabel("잠재 1번 칸")
plt.ylabel("잠재 2번 칸")
plt.tight_layout()
plt.savefig("latent_2d.png", dpi=200)
