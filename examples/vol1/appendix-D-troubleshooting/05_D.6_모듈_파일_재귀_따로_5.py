"""1권 부록 D. 자주 만나는 오류와 해결 — D.6 모듈, 파일, 재귀

원고: manuscript/appendix/D-troubleshooting.md (643줄부터)
"""

# ---- 원고 643줄 ----
def countdown(n):
    print(n)
    countdown(n - 1)
countdown(3)
