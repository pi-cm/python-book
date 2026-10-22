# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.1 합성곱: 돋보기를 옮기며 무늬 찾기 · manuscript-vol2/chapters/09-cnn.md:161]
import torch
import torch.nn.functional as F

그림 = torch.tensor([
    [0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0],
], dtype=torch.float32).reshape(1, 1, 6, 6)

세로선 = torch.tensor([[-1.0, 2.0, -1.0]] * 3)
가로선 = 세로선.T                                     # 전치하면 가로선 찾기
모서리 = torch.tensor([[-1.0, -1.0, -1.0],
                       [ 1.0,  1.0, -1.0],
                       [-1.0,  1.0, -1.0]])          # 왼쪽에서 와서 아래로 꺾이는 곳
필터들 = torch.stack([세로선, 가로선, 모서리]).unsqueeze(1)   # (3, 1, 3, 3): 필터 3개
print("필터 묶음:", 필터들.shape)

특징맵 = F.conv2d(그림, 필터들)                       # (1, 3, 4, 4): 필터마다 한 장
print("특징 맵 묶음:", 특징맵.shape)
for 이름, 맵 in zip(["세로선", "가로선", "모서리"], 특징맵[0]):
    print(f"[{이름}] 가장 큰 값 {맵.max():.0f}, 자리 {divmod(맵.argmax().item(), 4)}")
    for 줄 in 맵:
        print("   " + " ".join("#" if v >= 맵.max() / 2 else "+" if v > 0 else "." for v in 줄))
