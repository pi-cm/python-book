# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.3 순서를 알아야 풀리는 문제: 괄호 짝 맞추기 · manuscript-vol2/chapters/11-rnn-lstm.md:438]
import torch
from torch import nn

from 괄호도구 import 괄호_만들기, 원핫으로

괄호_학습, y_학습 = 괄호_만들기(3000, [20], 씨앗=0)
X_학습, _ = 원핫으로(괄호_학습)

torch.manual_seed(0)
rnn = nn.RNN(3, 32, batch_first=True)
판단 = nn.Linear(32, 2)
모델 = lambda x: 판단(rnn(x)[1][-1])               # 마지막 메모로 판단
옵티마이저 = torch.optim.Adam([*rnn.parameters(), *판단.parameters()], lr=3e-3)
for _ in range(30):                                 # 앞 예제와 같은 학습
    for 묶음 in torch.randperm(len(X_학습)).split(64):
        손실 = nn.functional.cross_entropy(모델(X_학습[묶음]), y_학습[묶음])
        옵티마이저.zero_grad()
        손실.backward()
        옵티마이저.step()

펼친_MLP = nn.Sequential(nn.Flatten(), nn.Linear(20 * 3, 64), nn.ReLU(), nn.Linear(64, 2))
for 길이 in [20, 24, 30, 40]:
    괄호들, 정답 = 괄호_만들기(1000, [길이], 씨앗=2)
    X, _ = 원핫으로(괄호들)
    with torch.no_grad():
        정확도 = (모델(X).argmax(dim=1) == 정답).float().mean().item()
    try:
        펼친_MLP(X)
        mlp_결과 = "실행됨"
    except RuntimeError as e:
        mlp_결과 = "모양 오류 " + str(e)[str(e).index("("):]
    print(f"길이 {길이}: RNN 정확도 {정확도:.1%} / 펼친 MLP {mlp_결과}")
