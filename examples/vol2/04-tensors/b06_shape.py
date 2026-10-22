# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.2 모양과 차원 · manuscript-vol2/chapters/04-tensors.md:225]
import torch

점 = torch.tensor(36.5)                         # 0차원: 체온 하나
선 = torch.tensor([36.5, 36.7, 36.6])           # 1차원: 하루 세 번 잰 체온
면 = torch.tensor([[36.5, 36.7, 36.6],
                  [36.4, 36.9, 36.8]])          # 2차원: 이틀치
책 = torch.zeros(7, 2, 3)                        # 3차원: 일주일치 표 7장

for 이름, t in [("점", 점), ("선", 선), ("면", 면), ("책", 책)]:
    print(f"{이름}: ndim={t.ndim}, shape={tuple(t.shape)}, 숫자 {t.numel()}개")
