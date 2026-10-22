# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.3 데이터 누수: 시험 문제가 새는 길 · manuscript-vol2/chapters/02-data-preparation.md:333]
import numpy as np
from sklearn.model_selection import GroupShuffleSplit, train_test_split

rng = np.random.default_rng(0)
# 환자 50명이 각자 4번씩 검사받은 기록 200줄 (예제용)
환자번호 = np.repeat(np.arange(50), 4)
X = rng.normal(size=(200, 3))

_, _, 학습_환자, 시험_환자 = train_test_split(X, 환자번호, test_size=0.25, random_state=0)
겹침 = set(학습_환자) & set(시험_환자)
print(f"줄 단위로 섞어 나누기: 양쪽에 다 나온 환자 {len(겹침)}명")

나누개 = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=0)
학습_위치, 시험_위치 = next(나누개.split(X, groups=환자번호))
겹침 = set(환자번호[학습_위치]) & set(환자번호[시험_위치])
print(f"환자 단위로 나누기:    양쪽에 다 나온 환자 {len(겹침)}명")
print("학습/시험 줄 수:", len(학습_위치), len(시험_위치))
