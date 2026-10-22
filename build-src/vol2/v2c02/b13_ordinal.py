import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

만족도 = pd.DataFrame({"만족도": ["보통", "높음", "낮음", "보통", "높음"]})

알아서 = OrdinalEncoder().fit(만족도)
print("순서를 안 정하면:", 알아서.categories_[0].tolist())
print(알아서.transform(만족도).ravel())

순서대로 = OrdinalEncoder(categories=[["낮음", "보통", "높음"]],
                          handle_unknown="use_encoded_value", unknown_value=-1)
순서대로.fit(만족도)
print("순서를 정해 주면:", 순서대로.categories_[0].tolist())
print(순서대로.transform(만족도).ravel())
print("못 본 값:", 순서대로.transform(pd.DataFrame({"만족도": ["매우 높음"]})).ravel())
