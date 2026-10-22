import hashlib
import json
from pathlib import Path

import numpy as np
import torch

from 맛집데이터 import 데이터_만들기, 음식들, 지역들
from 추천학습 import 학습설정, 학습하기, 좋았던_쌍
from 투타워 import 투타워

기준일 = 330                                          # 서비스를 여는 날: 이날 전의 기록을 모두 쓴다
데이터 = 데이터_만들기(씨앗=0)
식당, 사용자 = 데이터.식당, 데이터.사용자
지난_기록 = 데이터.방문[데이터.방문["날짜"] < 기준일]
쌍 = 좋았던_쌍(지난_기록)
영업중 = (식당["개업일"] < 기준일).to_numpy()

torch.manual_seed(0)
타워 = 투타워(사용자, 식당)
학습하기(타워, 쌍, torch.tensor(np.flatnonzero(영업중)), 학습설정(손실="bpr", 에폭=55))  # 검증 없이 정한 에폭만큼
타워.eval()

아는_사용자 = np.isin(np.arange(len(사용자)), 쌍[:, 0].numpy())
아는_식당 = torch.tensor(np.isin(np.arange(len(식당)), 쌍[:, 1].numpy()))[:, None]
with torch.no_grad():
    전체 = torch.arange(len(식당))
    식당_벡터 = torch.where(아는_식당, 타워.식당_벡터(전체), 타워.식당_벡터(전체, 번호_쓰기=False))
    사용자_벡터 = 타워.사용자_벡터(torch.arange(len(사용자)))

폴더 = Path("restaurant_service/artifacts")
폴더.mkdir(parents=True, exist_ok=True)
np.savez(폴더 / "vectors.npz", user_vectors=사용자_벡터.numpy(), restaurant_vectors=식당_벡터.numpy(),
         known_users=아는_사용자)
방문수 = np.bincount(지난_기록["식당"], minlength=len(식당))
가본_곳 = 지난_기록.groupby("사용자")["식당"].apply(lambda s: sorted(set(s)))
목록 = {
    "as_of_day": 기준일, "areas": 지역들,
    "restaurants": [{"id": int(r.식당), "name": r.이름, "area": 지역들[r.지역], "cuisine": 음식들[r.음식],
                     "price": int(r.가격대), "open": bool(영업중[r.식당]), "visits": int(방문수[r.식당])}
                    for r in 식당.itertuples()],
    "users": [{"home": 지역들[동네], "visited": [int(i) for i in 가본_곳.get(u, [])]}
              for u, 동네 in enumerate(사용자["동네"])],
}
(폴더 / "catalog.json").write_text(json.dumps(목록, ensure_ascii=False), encoding="utf-8")

# 확인: NumPy로 계산한 상위 10개가 PyTorch 모델의 상위 10개와 같은가
읽은 = np.load(폴더 / "vectors.npz")
with torch.no_grad():
    모델_점수 = 사용자_벡터 @ 식당_벡터.T
같음 = all(np.array_equal(np.argsort(-(읽은["restaurant_vectors"] @ 읽은["user_vectors"][u]))[:10],
                          모델_점수[u].topk(10).indices.numpy()) for u in range(200))
print(f"아는 사용자 {아는_사용자.sum():,}명 / {len(사용자):,}명, 영업 중인 식당 {영업중.sum()}곳 "
      f"(그중 기록 없는 새 식당 {(영업중 & ~아는_식당[:, 0].numpy()).sum()}곳)")
print("NumPy와 PyTorch의 상위 10개가 같은가:", 같음)
for 파일 in sorted(폴더.iterdir()):
    print(f"{파일.name:14} {파일.stat().st_size / 1024:7.1f} KB  sha256 {hashlib.sha256(파일.read_bytes()).hexdigest()[:12]}")
