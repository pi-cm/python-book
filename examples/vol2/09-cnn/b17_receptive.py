# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.8 유명한 구조의 아이디어 · manuscript-vol2/chapters/09-cnn.md:852]
import torch
from torch import nn

c = 64
큰필터 = nn.Conv2d(c, c, kernel_size=5, padding=2, bias=False)
작은필터_둘 = nn.Sequential(nn.Conv2d(c, c, kernel_size=3, padding=1, bias=False), nn.ReLU(),
                            nn.Conv2d(c, c, kernel_size=3, padding=1, bias=False))
for 이름, 층 in [("5×5 한 번", 큰필터), ("3×3 두 번", 작은필터_둘)]:
    print(f"{이름}: 파라미터 {sum(p.numel() for p in 층.parameters()):,}개")


def 보는_범위(층: nn.Module, 크기: int = 11) -> torch.Tensor:
    """출력 한가운데 칸이 입력의 어느 칸들에 영향을 받는지 기울기로 찾는다 (5장 5.12절)."""
    x = torch.randn(1, 1, 크기, 크기, requires_grad=True)
    출력 = 층(x)
    출력[0, 0, 크기 // 2, 크기 // 2].backward()       # 가운데 칸 하나만 거꾸로 따라가기
    return (x.grad[0, 0] != 0).int()


torch.manual_seed(0)
for 깊이 in (1, 2, 3):
    층 = nn.Sequential(*[nn.Conv2d(1, 1, kernel_size=3, padding=1) for _ in range(깊이)])
    범위 = 보는_범위(층)
    print(f"3×3을 {깊이}번 쌓으면 보는 범위: {범위.sum(dim=0).max().item()}×{범위.sum(dim=1).max().item()}")
print(보는_범위(nn.Sequential(nn.Conv2d(1, 1, 3, padding=1), nn.Conv2d(1, 1, 3, padding=1))))
