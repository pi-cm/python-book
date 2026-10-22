# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.9 CNN은 무엇을 보는가 · manuscript-vol2/chapters/09-cnn.md:1156]
import matplotlib
import matplotlib.pyplot as plt
import torch

from 옷도구 import 옷CNN, 시험_데이터

matplotlib.use("Agg")
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))
모델.eval()
X, _ = 시험_데이터()
사진 = X[:1]                                           # 시험 사진 0번(앵클부츠): (1, 1, 28, 28)
with torch.no_grad():
    첫단 = 모델.특징[:2](사진)                         # 첫 합성곱 + ReLU: (1, 32, 28, 28)
    둘째단 = 모델.특징[:5](사진)                       # 둘째 합성곱 + ReLU까지: (1, 64, 14, 14)
print("첫째 단 특징 맵:", tuple(첫단.shape), " 둘째 단 특징 맵:", tuple(둘째단.shape))
print("첫째 단에서 0인 칸의 비율:", f"{(첫단 == 0).float().mean():.1%}")
print("둘째 단에서 0인 칸의 비율:", f"{(둘째단 == 0).float().mean():.1%}")

그림, 칸들 = plt.subplots(3, 8, figsize=(8, 3.6))
칸들[0, 0].imshow(사진[0, 0], cmap="gray_r")
칸들[0, 0].set_title("입력", fontsize=8)
for i in range(1, 8):                                  # 첫째 단 7장
    칸들[0, i].imshow(첫단[0, i - 1], cmap="viridis")
    칸들[0, i].set_title(f"1단 {i - 1}번", fontsize=8)
for 번호 in range(16):                                 # 둘째 단 16장
    칸 = 칸들[1 + 번호 // 8, 번호 % 8]
    칸.imshow(둘째단[0, 번호], cmap="viridis")
    칸.set_title(f"2단 {번호}번", fontsize=8)
for 칸 in 칸들.flat:
    칸.axis("off")
그림.tight_layout()
그림.savefig("cnn_feature_maps.png", dpi=200)
