# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.6 순서 알려 주기: 위치 정보 · manuscript-vol2/chapters/12-transformer.md:549]
import matplotlib
import matplotlib.pyplot as plt
import torch

matplotlib.use("Agg")                               # 창을 띄우지 않고 파일로만 그리기
plt.rcParams["font.family"] = "AppleGothic"         # macOS 한글 글꼴
plt.rcParams["axes.unicode_minus"] = False
torch.set_printoptions(precision=2, sci_mode=False)


def 사인_위치_인코딩(길이: int, 차원: int) -> torch.Tensor:
    """위치마다 빠르기가 다른 사인·코사인 물결의 값을 이어 붙인 표 (길이, 차원)."""
    위치 = torch.arange(길이).unsqueeze(1)                          # (길이, 1)
    빠르기 = 10000 ** (-torch.arange(0, 차원, 2) / 차원)            # (차원/2,): 1부터 점점 느리게
    표 = torch.zeros(길이, 차원)
    표[:, 0::2] = torch.sin(위치 * 빠르기)                           # 짝수 칸: 사인
    표[:, 1::2] = torch.cos(위치 * 빠르기)                           # 홀수 칸: 코사인
    return 표


표 = 사인_위치_인코딩(100, 64)
print("모양:", tuple(표.shape))
print(표[:4, :6])                                   # 위치 0~3의 앞 칸 여섯 개

# 위치 20과 다른 위치들의 코사인 유사도: 가까울수록 닮았다
단위 = 표 / 표.norm(dim=1, keepdim=True)
닮음 = 단위 @ 단위[20]
for 위치 in [20, 21, 22, 25, 30, 40, 60, 99]:
    print(f"위치 20 vs {위치:2d}: {닮음[위치]:.3f}")

# 표 전체를 그림으로: 가로는 위치, 세로는 칸 번호
그림, 축 = plt.subplots(figsize=(7, 3.6))
색 = 축.imshow(표.T, aspect="auto", cmap="RdBu", vmin=-1, vmax=1)
축.set_xlabel("위치 (몇 번째 글자)")
축.set_ylabel("칸 번호 (0~63)")
그림.colorbar(색, ax=축, fraction=0.03)
그림.tight_layout()
그림.savefig("positional_encoding.png", dpi=200)
