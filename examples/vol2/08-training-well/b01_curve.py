# [2권 Chapter 8. 학습 잘 시키기 · 8.1 과적합과 과소적합 진단하기 · manuscript-vol2/chapters/08-training-well.md:130]
import matplotlib.pyplot as plt
import torch

from 학습도구 import 데이터_준비, 로더_만들기, 모델_만들기, 평가, 한_에폭_학습

(X_학습, y_학습), (X_검증, y_검증), _ = 데이터_준비()
(_, y_진짜), _, _ = 데이터_준비(잡음_비율=0.0)       # 바꾸기 전의 진짜 정답
print("학습", tuple(X_학습.shape), "검증", tuple(X_검증.shape))
print(f"정답이 틀린 학습 데이터: {(y_학습 != y_진짜).sum().item()}개")

torch.manual_seed(0)
모델 = 모델_만들기()
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
로더 = 로더_만들기(X_학습, y_학습)

기록 = {"학습 손실": [], "검증 손실": []}
print("에폭  학습손실  검증손실  학습정확도  검증정확도")
for 에폭 in range(1, 151):
    한_에폭_학습(모델, 로더, 옵티마이저)
    학습_손실, 학습_정확도 = 평가(모델, X_학습, y_학습)
    검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
    기록["학습 손실"].append(학습_손실)
    기록["검증 손실"].append(검증_손실)
    if 에폭 in (1, 5, 10, 20, 30, 50, 100, 150):
        print(f"{에폭:4d}  {학습_손실:8.4f}  {검증_손실:8.4f}  "
              f"{학습_정확도:9.1%}  {검증_정확도:9.1%}")

최저 = min(range(150), key=lambda i: 기록["검증 손실"][i])
print(f"검증 손실이 가장 낮았던 에폭: {최저 + 1} ({기록['검증 손실'][최저]:.4f})")

plt.rcParams["font.family"] = "AppleGothic"      # macOS 한글 글꼴
plt.rcParams["axes.unicode_minus"] = False
plt.figure(figsize=(7, 4))
for 이름, 값들 in 기록.items():
    plt.plot(range(1, 151), 값들, label=이름)
plt.axvline(최저 + 1, color="gray", linestyle="--", label="검증 손실 최저")
plt.xlabel("에폭")
plt.ylabel("손실")
plt.legend()
plt.tight_layout()
plt.savefig("learning_curve.png", dpi=200)
