# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.8 작은 GPT 만들기 · manuscript-vol2/chapters/12-transformer.md:951]
from collections import Counter

from 법전 import 글자표, 법전_읽기

글 = 법전_읽기()                       # 처음 한 번은 위키문헌에서 받아 data/법전.txt로 저장
줄들 = 글.splitlines()
print(f"글자 {len(글):,}개, 줄 {len(줄들):,}개")
for 줄 in 줄들[1:4] + 줄들[150:152]:
    print(" ", 줄[:60])

표 = 글자표(글)
print("글자 종류:", len(표))
print("자주 나오는 글자:", Counter(글).most_common(12))
번호들 = 표.인코딩("제1조 ① 대한민국은")
print(번호들.tolist())
print(표.디코딩(번호들))
