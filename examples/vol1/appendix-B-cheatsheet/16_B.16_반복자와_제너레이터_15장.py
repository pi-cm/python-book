"""1권 부록 B. 한눈에 보는 파이썬 — B.16 반복자와 제너레이터 (15장)

원고: manuscript/appendix/B-cheatsheet.md (752줄부터)
"""

# ---- 원고 752줄 ----
it = iter([10, 20])
print(next(it), next(it), next(it, "끝"))   # 10 20 끝

def countdown(n):
    while n > 0:
        yield n                 # 값을 하나 내주고 여기서 멈춤
        n -= 1

print(list(countdown(3)))       # [3, 2, 1]

def read_upper(lines):
    for line in lines:
        yield line.upper()

def chain_all(*iterables):
    for it in iterables:
        yield from it           # 다른 반복 가능 객체를 그대로 넘김

print(list(chain_all("ab", [1, 2])))     # ['a', 'b', 1, 2]
print(list(read_upper(["a", "b"])))      # ['A', 'B']
gen = (x * x for x in range(3))
print(sum(gen), sum(gen))                # 5 0

# ---- 원고 781줄 ----
import itertools as itt

print(list(itt.islice(itt.count(10, 5), 3)))       # [10, 15, 20]
print(list(itt.chain([1, 2], [3])))                # [1, 2, 3]
print(list(itt.accumulate([1, 2, 3, 4])))          # [1, 3, 6, 10]
print(list(itt.pairwise("abcd")))                  # [('a', 'b'), ('b', 'c'), ('c', 'd')]
print(list(itt.batched(range(7), 3)))              # [(0, 1, 2), (3, 4, 5), (6,)]
print(list(itt.combinations("abc", 2)))            # [('a', 'b'), ('a', 'c'), ('b', 'c')]
print(len(list(itt.permutations("abc"))))          # 6
print([(k, len(list(g))) for k, g in itt.groupby("aabccc")])  # [('a', 2), ('b', 1), ('c', 3)]
