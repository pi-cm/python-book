"""1권 부록 D. 자주 만나는 오류와 해결 — D.6 모듈, 파일, 재귀

원고: manuscript/appendix/D-troubleshooting.md (621줄부터)
"""

# ---- 원고 621줄 ----
# 윈도우 메모장 등에서 CP949로 저장된 파일을 UTF-8로 읽음
print(open('cp949.txt', encoding='utf-8').read())
