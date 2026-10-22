# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.9 글 만들기와 들여다보기 · manuscript-vol2/chapters/12-transformer.md:1329]
import matplotlib
import matplotlib.pyplot as plt
import torch

from 법전 import 준비
from 작은GPT import 학습된_모델

matplotlib.use("Agg")                               # 창을 띄우지 않고 파일로만 그리기
plt.rcParams["font.family"] = "AppleGothic"         # macOS 한글 글꼴

모델, 표 = 학습된_모델()
_, _, 검증_데이터 = 준비()
x = 검증_데이터[1000:1128].unsqueeze(0)       # 학습 때 못 본 128글자
글 = 표.디코딩(x[0])
with torch.no_grad():
    로짓 = 모델(x)

# 1) 첫 층의 헤드들은 평균 몇 칸 앞을 보고, 바로 앞 글자에 얼마를 줄까 (20번째 글자부터 평균)
거리 = (torch.arange(128)[:, None] - torch.arange(128)[None, :]).clamp(min=0).float()
가중치 = 모델.블록들[0].어텐션.가중치[0]                     # (헤드, 128, 128)
for h in range(4):
    평균_거리 = (가중치[h] * 거리).sum(dim=-1)[20:].mean()
    바로_앞 = 가중치[h].diagonal(-1)[20:].mean()
    print(f"1층 {h}번 헤드: 평균 {평균_거리:4.1f}칸 앞, 바로 앞 글자에 {바로_앞:.2f}")

# 2) "제1006" 다음 글자를 맞힐 때, 층마다 각 헤드가 가장 많이 본 글자
자리 = 글.index("제1006") + 4                                  # '6'의 자리
값, 번호 = 로짓[0, 자리].softmax(dim=-1).topk(2)
print(repr(글[자리 - 30:자리 + 1]), "다음 글자 예측:",
      [(표.글자들[i], round(p, 3)) for p, i in zip(값.tolist(), 번호.tolist())])
for 층, 블 in enumerate(모델.블록들, start=1):
    본_곳 = []
    for h, 줄 in enumerate(블.어텐션.가중치[0, :, 자리]):
        j = 줄.argmax().item()
        본_곳.append(f"{글[j - 2:j]!r}[{글[j]!r}] {줄[j]:.2f}")
    print(f"{층}층:", " | ".join(본_곳))

# 3) 1층 3번 헤드와 3층 2번 헤드의 가중치 표 일부(뒤쪽 44글자)를 그림으로
시작 = 84
라벨 = ["\\n" if c == "\n" else "_" if c == " " else c for c in 글[시작:]]   # 줄바꿈·띄어쓰기를 보이게
그림, 축들 = plt.subplots(1, 2, figsize=(11, 5.6))
for 축, (층, h) in zip(축들, [(0, 3), (2, 2)]):
    축.imshow(모델.블록들[층].어텐션.가중치[0, h, 시작:, 시작:], cmap="Greys", vmin=0, vmax=1)
    축.set_title(f"{층 + 1}층 {h}번 헤드")
    축.set_xticks(range(len(라벨)), 라벨, fontsize=6)
    축.set_yticks(range(len(라벨)), 라벨, fontsize=6)
    축.set_xlabel("보는 글자 (키)")
    축.set_ylabel("지금 글자 (쿼리)")
그림.tight_layout()
그림.savefig("attention_heads.png", dpi=200)
