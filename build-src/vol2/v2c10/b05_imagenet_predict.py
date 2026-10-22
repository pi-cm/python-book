import torch
from torchvision import datasets, models

가중치 = models.ResNet18_Weights.DEFAULT
모델 = models.resnet18(weights=가중치).eval()
전처리 = 가중치.transforms()
범주 = 가중치.meta["categories"]

원본 = datasets.EuroSAT("data", download=True)
정답들 = torch.tensor(원본.targets)
for k in [1, 3, 7, 8, 9]:                       # 숲, 도로, 주거지, 강, 바다·호수
    i = (정답들 == k).nonzero()[0].item()       # 그 클래스의 첫 사진
    with torch.no_grad():
        확률 = 모델(전처리(원본[i][0]).unsqueeze(0)).softmax(dim=1)[0]
    위 = 확률.topk(3)
    print(f"{원본.classes[k]:11} →", ", ".join(f"{범주[j]} {p:.0%}" for p, j in zip(위.values, 위.indices)))
