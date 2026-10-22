"""1권 부록 D. 자주 만나는 오류와 해결 — D.8 오류 메시지 읽는 법

원고: manuscript/appendix/D-troubleshooting.md (782줄부터)
"""

# ---- 원고 782줄 ----
def average(scores):
    return sum(scores) / len(scores)

def report(students):
    for name, scores in students.items():
        print(name, average(scores))

report({"민수": [90, 80], "지아": []})
