# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.5 첫 CNN으로 옷 사진 분류하기 · manuscript-vol2/chapters/09-cnn.md:590]
import torch

from 옷도구 import 옷CNN, 시험_데이터, 의류분류기

이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트", "샌들", "셔츠", "운동화", "가방", "앵클부츠"]
X, y = 시험_데이터()

예측 = {}
for 별명, 모델, 파일 in [("MLP", 의류분류기(), "fashion_mlp.pt"), ("CNN", 옷CNN(), "fashion_cnn.pt")]:
    모델.load_state_dict(torch.load(파일, weights_only=True))
    모델.eval()
    with torch.no_grad():
        예측[별명] = 모델(X).argmax(dim=1)
    print(f"{별명} 전체 정확도 {(예측[별명] == y).float().mean():.2%}")

print("클래스     MLP     CNN    차이")
for k in range(10):
    a, b = [(예측[m][y == k] == k).float().mean().item() for m in ("MLP", "CNN")]
    print(f"{이름[k]:6} {a:6.1%}  {b:6.1%}  {(b - a) * 100:+5.1f}%p")

for m in ("MLP", "CNN"):                         # 모델마다 가장 많이 헷갈린 짝 3개
    혼동 = torch.zeros(10, 10, dtype=torch.int64)
    혼동.index_put_((y, 예측[m]), torch.ones(len(y), dtype=torch.int64), accumulate=True)
    혼동.fill_diagonal_(0)
    짝들 = [divmod(i, 10) for i in 혼동.flatten().topk(3).indices.tolist()]
    print(m, "헷갈림:", ", ".join(f"{이름[a]}→{이름[b]} {혼동[a, b]}번" for a, b in 짝들))
