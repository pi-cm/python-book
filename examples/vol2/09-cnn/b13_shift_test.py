# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.6 그림을 밀어도 알아볼까요? · manuscript-vol2/chapters/09-cnn.md:647]
import torch

from 옷도구 import 옷CNN, 시험_데이터, 오른쪽으로_밀기, 의류분류기

X, y = 시험_데이터()
print("밀기(칸)" + "".join(f"{칸:>8}" for 칸 in range(5)))
for 별명, 모델, 파일 in [("MLP", 의류분류기(), "fashion_mlp.pt"), ("CNN", 옷CNN(), "fashion_cnn.pt")]:
    모델.load_state_dict(torch.load(파일, weights_only=True))
    모델.eval()
    with torch.no_grad():
        정확도 = [(모델(오른쪽으로_밀기(X, 칸)).argmax(dim=1) == y).float().mean().item() for 칸 in range(5)]
    print(f"{별명:7}" + "".join(f"{a:>8.1%}" for a in 정확도))
