# [2권 Chapter 8. 학습 잘 시키기 · 8.1 과적합과 과소적합 진단하기 · manuscript-vol2/chapters/08-training-well.md:45]
"""8장 실험에서 함께 쓰는 데이터 준비·모델·학습 도구."""
import torch
from sklearn.datasets import load_digits
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def 데이터_준비(잡음_비율: float = 0.2, 학습_개수: int = 200):
    """손글씨 숫자를 학습·검증·테스트로 나누고, 학습 정답 일부를 일부러 틀리게 바꾼다."""
    X, y = load_digits(return_X_y=True)          # 8×8 흑백 숫자 1,797장
    X = torch.tensor(X, dtype=torch.float32) / 16.0   # 0~16 밝기를 0~1로
    y = torch.tensor(y)                          # 정답 0~9 (int64)

    g = torch.Generator().manual_seed(0)         # 분할을 언제나 같게
    순서 = torch.randperm(len(X), generator=g)
    학습, 검증, 테스트 = 순서[:학습_개수], 순서[학습_개수:학습_개수 + 500], 순서[학습_개수 + 500:]

    y_학습 = y[학습].clone()
    바꿀_곳 = torch.rand(학습_개수, generator=g) < 잡음_비율
    y_학습[바꿀_곳] = torch.randint(0, 10, (int(바꿀_곳.sum()),), generator=g)
    return (X[학습], y_학습), (X[검증], y[검증]), (X[테스트], y[테스트])


def 모델_만들기(은닉: int = 256, 드롭아웃: float = 0.0, 배치정규화: bool = False) -> nn.Sequential:
    """입력 64 → 은닉 두 층 → 출력 10인 다층 신경망."""
    층들: list[nn.Module] = []
    입력 = 64
    for _ in range(2):
        층들.append(nn.Linear(입력, 은닉))
        if 배치정규화:
            층들.append(nn.BatchNorm1d(은닉))
        층들.append(nn.ReLU())
        if 드롭아웃 > 0:
            층들.append(nn.Dropout(드롭아웃))
        입력 = 은닉
    층들.append(nn.Linear(입력, 10))
    return nn.Sequential(*층들)


def 깊은_모델(배치정규화: bool = False, 활성화: type[nn.Module] = nn.ReLU) -> nn.Sequential:
    """폭 64짜리 은닉층 8개를 쌓은 깊은 신경망 (8.4절, 8.6절, 8.11절에서 사용)."""
    층들: list[nn.Module] = []
    for _ in range(8):
        층들.append(nn.Linear(64, 64))
        if 배치정규화:
            층들.append(nn.BatchNorm1d(64))
        층들.append(활성화())
    층들.append(nn.Linear(64, 10))
    return nn.Sequential(*층들)


def 한_에폭_학습(모델: nn.Module, 로더: DataLoader, 옵티마이저: torch.optim.Optimizer) -> None:
    """학습 데이터를 한 바퀴 돌며 가중치를 고친다."""
    모델.train()
    손실_함수 = nn.CrossEntropyLoss()
    for X, y in 로더:
        옵티마이저.zero_grad()
        손실 = 손실_함수(모델(X), y)
        손실.backward()
        옵티마이저.step()


@torch.no_grad()
def 평가(모델: nn.Module, X: torch.Tensor, y: torch.Tensor) -> tuple[float, float]:
    """손실과 정확도를 돌려준다."""
    모델.eval()
    출력 = 모델(X)
    손실 = nn.functional.cross_entropy(출력, y).item()
    정확도 = (출력.argmax(dim=1) == y).float().mean().item()
    return 손실, 정확도


def 로더_만들기(X: torch.Tensor, y: torch.Tensor, 배치_크기: int = 32) -> DataLoader:
    """씨앗을 고정한 생성기로 섞는 DataLoader."""
    g = torch.Generator().manual_seed(0)
    return DataLoader(TensorDataset(X, y), batch_size=배치_크기, shuffle=True, generator=g)
