# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.10 실습: 통신사 고객 이탈 데이터 손질하기 · manuscript-vol2/chapters/02-data-preparation.md:1154]
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

데이터_폴더 = Path(os.environ.get("BOOK_DATA_DIR", "data"))
고객 = pd.read_csv(데이터_폴더 / "통신사_고객.csv")

# 1) 행 단위 정리 (앞에서 살펴본 규칙 그대로)
고객 = 고객.drop_duplicates().copy()
고객["지역"] = 고객["지역"].str.strip().str.removesuffix("시")
고객.loc[고객["나이"] > 100, "나이"] = np.nan

# 2) 특성과 정답 나누기: 고객번호는 이름표일 뿐이라 뺀다
X = 고객.drop(columns=["고객번호", "이탈"])
y = 고객["이탈"]

# 3) 학습 60 / 검증 20 / 테스트 20, 이탈 비율을 똑같이 유지
X_나머지, X_테스트, y_나머지, y_테스트 = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)
X_학습, X_검증, y_학습, y_검증 = train_test_split(
    X_나머지, y_나머지, test_size=0.25, stratify=y_나머지, random_state=42)
for 이름, 정답 in [("학습", y_학습), ("검증", y_검증), ("테스트", y_테스트)]:
    print(f"{이름}: {len(정답)}명, 이탈 {정답.mean():.1%}")


# 4) 열 종류마다 다른 전처리
def 전처리_만들기() -> ColumnTransformer:
    """숫자·범주·순서 열을 각자 맞는 방법으로 처리하는 전처리기를 만든다."""
    숫자 = make_pipeline(SimpleImputer(strategy="median", add_indicator=True),
                         StandardScaler())
    범주 = make_pipeline(SimpleImputer(strategy="constant", fill_value="모름"),
                         OneHotEncoder(handle_unknown="ignore"))
    순서 = OrdinalEncoder(categories=[["베이직", "스탠다드", "프리미엄"],
                                      ["무약정", "1년", "2년"]])
    return ColumnTransformer([
        ("숫자", 숫자, ["나이", "가입개월", "월요금", "상담횟수"]),
        ("범주", 범주, ["지역"]),
        ("순서", 순서, ["요금제", "약정"]),
    ])


def 성적(모델: Pipeline, X: pd.DataFrame, y: pd.Series) -> str:
    """정확도와 실제 이탈자 중 몇 명을 찾았는지를 한 줄로 만든다."""
    예측 = 모델.predict(X)
    찾음 = int(((예측 == 1) & (y == 1)).sum())
    return f"정확도 {(예측 == y).mean():.1%}, 이탈자 {int(y.sum())}명 중 {찾음}명 찾음"


# 5) 후보 둘을 검증 데이터로 비교 (테스트 데이터는 아직 금고 안에)
for 가중치 in [None, "balanced"]:
    후보 = Pipeline([("전처리", 전처리_만들기()),
                     ("분류", LogisticRegression(class_weight=가중치, max_iter=1000))])
    후보.fit(X_학습, y_학습)
    print(f"[검증] class_weight={가중치!s:<8} {성적(후보, X_검증, y_검증)}")

# 6) 고른 설정으로 학습+검증 데이터에 다시 학습하고, 테스트는 마지막에 딱 한 번
최종 = Pipeline([("전처리", 전처리_만들기()),
                 ("분류", LogisticRegression(class_weight="balanced", max_iter=1000))])
최종.fit(X_나머지, y_나머지)
print(f"[테스트] {성적(최종, X_테스트, y_테스트)}")
print("전처리 후 특성:", len(최종[:-1].get_feature_names_out()), "개")

# 7) 새 고객: 처음 보는 지역, 빈칸이 있어도 원본 모양 그대로 넣으면 된다
새_고객 = pd.DataFrame({
    "나이": [23, np.nan], "지역": ["세종", "서울"], "요금제": ["프리미엄", "베이직"],
    "약정": ["무약정", "2년"], "가입개월": [3, 60], "월요금": [91000, np.nan],
    "상담횟수": [4, 0],
})
print("새 고객 이탈 확률:", 최종.predict_proba(새_고객)[:, 1].round(2))
