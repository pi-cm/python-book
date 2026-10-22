"""1권 부록 D. 자주 만나는 오류와 해결 — D.7 오류는 안 나는데 결과가 이상할 때

원고: manuscript/appendix/D-troubleshooting.md (694줄부터)
"""

# ---- 원고 694줄 ----
def add_item(item, box=[]):
    box.append(item)
    return box

print(add_item("사과"))   # ['사과']
print(add_item("배"))     # ['사과', '배']
