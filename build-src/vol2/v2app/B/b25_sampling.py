import torch

torch.manual_seed(0)
확률 = torch.tensor([0.659, 0.242, 0.099])           # B.5절 소프트맥스 결과
뽑기 = torch.multinomial(확률, num_samples=10000, replacement=True)
횟수 = torch.bincount(뽑기, minlength=3)
print("뽑힌 횟수:", 횟수.tolist())
print("뽑힌 비율:", [f"{c / 10000:.3f}" for c in 횟수.tolist()])
print("argmax   :", 확률.argmax().item(), "(언제나 같은 답)")
