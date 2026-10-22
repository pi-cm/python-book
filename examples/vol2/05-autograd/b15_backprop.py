# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.6 연쇄 법칙: 기울기가 거꾸로 흐르는 이유 · manuscript-vol2/chapters/05-autograd.md:608]
import torch

x, y = torch.tensor(3.0), torch.tensor(10.0)          # 데이터 한 개
w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(1.0, requires_grad=True)

# 앞으로 계산(forward): 중간값을 모두 이름 붙여 둔다
예측 = w * x + b              # 7
오차 = 예측 - y               # -3
손실 = 오차 ** 2              # 9
예측.retain_grad()            # 중간 결과의 기울기도 보관해 달라고 부탁
오차.retain_grad()
손실.backward()

# 거꾸로 계산(backward)을 손으로: 끝에서부터 '지역 기울기'를 곱해 나간다
d손실_d오차 = 2 * 오차.item()                 # 손실 = 오차^2
d손실_d예측 = d손실_d오차 * 1                 # 오차 = 예측 - y
d손실_dw = d손실_d예측 * x.item()             # 예측 = w*x + b
d손실_db = d손실_d예측 * 1

for 이름, 손, 파이토치 in [("오차", d손실_d오차, 오차.grad), ("예측", d손실_d예측, 예측.grad),
                          ("w", d손실_dw, w.grad), ("b", d손실_db, b.grad)]:
    print(f"d손실/d{이름}: 손으로 {손:6.1f}, PyTorch {파이토치.item():6.1f}")
