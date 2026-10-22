import torch

from 법전 import 배치_뽑기, 준비

표, 학습_데이터, 검증_데이터 = 준비()
print(f"학습 {len(학습_데이터):,}글자, 검증 {len(검증_데이터):,}글자")

x, y = 배치_뽑기(학습_데이터, 문맥_길이=12, 배치_크기=2, 생성기=torch.Generator().manual_seed(3))
print("입력 모양:", tuple(x.shape), "정답 모양:", tuple(y.shape))
for i in range(2):
    print(f"입력 {i}: {표.디코딩(x[i])!r}")
    print(f"정답 {i}: {표.디코딩(y[i])!r}")

# 조각 하나에 '다음 글자 맞히기' 문제가 문맥_길이만큼 들어 있다
for t in range(5):
    print(f"  {표.디코딩(x[0, :t + 1])!r} 다음은 → {표.디코딩(y[0, t:t + 1])!r}")
