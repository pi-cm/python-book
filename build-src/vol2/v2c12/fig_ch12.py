"""12장 그림: 위치 인코딩 표, 학습된 작은 GPT의 어텐션 가중치."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

sys.path.insert(0, str(Path(__file__).parent))
from 법전 import 준비
from 작은GPT import 학습된_모델

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
출력_폴더 = Path("/Users/changmin/git/python-book/manuscript-vol2/assets/images/ch12")

# 1) 사인·코사인 위치 인코딩
길이, 차원 = 100, 64
위치 = torch.arange(길이).unsqueeze(1)
빠르기 = 10000 ** (-torch.arange(0, 차원, 2) / 차원)
표 = torch.zeros(길이, 차원)
표[:, 0::2] = torch.sin(위치 * 빠르기)
표[:, 1::2] = torch.cos(위치 * 빠르기)
fig, ax = plt.subplots(figsize=(7, 3.6), dpi=200)
im = ax.imshow(표.T, aspect="auto", cmap="RdBu", vmin=-1, vmax=1)
ax.set_xlabel("위치 (몇 번째 글자)")
ax.set_ylabel("칸 번호 (0~63)")
fig.colorbar(im, ax=ax, fraction=0.03)
fig.tight_layout()
fig.savefig(출력_폴더 / "positional_encoding.png")

# 2) 학습된 모델의 어텐션: 1층 3번 헤드, 3층 2번 헤드
모델, 글자 = 학습된_모델()
_, _, 검증 = 준비()
x = 검증[1000:1128].unsqueeze(0)
with torch.no_grad():
    모델(x)
시작, 끝 = 84, 128
라벨 = [("\\n" if c == "\n" else "_" if c == " " else c) for c in 글자.디코딩(x[0, 시작:끝])]
fig, axes = plt.subplots(1, 2, figsize=(11, 5.6), dpi=200)
for ax, (층, 헤드) in zip(axes, [(0, 3), (2, 2)]):
    w = 모델.블록들[층].어텐션.가중치[0, 헤드, 시작:끝, 시작:끝]
    ax.imshow(w, cmap="Greys", vmin=0, vmax=1)
    ax.set_title(f"{층 + 1}층 {헤드}번 헤드")
    ax.set_xticks(range(len(라벨)), 라벨, fontsize=6)
    ax.set_yticks(range(len(라벨)), 라벨, fontsize=6)
    ax.set_xlabel("보는 글자 (키)")
    ax.set_ylabel("지금 글자 (쿼리)")
fig.tight_layout()
fig.savefig(출력_폴더 / "attention_heads.png")
print("saved")
