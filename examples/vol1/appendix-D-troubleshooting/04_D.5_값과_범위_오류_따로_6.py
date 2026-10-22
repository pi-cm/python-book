"""1권 부록 D. 자주 만나는 오류와 해결 — D.5 값과 범위 오류

원고: manuscript/appendix/D-troubleshooting.md (550줄부터)
"""

# ---- 원고 550줄 ----
d = {'a': 1, 'b': 2}
for k in d:
    if d[k] == 1:
        del d[k]
