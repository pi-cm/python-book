"""1권 부록 D. 자주 만나는 오류와 해결 — D.7 오류는 안 나는데 결과가 이상할 때

원고: manuscript/appendix/D-troubleshooting.md (728줄부터)
"""

# ---- 원고 728줄 ----
import copy

a = [[1, 2], [3, 4]]
b = a.copy()          # 바깥 리스트만 새로, 안쪽은 공유 (얕은 복사)
b[0].append(99)
print(a)              # [[1, 2, 99], [3, 4]]

c = copy.deepcopy(a)  # 안쪽까지 모두 새로 (깊은 복사)
c[0].append(100)
print(a)              # [[1, 2, 99], [3, 4]]

board = [[0] * 3 for _ in range(3)]   # 줄마다 새 리스트
board[0][0] = 1
print(board)          # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
