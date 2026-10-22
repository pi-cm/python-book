# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.3 이 장의 데이터: EuroSAT 위성 사진 · manuscript-vol2/chapters/10-transfer-learning.md:396]
import torch

from 전이도구 import 로더_만들기, 유로샛_불러오기

학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
시험_사진, 시험_정답 = 유로샛_불러오기("시험", 100)
for 이름, 사진, 정답 in [("학습", 학습_사진, 학습_정답), ("검증", 검증_사진, 검증_정답), ("시험", 시험_사진, 시험_정답)]:
    print(f"{이름}: {tuple(사진.shape)} {사진.dtype}, 클래스별 {torch.bincount(정답).tolist()}")
print(f"학습 사진이 차지하는 메모리 {학습_사진.numel() * 학습_사진.element_size() / 1024**2:.1f}MB")

x, y = next(iter(로더_만들기(학습_사진, 학습_정답, 증강=True, 섞기=True)))
print("배치 하나:", tuple(x.shape), x.dtype, y[:8].tolist())
print("채널별 평균:", [f"{v:.2f}" for v in x.mean(dim=(0, 2, 3)).tolist()],
      "표준편차:", [f"{v:.2f}" for v in x.std(dim=(0, 2, 3)).tolist()])
