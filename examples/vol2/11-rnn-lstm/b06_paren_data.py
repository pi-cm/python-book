# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.3 순서를 알아야 풀리는 문제: 괄호 짝 맞추기 · manuscript-vol2/chapters/11-rnn-lstm.md:322]
from collections import Counter

from 괄호도구 import 괄호_만들기, 원핫으로, 짝맞나

print(짝맞나("(()())"), 짝맞나("())(()"), 짝맞나("(()"))

괄호들, 정답 = 괄호_만들기(3000, 길이들=[20], 씨앗=0)
for 괄호, 답 in zip(괄호들[:4], 정답[:4].tolist()):
    print(괄호, "짝 맞음" if 답 else "짝 틀림")
print("짝 맞음 비율:", 정답.float().mean().item())
print("'('와 ')' 개수가 늘 같은가:", all(Counter(괄호)["("] == 10 for 괄호 in 괄호들))

X, 길이 = 원핫으로(괄호들[:2])
print("원-핫 모양:", tuple(X.shape))
print(X[0, :3])
