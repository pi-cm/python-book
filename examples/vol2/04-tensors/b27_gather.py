# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.4 인덱싱과 슬라이싱 · manuscript-vol2/chapters/04-tensors.md:514]
import torch

# 사진 4장에 대해 모델이 낸 클래스별 확률 (0: 고양이, 1: 개, 2: 새)
확률 = torch.tensor([[0.7, 0.2, 0.1],
                     [0.1, 0.8, 0.1],
                     [0.3, 0.3, 0.4],
                     [0.6, 0.3, 0.1]])
정답 = torch.tensor([0, 1, 2, 1])            # 장마다 정답 클래스 번호

예측 = 확률.argmax(dim=1)
print("예측:", 예측, "정확도:", (예측 == 정답).float().mean())

# 방법 1: 줄 번호 목록과 칸 번호 목록을 짝지어 꺼내기
print(확률[torch.arange(4), 정답])

# 방법 2: gather. dim=1 방향에서 index가 가리키는 칸을 꺼낸다
번호표 = 정답.unsqueeze(1)                   # (4,) → (4, 1): 확률과 차원 수를 맞춘다
정답_확률 = 확률.gather(dim=1, index=번호표)
print(정답_확률.shape)
print(정답_확률.squeeze(1))

# 정답 확률이 낮을수록 커지는 벌점: -log를 씌워 평균
print(정답_확률.log().neg().mean())
