# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.4 기울기 소실과 폭주 · manuscript-vol2/chapters/11-rnn-lstm.md:492]
import torch

# 같은 수를 거듭 곱하면: 1보다 조금 작으면 사라지고, 조금 크면 터진다
for 배율 in [0.5, 0.9, 1.0, 1.1, 1.5]:
    결과 = [배율 ** 횟수 for 횟수 in (10, 50, 100)]
    print(f"{배율} 거듭 곱하기  10번 {결과[0]:9.3g}  50번 {결과[1]:9.3g}  100번 {결과[2]:9.3g}")

# 역전파의 한 단계에는 tanh의 기울기(1 - tanh²)가 곱해진다. 언제나 1 이하
z = torch.tensor([0.0, 1.0, 2.0, 3.0], requires_grad=True)
torch.tanh(z).sum().backward()
print("tanh의 기울기:", [round(v, 4) for v in z.grad.tolist()])
