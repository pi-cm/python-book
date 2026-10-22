# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.8 유명한 구조의 아이디어 · manuscript-vol2/chapters/09-cnn.md:820]
from torchvision import models

# 구조만 만든다 (weights=None: 학습된 숫자는 받지 않는다. 받아서 쓰는 일은 10장에서)
for 이름, 만들기 in [("AlexNet (2012)", models.alexnet), ("VGG-16 (2014)", models.vgg16),
                     ("ResNet-18 (2015)", models.resnet18), ("ResNet-50 (2015)", models.resnet50)]:
    모델 = 만들기(weights=None)
    개수 = sum(p.numel() for p in 모델.parameters())
    합성곱수 = sum(1 for m in 모델.modules() if type(m).__name__ == "Conv2d")
    print(f"{이름:17} 파라미터 {개수 / 1e6:6.1f}백만개, 합성곱층 {합성곱수:2}개, float32로 {개수 * 4 / 1024**2:5.0f} MB")
