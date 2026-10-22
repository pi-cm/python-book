import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.tree import DecisionTreeRegressor

X, y = load_diabetes(return_X_y=True)

예측 = np.full(len(y), y.mean())         # 0단계: 모두 평균으로 찍기
print(f"0단계(평균으로 찍기) 평균 오차(RMSE): {np.sqrt(np.mean((y - 예측) ** 2)):.1f}")
학습률 = 0.3
for 단계 in range(1, 6):
    잔차 = y - 예측                      # 지금까지 틀린 만큼 (오답 노트)
    작은_나무 = DecisionTreeRegressor(max_depth=2, random_state=0).fit(X, 잔차)
    예측 = 예측 + 학습률 * 작은_나무.predict(X)   # 오답을 조금만 고친다
    오차 = np.sqrt(np.mean((y - 예측) ** 2))
    print(f"{단계}단계 뒤 평균 오차(RMSE): {오차:.1f}")
