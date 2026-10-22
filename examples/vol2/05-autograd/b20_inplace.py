# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.9 제자리 연산과 자동 미분의 충돌 · manuscript-vol2/chapters/05-autograd.md:830]
import torch

a = torch.tensor([0.0, 1.0, 2.0], requires_grad=True)
b = a.exp()                    # exp는 기울기 계산에 '자기 결과'를 다시 쓴다
print("b의 버전:", b._version)
b.add_(1)                      # 결과를 제자리에서 바꿔 버리면?
print("b의 버전:", b._version)
try:
    b.sum().backward()
except RuntimeError as e:
    print("오류:", str(e).split(" Hint")[0])

a = torch.tensor([0.0, 1.0, 2.0], requires_grad=True)
b = a.exp()
c = b + 1                      # 밑줄 없는 연산: 새 텐서를 만든다
c.sum().backward()
print("밑줄 없이:", a.grad)

a = torch.tensor([0.0, 1.0, 2.0], requires_grad=True)
b = a * 3                      # 곱하기 3의 기울기는 b의 값과 상관없다
b.add_(1)
b.sum().backward()
print("상관없는 경우:", a.grad)
