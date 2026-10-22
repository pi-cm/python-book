"""19.11절 본문 확인용(책에 싣지 않음): 학생에게 6만 장을 다 주고 3에폭씩 증류 효과를 비교한다."""
import torch
import torch.nn.functional as F
from torch import nn
from torchvision import datasets

from 배포도구 import 불러오기, 시험_데이터, 작은_ResNet

torch.set_num_threads(4)
학습셋 = datasets.FashionMNIST("data", train=True, download=True)
X학습 = 학습셋.data.float().unsqueeze(1) / 255             # 이번에는 6만 장 전부
y학습 = 학습셋.targets
X, y = 시험_데이터()

선생 = 불러오기(작은_ResNet, "fashion_resnet.pt")          # 6만 장으로 배운 선생 (308,074개)
with torch.no_grad():
    선생_점수 = torch.cat([선생(조각) for 조각 in X학습.split(1000)])                                  # 선생의 답안지를 미리 받아 둔다


def 학생() -> nn.Sequential:
    """채널을 확 줄인 작은 CNN."""
    return nn.Sequential(
        nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Linear(16 * 7 * 7, 10),
    )


def 학습시키기(증류: bool, 씨앗: int, 온도: float = 4.0, 비중: float = 0.9) -> float:
    """학생을 3에폭 학습하고 시험 정확도를 돌려준다. 증류면 선생의 점수도 따라 배운다."""
    torch.manual_seed(씨앗)
    모델 = 학생()
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=2e-3)
    for _ in range(3):
        for 번호 in torch.randperm(len(X학습)).split(64):
            출력 = 모델(X학습[번호])
            손실 = F.cross_entropy(출력, y학습[번호])
            if 증류:   # 온도로 부드럽게 만든 두 확률 분포의 차이 (KL 발산)
                따라하기 = F.kl_div(F.log_softmax(출력 / 온도, dim=1),
                                    F.softmax(선생_점수[번호] / 온도, dim=1),
                                    reduction="batchmean") * 온도 ** 2
                손실 = 비중 * 따라하기 + (1 - 비중) * 손실
            옵티마이저.zero_grad()
            손실.backward()
            옵티마이저.step()
    with torch.no_grad():
        return (모델(X).argmax(dim=1) == y).float().mean().item()


print(f"학생 파라미터 {sum(p.numel() for p in 학생().parameters()):,}개")
결과 = {"정답만": [], "증류": []}
for 씨앗 in range(3):
    for 방식 in 결과:
        결과[방식].append(학습시키기(방식 == "증류", 씨앗))
for 방식, 값 in 결과.items():
    print(f"{방식:4}: " + ", ".join(f"{v:.2%}" for v in 값) + f"  평균 {sum(값) / len(값):.2%}")
