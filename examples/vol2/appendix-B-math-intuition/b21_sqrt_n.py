# [2권 부록 B. 꼭 필요한 수학 직관 · B.7 평균·분산·표준편차와 표준화 · manuscript-vol2/appendix/B-math-intuition.md:637]
import torch

torch.manual_seed(0)
# 표준편차 1인 무작위 수 n개를 "더하기"와 "평균 내기"를 10000번씩 해 보고 흔들림을 잰다
for n in [4, 64, 512]:
    묶음 = torch.randn(10000, n)
    합_흔들림 = 묶음.sum(dim=1).std().item()
    평균_흔들림 = 묶음.mean(dim=1).std().item()
    print(f"n={n:3}  합의 표준편차 {합_흔들림:6.2f} (n의 제곱근 {n ** 0.5:5.2f})"
          f"  평균의 표준편차 {평균_흔들림:.4f} (1 / n의 제곱근 {1 / n ** 0.5:.4f})")
