"""1권 레퍼런스 B. 키워드와 연산자 — 들어가며

원고: manuscript/references/B-keywords-operators.md (7줄부터)
"""

# ---- 원고 7줄 ----
import keyword
print(len(keyword.kwlist))     # 35
print(keyword.softkwlist)      # ['_', 'case', 'match', 'type']
print(keyword.iskeyword('class'), keyword.issoftkeyword('match'))   # True True
