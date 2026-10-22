# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.9 CNN은 무엇을 보는가 · manuscript-vol2/chapters/09-cnn.md:1213]
import matplotlib
import matplotlib.pyplot as plt
import torch

from 옷도구 import 옷CNN, 시험_데이터

matplotlib.use("Agg")
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트", "샌들", "셔츠", "운동화", "가방", "앵클부츠"]

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))
모델.eval()
X, y = 시험_데이터()

번호들 = [0, 1, 2, 4]                                  # 앵클부츠, 풀오버, 바지, 셔츠
그림, 칸들 = plt.subplots(2, len(번호들), figsize=(7, 3.8))
for 열, 번호 in enumerate(번호들):
    사진 = X[번호:번호 + 1].clone().requires_grad_(True)
    점수 = 모델(사진)[0]
    예측 = 점수.argmax().item()
    점수[예측].backward()                              # 예측한 클래스 점수를 입력으로 미분 (5장 5.12절)
    중요도 = 사진.grad[0, 0].abs()
    확률 = torch.softmax(점수.detach(), dim=0)[예측]
    print(f"{번호}번: 정답 {이름[y[번호]]}, 예측 {이름[예측]} ({확률:.1%})")
    칸들[0, 열].imshow(사진.detach()[0, 0], cmap="gray_r")
    칸들[0, 열].set_title(f"예측: {이름[예측]}", fontsize=9)
    칸들[1, 열].imshow(중요도, cmap="hot")
    for 칸 in 칸들[:, 열]:
        칸.axis("off")
그림.tight_layout()
그림.savefig("cnn_saliency.png", dpi=200)
