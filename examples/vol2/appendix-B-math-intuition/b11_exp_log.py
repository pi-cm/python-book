# [2권 부록 B. 꼭 필요한 수학 직관 · B.4 지수와 로그 · manuscript-vol2/appendix/B-math-intuition.md:338]
import math

print("exp(0) =", math.exp(0), " exp(1) =", round(math.exp(1), 4))
print("exp(2 + 3) == exp(2) * exp(3):", math.isclose(math.exp(5), math.exp(2) * math.exp(3)))
print("log(2 * 3) == log(2) + log(3):", math.isclose(math.log(6), math.log(2) + math.log(3)))
print("log(exp(4)) =", math.log(math.exp(4)))
for p in [1.0, 0.5, 0.1, 0.01]:
    print(f"log({p}) = {math.log(p):.3f}")
