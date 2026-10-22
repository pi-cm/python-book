# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.13 실습: 당뇨병 진행 정도를 autograd만으로 예측하기 · manuscript-vol2/chapters/05-autograd.md:1237]
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


# 2) 전체 데이터로, 학습률 0.2, 5000번 (미니배치의 흔들림 없이 끝까지 내려가기)
w = torch.zeros(10, requires_grad=True)
b = torch.zeros((), requires_grad=True)
for _ in range(5000):
    손실 = ((예측(X_학습, w, b) - y_학습) ** 2).mean()
    손실.backward()
    with torch.no_grad():
        w -= 0.2 * w.grad
        b -= 0.2 * b.grad
    w.grad.zero_()
    b.grad.zero_()

# 3) 한 번에 푸는 정답(최소제곱법)
A = torch.cat([X_학습, torch.ones(len(X_학습), 1)], dim=1)   # 마지막 열 1은 b 자리
정답 = torch.linalg.lstsq(A, y_학습.unsqueeze(1)).solution.squeeze(1)
정답_w, 정답_b = 정답[:10], 정답[10]

print("특성  경사하강법  최소제곱법")
for i in range(10):
    print(f"{이름[i]:<4} {w[i].item():10.3f} {정답_w[i].item():11.3f}")
print(f"b    {b.item():10.3f} {정답_b.item():11.3f}")
print(f"가장 큰 차이: {(w.detach() - 정답_w).abs().max().item():.4f}")
with torch.no_grad():
    print(f"학습 RMSE: 경사하강법 {rmse(X_학습, y_학습, w, b):.2f}, 최소제곱법 {rmse(X_학습, y_학습, 정답_w, 정답_b):.2f}")
    print(f"시험 RMSE: 경사하강법 {rmse(X_시험, y_시험, w, b):.2f}, 최소제곱법 {rmse(X_시험, y_시험, 정답_w, 정답_b):.2f}")
print(f"평균만 찍었을 때 시험 RMSE: {(y_시험 - y_학습.mean()).pow(2).mean().sqrt():.2f}")
