"""1권 레퍼런스 E. 표준 라이브러리 지도 — 들어가며

원고: manuscript/references/E-standard-library.md (7줄부터)
"""

# ---- 원고 7줄 ----
import sys

names = sorted(m for m in sys.stdlib_module_names if not m.startswith("_"))
print(len(names))   # 212
print(names[:6])    # ['abc', 'aifc', 'antigravity', 'argparse', 'array', 'ast']
