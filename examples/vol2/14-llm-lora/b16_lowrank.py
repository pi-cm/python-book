# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.7 LoRA의 아이디어: 고칠 부분만 작게 · manuscript-vol2/chapters/14-llm-lora.md:731]
import torch

# 세로 벡터 하나 × 가로 벡터 하나 = 표 전체 (외적)
a = torch.tensor([[1.0], [2.0], [3.0]])      # (3, 1)
b = torch.tensor([[10.0, 20.0, 30.0, 40.0]]) # (1, 4)
표 = a @ b                                    # (3, 4): 숫자 7개로 12개짜리 표를 만든다
print(표)
print("랭크:", torch.linalg.matrix_rank(표).item())

torch.manual_seed(0)
B, A = torch.randn(896, 8), torch.randn(8, 896)
print("(896, 8) @ (8, 896) 의 랭크:", torch.linalg.matrix_rank(B @ A).item())

# 가중치 하나를 통째로 고칠 때와 작은 행렬 두 개로 고칠 때의 숫자 개수
d = 896                                       # Qwen2.5-0.5B의 은닉 크기
print(f"통째로: {d * d:,}개")
for r in [1, 4, 8, 16, 64]:
    print(f"랭크 {r:2}: {r * (d + d):7,}개 ({r * (d + d) / (d * d):.1%})")
