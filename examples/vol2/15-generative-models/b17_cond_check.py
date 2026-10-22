# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.10 실습: 주문한 옷을 그리는 조건부 확산 모델 · manuscript-vol2/chapters/15-generative-models.md:1285]
import torch

from 생성도구 import 사진_불러오기, 채점기_만들기, 이름
from 확산도구 import 그리기, 작은UNet


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


장치 = 장치_고르기()
모델 = 작은UNet(클래스_수=10).to(장치)
모델.load_state_dict(torch.load("조건부_확산.pt", map_location=장치))
채점기 = 채점기_만들기(장치)

# 종류마다 100장씩 주문해서 그리고, 채점기가 주문한 종류로 알아보는지 센다
torch.manual_seed(0)
주문 = torch.arange(10, device=장치).repeat_interleave(100)
그림, _ = 그리기(모델, 1000, 장치, 클래스=주문)
with torch.no_grad():
    판정 = 채점기((그림 + 1) / 2).argmax(dim=1)

X_시험, y_시험 = 사진_불러오기(학습=False)
with torch.no_grad():
    진짜_판정 = 채점기(X_시험.to(장치)).argmax(dim=1).cpu()

print("종류       주문대로 그린 비율   (참고) 진짜 사진 정확도")
for 번호 in range(10):
    맞음 = (판정[주문 == 번호] == 번호).float().mean()
    진짜 = (진짜_판정[y_시험 == 번호] == 번호).float().mean()
    print(f"{이름[번호]:5}     {맞음:10.0%}              {진짜:6.0%}")
print(f"전체       {(판정 == 주문).float().mean():10.1%}              "
      f"{(진짜_판정 == y_시험).float().mean():6.1%}")
