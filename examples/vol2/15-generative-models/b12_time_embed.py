# [2권 Chapter 15. 생성 모델: 오토인코더, VAE, 확산 모델 입문 · 15.8 확산 모델: 잡음을 걷어 내며 그리기 · manuscript-vol2/chapters/15-generative-models.md:954]
import torch
import torch.nn.functional as F

from 확산도구 import 시간_임베딩

t = torch.tensor([0, 10, 11, 500, 999])
e = 시간_임베딩(t, 128)
print("모양:", tuple(t.shape), "→", tuple(e.shape))
print("t=10의 앞 4칸:", [round(v, 3) for v in e[1, :4].tolist()])

# 가까운 단계끼리는 비슷하고, 먼 단계끼리는 다르다 (코사인 유사도)
for i, j in [(1, 2), (1, 3), (3, 4), (1, 4)]:
    print(f"t={t[i].item():3} 와 t={t[j].item():3}: {F.cosine_similarity(e[i], e[j], dim=0):.3f}")
