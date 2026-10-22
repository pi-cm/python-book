"""1권 부록 B. 한눈에 보는 파이썬 — B.3 문자열 (2장, 6장)

원고: manuscript/appendix/B-cheatsheet.md (112줄부터)
"""

# ---- 원고 112줄 ----
s = "Python"
print(s[0], s[-1], s[1:4], s[:2], s[2:])  # P n yth Py thon
print(s[::-1], s[::2])                      # nohtyP Pto

# ---- 원고 140줄 ----
print("  hi \n".strip(), "hello".find("z"), "banana".count("a"))  # hi -1 3
print("test.py".endswith((".py", ".txt")), "7".zfill(3))         # True 007
print("k=v=w".partition("="))                                    # ('k', '=', 'v=w')
print("한".encode())                                             # b'\xed\x95\x9c'
print(len("한글"), len("한글".encode("utf-8")))                   # 2 6
