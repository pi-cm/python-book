# [2권 부록 B. 꼭 필요한 수학 직관 · B.8 확률 분포에서 뽑기: 정규분포와 샘플링 · manuscript-vol2/appendix/B-math-intuition.md:702]
import torch

torch.manual_seed(0)
z = torch.randn(100000)                      # 평균 0, 표준편차 1인 정규분포에서 뽑기
print(f"평균 {z.mean().item():+.3f}  표준편차 {z.std().item():.3f}")
for k in [1, 2, 3]:
    print(f"평균에서 표준편차 {k}개 안쪽: {(z.abs() < k).float().mean().item():.1%}")

# 평균 5, 표준편차 2인 정규분포가 필요하면: 평균 + 표준편차 × z
x = 5 + 2 * z
print(f"옮기고 늘린 뒤: 평균 {x.mean().item():.3f}  표준편차 {x.std().item():.3f}")
