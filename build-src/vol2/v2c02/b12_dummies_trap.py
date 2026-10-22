import pandas as pd

학습 = pd.DataFrame({"지역": ["서울", "부산", "대구", "서울"]})
시험 = pd.DataFrame({"지역": ["부산", "광주"]})

print("학습:", pd.get_dummies(학습).columns.tolist())
print("시험:", pd.get_dummies(시험).columns.tolist())
