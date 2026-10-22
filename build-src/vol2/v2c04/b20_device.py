import torch


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


장치 = 장치_고르기()
print("고른 장치:", 장치)

x = torch.ones(3)                  # 처음에는 CPU에서 만들어진다
print(x.device)
y = x.to(장치)                     # 장치로 옮기기 (새 텐서를 돌려준다)
print(y.device)
z = torch.ones(3, device=장치)     # 처음부터 그 장치에 만들기
print((y + z).cpu())               # 결과를 다시 CPU로
