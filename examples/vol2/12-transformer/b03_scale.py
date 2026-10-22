# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.2 점수를 d의 제곱근으로 나누는 이유 · manuscript-vol2/chapters/12-transformer.md:142]
import torch

torch.manual_seed(0)
for d in [4, 64, 512]:
    q = torch.randn(1000, 1, d)             # 질문 1000개
    k = torch.randn(1000, 8, d)             # 질문마다 키 8개
    점수 = (q * k).sum(dim=-1)              # 내적: (1000, 8)
    결과 = []
    for 나눌까 in (False, True):
        s = (점수 / d ** 0.5 if 나눌까 else 점수).detach().requires_grad_()
        가중치 = s.softmax(dim=-1)
        (가중치 * torch.randn(1000, 8)).sum().backward()    # 아무 손실이나 흘려 보기
        결과.append((s.std().item(), 가중치.max(dim=-1).values.mean().item(), s.grad.abs().mean().item()))
    (표1, 최대1, 기울기1), (표2, 최대2, 기울기2) = 결과
    print(f"d={d:3d}  점수 표준편차 {표1:5.2f} → {표2:.2f},  가장 큰 가중치 {최대1:.3f} → {최대2:.3f},"
          f"  기울기 {기울기1:.4f} → {기울기2:.4f}")
