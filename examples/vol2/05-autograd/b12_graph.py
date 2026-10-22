# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.5 계산 그래프: PyTorch는 무엇을 기억하나 · manuscript-vol2/chapters/05-autograd.md:480]
import torch

w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(1.0, requires_grad=True)
x = torch.tensor(3.0)                       # 데이터: 기울기가 필요 없다
y = torch.tensor(10.0)

예측 = w * x + b
손실 = (예측 - y) ** 2
print("손실:", 손실)


def 그래프_따라가기(노드, 깊이: int = 0) -> None:
    """grad_fn에서 출발해 계산을 거꾸로 거슬러 올라가며 출력한다(1권 9장의 재귀)."""
    if 노드 is None:
        return
    이름 = type(노드).__name__
    if 이름 == "AccumulateGrad":            # 잎(requires_grad=True인 텐서)에 도착
        이름 += f"  ← 잎 텐서 값 {노드.variable.item()}"
    print("    " * 깊이 + 이름)
    for 다음, _ in 노드.next_functions:
        그래프_따라가기(다음, 깊이 + 1)


그래프_따라가기(손실.grad_fn)
