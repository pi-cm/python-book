# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.3 이 장의 데이터: EuroSAT 위성 사진 · manuscript-vol2/chapters/10-transfer-learning.md:238]
import torch
from torchvision import datasets
from torchvision.transforms import v2

원본 = datasets.EuroSAT("data", download=True)   # 처음 한 번은 약 90MB를 내려받는다
정답들 = torch.tensor(원본.targets)
print(f"사진 {len(원본):,}장, 크기 {원본[0][0].size}")
for k, (이름, 개수) in enumerate(zip(원본.classes, torch.bincount(정답들).tolist())):
    # 클래스마다 앞 100장의 평균 색(0~255)
    번호 = (정답들 == k).nonzero().flatten()[:100].tolist()
    평균색 = torch.stack([v2.functional.pil_to_tensor(원본[i][0]) for i in 번호]).float().mean(dim=(0, 2, 3))
    print(f"{k} {이름:20} {개수:,}장  평균 색 R·G·B = {평균색.round().int().tolist()}")
