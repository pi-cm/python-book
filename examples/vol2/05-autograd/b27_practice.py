# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.13 실습: 당뇨병 진행 정도를 autograd만으로 예측하기 · manuscript-vol2/chapters/05-autograd.md:1157]
import torch
from sklearn.datasets import load_diabetes

# 1) 데이터: 당뇨병 환자 442명의 검사값 10가지와 1년 뒤 진행 정도
데이터 = load_diabetes(scaled=False)
X = torch.tensor(데이터.data, dtype=torch.float32)       # (442, 10)
y = torch.tensor(데이터.target, dtype=torch.float32)     # (442,)
이름 = 데이터.feature_names

torch.manual_seed(0)
순서 = torch.randperm(len(X))
학습_idx, 시험_idx = 순서[:350], 순서[350:]             # 350명으로 배우고 92명으로 시험
평균 = X[학습_idx].mean(dim=0)                          # 기준은 학습 데이터에서만 (2장)
표준편차 = X[학습_idx].std(dim=0)
X = (X - 평균) / 표준편차
X_학습, y_학습, X_시험, y_시험 = X[학습_idx], y[학습_idx], X[시험_idx], y[시험_idx]


def 예측(X: torch.Tensor, w: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return X @ w + b                                    # (n, 10) @ (10,) → (n,)


def rmse(X: torch.Tensor, y: torch.Tensor, w: torch.Tensor, b: torch.Tensor) -> float:
    """평균적으로 몇 점 틀리는지: 평균제곱오차의 제곱근."""
    return ((예측(X, w, b) - y) ** 2).mean().sqrt().item()


# 2) 손으로 미분한 기울기와 autograd가 같은지 먼저 확인
w = torch.zeros(10, requires_grad=True)
b = torch.zeros((), requires_grad=True)
손실 = ((예측(X_학습, w, b) - y_학습) ** 2).mean()
손실.backward()
with torch.no_grad():
    오차 = 예측(X_학습, w, b) - y_학습
    손_w = 2 * X_학습.T @ 오차 / len(X_학습)              # 5.3절 공식을 10개 특성으로
    손_b = 2 * 오차.mean()
print("기울기 일치:", torch.allclose(w.grad, 손_w), torch.allclose(b.grad, 손_b))
w.grad.zero_()
b.grad.zero_()

# 3) 미니배치 경사하강법으로 학습
학습률, 배치_크기 = 0.05, 32
for 에폭 in range(1, 101):
    섞기 = torch.randperm(len(X_학습))
    for 시작 in range(0, len(X_학습), 배치_크기):
        고를 = 섞기[시작:시작 + 배치_크기]
        손실 = ((예측(X_학습[고를], w, b) - y_학습[고를]) ** 2).mean()
        손실.backward()
        with torch.no_grad():
            w -= 학습률 * w.grad
            b -= 학습률 * b.grad
        w.grad.zero_()
        b.grad.zero_()
    if 에폭 in (1, 5, 20, 100):
        with torch.no_grad():
            print(f"에폭 {에폭:3}: 학습 RMSE {rmse(X_학습, y_학습, w, b):6.2f}, "
                  f"시험 RMSE {rmse(X_시험, y_시험, w, b):6.2f}")
print(f"s1, s2 가중치: {w[4].item():.2f}, {w[5].item():.2f}")
