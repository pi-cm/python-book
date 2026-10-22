# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.5 오토인코더로 새 그림을 그릴 수 있을까 · manuscript-vol2/chapters/15-generative-models.md:460]
import torch

from 생성도구 import 격자_저장, 사진_불러오기, 오토인코더, 오토인코더_학습

torch.manual_seed(0)
X_학습, _ = 사진_불러오기(학습=True)
모델 = 오토인코더_학습(오토인코더(잠재_크기=2), X_학습, 에폭=5, 출력=False).eval()

with torch.no_grad():
    점 = 모델.인코더(X_학습)
    print("잠재 공간 범위: 1번 칸", [round(v, 1) for v in (점[:, 0].min().item(), 점[:, 0].max().item())],
          "/ 2번 칸", [round(v, 1) for v in (점[:, 1].min().item(), 점[:, 1].max().item())])
    print("잠재 벡터의 평균:", [round(v, 2) for v in 점.mean(dim=0).tolist()],
          "표준편차:", [round(v, 2) for v in 점.std(dim=0).tolist()])

    # 범위 안의 점이라도 '빈 땅'이면? 1번 칸 0, 2번 칸 7 근처는 데이터가 거의 없다
    빈_땅 = torch.tensor([[0.0, 7.0]])
    가까운_개수 = ((점 - 빈_땅).norm(dim=1) < 1.0).sum().item()
    print("(0, 7)에서 거리 1 안에 있는 학습 사진:", 가까운_개수, "장")

    # 표준정규분포에서 아무 점이나 15개 골라 디코더에 넣고, 마지막 칸에는 빈 땅을 넣어 보기
    아무_점 = torch.randn(15, 2)
    격자_저장(모델.디코더(torch.cat([아무_점, 빈_땅])), "ae_random.png")
