# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.10 NumPy와 다른 점, 자주 만나는 오류 · manuscript-vol2/chapters/04-tensors.md:1277]
import torch


def 오류_보기(설명: str, 계산) -> None:
    """계산을 실행해 보고, 오류가 나면 첫 줄만 보여 준다."""
    try:
        계산()
    except RuntimeError as e:
        print(f"[{설명}] {str(e).splitlines()[0]}")


torch.manual_seed(0)
x = torch.randn(4, 3)            # 사진 4장 × 특성 3개
w = torch.randn(4, 2)            # 실수로 (특성 3개 → 2개)가 아닌 (4, 2)로 만듦
오류_보기("행렬 곱 모양", lambda: x @ w)
오류_보기("자료형 섞기", lambda: torch.tensor([[1, 2]]) @ torch.tensor([[0.5], [0.5]]))
오류_보기("숫자 하나가 아님", lambda: x.sum(dim=0).item())
오류_보기("쌓을 크기가 다름", lambda: torch.stack([torch.zeros(3), torch.zeros(4)]))

# 고친 뒤: 모양을 찍어 보며 확인
w = torch.randn(3, 2)
print(x.shape, "@", w.shape, "→", (x @ w).shape)
print((torch.tensor([[1, 2]]).float() @ torch.tensor([[0.5], [0.5]])).item())
print(x.sum().item())
