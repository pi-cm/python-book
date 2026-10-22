# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.9 CNN은 무엇을 보는가 · manuscript-vol2/chapters/09-cnn.md:1108]
import matplotlib
import matplotlib.pyplot as plt
import torch

matplotlib.use("Agg")                                  # 창을 띄우지 않고 파일로만 그리기
plt.rcParams["font.family"] = "AppleGothic"            # macOS 한글 글꼴
plt.rcParams["axes.unicode_minus"] = False

가중치 = torch.load("fashion_cnn.pt", weights_only=True)    # 9.5절에서 저장한 CNN
첫필터 = 가중치["특징.0.weight"]                            # 첫 합성곱층: (32, 1, 3, 3)
print("첫 층 필터 묶음:", tuple(첫필터.shape))
print("둘째 층 필터 묶음:", tuple(가중치["특징.3.weight"].shape))

그림, 칸들 = plt.subplots(4, 8, figsize=(8, 4.4))
for i, 칸 in enumerate(칸들.flat):
    필터 = 첫필터[i, 0]
    한계 = 필터.abs().max()
    칸.imshow(필터, cmap="bwr", vmin=-한계, vmax=한계)    # 빨강은 +, 파랑은 -
    칸.set_title(f"{i}번", fontsize=8)
    칸.axis("off")
그림.suptitle("첫 합성곱층의 3×3 필터 32개 (빨강 +, 파랑 -)")
그림.tight_layout()
그림.savefig("cnn_filters.png", dpi=200)

# 필터 숫자의 합이 0에 가까우면 '밝기의 변화(경계)'에, 한쪽으로 쏠리면 '밝기 자체'에 반응한다
쏠림 = 첫필터.sum(dim=(1, 2, 3)) / 첫필터.abs().sum(dim=(1, 2, 3))
경계형 = (쏠림.abs() < 0.3).nonzero().flatten().tolist()
print(f"경계에 반응하는 필터 {len(경계형)}개:", 경계형)
print("잉크에 반응:", (쏠림 >= 0.3).nonzero().flatten().tolist(),
      "/ 잉크 없는 곳에 반응:", (쏠림 <= -0.3).nonzero().flatten().tolist())
