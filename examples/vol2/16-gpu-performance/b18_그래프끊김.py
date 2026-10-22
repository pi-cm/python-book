# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.8 torch.compile: 모델을 미리 번역해 두기 · manuscript-vol2/chapters/16-gpu-performance.md:1056]
import torch


def 깐깐한_함수(x: torch.Tensor) -> torch.Tensor:
    y = x.sin() * 2
    print("중간 점검")                 # 파이썬의 부수 효과
    if y.sum() > 0:                    # 텐서 값을 보고 갈림길을 고른다
        return y.cos()
    return y + 1


설명 = torch._dynamo.explain(깐깐한_함수)(torch.randn(8))     # 내부 도구(_dynamo)라 버전마다 바뀔 수 있다
print("그래프 수:", 설명.graph_count, "| 끊긴 곳:", 설명.graph_break_count)
for 이유 in 설명.break_reasons:
    print(" -", 이유.reason.splitlines()[0][:70])

torch.compiler.reset()
try:
    torch.compile(깐깐한_함수, fullgraph=True)(torch.randn(8))   # 끊기면 오류를 내라
except Exception as 오류:
    print("fullgraph=True:", type(오류).__name__)
