# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.4 PyTorch에게 미분 맡기기 · manuscript-vol2/chapters/05-autograd.md:440]
import torch

x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
y = x ** 2                        # 결과가 숫자 3개인 벡터
try:
    y.backward()
except RuntimeError as e:
    print("오류 1:", e)

y.sum().backward()                # 하나로 모으면 된다
print("x.grad:", x.grad)          # 각 칸의 기울기 2x

try:
    torch.tensor([1, 2, 3], requires_grad=True)
except RuntimeError as e:
    print("오류 2:", e)

print("x는 잎인가?", x.is_leaf, "/ y는 잎인가?", y.is_leaf)
print("y.grad:", y.grad)          # 중간 결과의 기울기는 보관하지 않는다
