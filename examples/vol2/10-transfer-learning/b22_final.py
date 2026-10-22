# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.9 실습: 데이터가 적을수록 전이 학습이 빛난다 · manuscript-vol2/chapters/10-transfer-learning.md:1259]
import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 정확도, 한_에폭_학습

이름 = ["경작지", "숲", "초지", "고속도로", "산업지역", "목초지", "과수원", "주거지", "강", "바다·호수"]
장치 = 장치_고르기()
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 100)
시험_사진, 시험_정답 = 유로샛_불러오기("시험", 100)     # 여기서 처음이자 마지막으로 쓴다
학습_로더 = 로더_만들기(학습_사진, 학습_정답, 증강=True, 섞기=True)

torch.manual_seed(0)
모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
모델.fc = nn.Linear(512, 10)
모델.to(장치)
몸통_파라미터 = [p for n, p in 모델.named_parameters() if not n.startswith("fc.")]
옵티마이저 = torch.optim.Adam([{"params": 몸통_파라미터, "lr": 1e-4},
                            {"params": 모델.fc.parameters(), "lr": 1e-3}])
for 에폭 in range(4):                       # 1,000장 ÷ 64 = 16배치 × 4에폭 = 64번 고치기
    한_에폭_학습(모델, 학습_로더, 옵티마이저, 장치)
print(f"시험 정확도 {정확도(모델, 로더_만들기(시험_사진, 시험_정답), 장치):.1%}")

# 클래스별 정확도와 헷갈린 짝(6장 6.11절과 같은 방법)
모델.eval()
with torch.no_grad():
    예측 = torch.cat([모델(x.to(장치)).argmax(1).cpu() for x, _ in 로더_만들기(시험_사진, 시험_정답)])
for k in range(10):
    print(f"{이름[k]:5} {(예측[시험_정답 == k] == k).float().mean():5.0%}", end="  " if k % 5 != 4 else "\n")
혼동 = torch.bincount(시험_정답 * 10 + 예측, minlength=100).reshape(10, 10)   # (정답, 예측) 칸마다 개수
혼동.fill_diagonal_(0)
for 위치 in 혼동.flatten().topk(3).indices.tolist():
    정답, 답 = divmod(위치, 10)
    print(f"정답 {이름[정답]} → 예측 {이름[답]}: {혼동[정답, 답]}번")
