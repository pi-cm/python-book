# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.5 멀티헤드 어텐션: 여러 관점으로 동시에 보기 · manuscript-vol2/chapters/12-transformer.md:391]
import torch

B, T, C, H = 2, 5, 8, 2                 # 문장 2개, 글자 5개, 숫자 8개, 헤드 2개
D = C // H                              # 헤드마다 숫자 4개씩
x = torch.arange(B * T * C, dtype=torch.float32).view(B, T, C)

나눔 = x.view(B, T, H, D).transpose(1, 2)        # (B, T, C) → (B, T, H, D) → (B, H, T, D)
print("나눈 모양:", tuple(나눔.shape), "이어져 있나?", 나눔.is_contiguous())
print("0번 헤드 = 숫자 0~3번 칸:", torch.equal(나눔[:, 0], x[..., :D]))
print("1번 헤드 = 숫자 4~7번 칸:", torch.equal(나눔[:, 1], x[..., D:]))

결과 = 나눔 @ torch.eye(D)                          # 행렬 곱의 결과는 (B, H, T, D) 순서로 새로 놓인다
되돌림 = 결과.transpose(1, 2)                       # (B, H, T, D) → (B, T, H, D)
try:
    되돌림.view(B, T, C)
except RuntimeError as e:
    print("view 오류:", str(e).split("(")[0].strip())
합침 = 되돌림.contiguous().view(B, T, C)            # 4장의 permute → contiguous → view
print("다시 합친 모양:", tuple(합침.shape), "원래와 같은가?", torch.equal(합침, x))
