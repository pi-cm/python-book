# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.7 트랜스포머 블록 조립하기 · manuscript-vol2/chapters/12-transformer.md:820]
import torch
from torch import nn

torch.manual_seed(0)
torch.set_printoptions(precision=2)
교차_어텐션 = nn.MultiheadAttention(16, num_heads=4, batch_first=True)
원문 = torch.randn(1, 4, 16)          # 인코더가 읽은 원문 단어 4개 (예: 영어 문장)
번역문 = torch.randn(1, 7, 16)        # 디코더가 지금까지 쓴 번역문 7글자

# 쿼리는 번역문에서, 키와 값은 원문에서: "다음 글자를 쓰려면 원문의 어디를 봐야 하나"
출력, 가중치 = 교차_어텐션(번역문, 원문, 원문)
print("출력", tuple(출력.shape), "가중치", tuple(가중치.shape))
print("번역문 0번 글자가 원문 단어들을 보는 비율:", 가중치[0, 0].detach())
