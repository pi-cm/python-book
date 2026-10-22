"""1권 부록 D. 자주 만나는 오류와 해결 — D.7 오류는 안 나는데 결과가 이상할 때

원고: manuscript/appendix/D-troubleshooting.md (750줄부터)
"""

# ---- 원고 750줄 ----
print(0.1 + 0.2 == 0.3)        # False
print(0.1 + 0.2)               # 0.30000000000000004

import math
print(math.isclose(0.1 + 0.2, 0.3))   # True

from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))  # True
print(round(2.675, 2))         # 2.67
