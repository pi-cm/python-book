# Chapter 3. scikit-learn으로 보는 고전 머신러닝

> **학습 목표**  
> - scikit-learn 모델이 공통으로 따르는 `fit`·`predict`·`score` 약속을 이해하고 모델을 바꿔 끼우기
> - 선형 회귀·로지스틱 회귀가 무엇을 배우는지(계수) 읽고, 결정 트리·랜덤 포레스트·그래디언트 부스팅의 차이를 설명하기
> - 정답 없는 데이터를 k-means로 묶고, 무리 수를 고르는 방법 알기
> - 정확도·정밀도·재현율·F1·ROC-AUC와 MAE·RMSE·R²를 상황에 맞게 고르기
> - 교차 검증으로 모델을 믿을 만하게 비교하고, 하이퍼파라미터를 탐색하고, 완성한 모델을 파일로 저장하기

---

## 들어가며: 엑셀 표 같은 데이터에도 딥러닝이 필요할까요?

회사에서 받는 데이터의 상당수는 사진이나 문장이 아니라 **표**입니다. 고객 한 명이 한 줄이고, 나이·가입 기간·지난달 구매액 같은 값이 칸마다 들어 있는 엑셀 시트 말이에요. 병원의 검사 수치, 부동산의 면적과 위치, 공장의 센서 기록도 대개 이런 모양입니다.

이런 표 데이터라면 꼭 거대한 신경망을 꺼낼 필요가 없습니다. 수십 년 동안 다듬어진 **고전 머신러닝** 알고리즘이 몇 초 만에 학습하고, 결과를 사람이 읽을 수 있게 설명해 주고, 성능도 딥러닝에 뒤지지 않는 경우가 많거든요. 파이썬에서 이 알고리즘들을 한곳에 모아 둔 도구가 **scikit-learn**(사이킷런)입니다.

1장에서 최근접 이웃 모델을 scikit-learn 한 줄로 바꿔 봤고, 2장에서는 데이터를 나누고 다듬는 법을 배웠습니다. 이번 장에서는 scikit-learn에 들어 있는 대표 모델들을 하나씩 열어 보고, 무엇보다 **모델을 공정하게 채점하는 법**을 익힙니다. 먼저 scikit-learn이 얼마나 일관된 도구인지부터 보겠습니다. 유방암 진단 데이터에 서로 전혀 다른 모델 세 개를 똑같은 코드로 학습시켜 볼게요.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

모델들 = {
    "최근접 이웃": make_pipeline(StandardScaler(), KNeighborsClassifier()),
    "로지스틱 회귀": make_pipeline(StandardScaler(), LogisticRegression()),
    "결정 트리": DecisionTreeClassifier(random_state=42),
}
for 이름, 모델 in 모델들.items():
    모델.fit(X_학습, y_학습)               # 배우기: 모델마다 똑같은 한 줄
    정확도 = 모델.score(X_시험, y_시험)     # 처음 보는 문제로 채점하기
    print(f"{이름}: 시험 정확도 {정확도:.3f}")
```

```text
최근접 이웃: 시험 정확도 0.979
로지스틱 회귀: 시험 정확도 0.986
결정 트리: 시험 정확도 0.923
```

최근접 이웃, 로지스틱 회귀, 결정 트리는 속에서 하는 일이 완전히 다릅니다. 그런데 쓰는 방법은 `fit`으로 배우고 `score`로 채점하는 두 줄로 똑같아요. 이 일관성 덕분에 "어느 모델이 내 데이터에 맞을까?"를 고민할 때 코드를 갈아엎지 않고 모델만 바꿔 끼우며 비교할 수 있습니다. 이 장이 끝날 즈음이면 위의 비교를 훨씬 믿을 만한 방법(교차 검증)으로 다시 하고, 고른 모델을 파일로 저장하는 데까지 가게 됩니다.

> **Q. 따로 설치할 것이 있나요?**
> 없습니다. 1·2장에서 설치한 scikit-learn과 pandas면 충분하고, 모델 저장에 쓰는 `joblib`과 계산에 쓰는 `scipy`는 scikit-learn을 설치할 때 함께 따라옵니다. 이 장의 예제는 scikit-learn 1.9, 파이썬 3.12에서 실행해 확인했습니다.

## 3.1 scikit-learn의 약속: fit, predict, score

### 모든 모델이 같은 모양의 손잡이를 갖고 있습니다

가전제품마다 전원 버튼 위치가 다르면 새 제품을 살 때마다 설명서를 읽어야겠죠. scikit-learn은 모든 모델에 **같은 손잡이**를 달아 두었습니다. 이 장에서 계속 쓸 약속은 다음과 같아요.

| 손잡이 | 하는 일 |
|---|---|
| `모델 = 모델종류(설정=값)` | 모델을 만들면서 **하이퍼파라미터**(사람이 정하는 설정)를 정한다 |
| `모델.fit(X, y)` | 데이터에서 배운다. 지도 학습은 정답 `y`도 함께 준다 |
| `모델.predict(X)` | 새 데이터의 답을 예측한다 |
| `모델.predict_proba(X)` | 분류 모델이 각 답일 **확률**을 돌려준다 |
| `모델.score(X, y)` | 예측해서 채점한다. 분류는 정확도, 회귀는 R²(3.8절) |
| `모델.이름_` | 끝에 밑줄이 붙은 속성은 `fit`으로 **배운 결과**다 |

마지막 줄이 특히 중요합니다. `coef_`, `feature_importances_`, `cluster_centers_`처럼 이름 끝에 밑줄이 붙은 속성은 `fit`을 하기 전에는 없다가 학습이 끝나면 생깁니다. 사람이 정해 주는 하이퍼파라미터(`max_depth=3` 같은)와, 모델이 데이터에서 스스로 찾아낸 **파라미터**(`coef_` 같은)를 이름만 보고 구분할 수 있게 해 둔 약속이에요.

데이터 `X`는 언제나 **(샘플 수, 특성 수)** 모양의 2차원 표입니다. 숫자만 보지 말고 "환자 569명, 검사 수치 30개"처럼 자리마다 이름을 붙여 소리 내어 읽어 보세요. 4장에서 텐서를 다룰 때도 이 습관이 큰 도움이 됩니다. 정답 `y`는 샘플 수만큼의 1차원 줄이고요. NumPy 배열이든 pandas 데이터프레임이든(1권 20장) 모두 받습니다.

### 이 장에서 쓰는 데이터

예제는 scikit-learn에 들어 있는 데이터를 주로 씁니다. 따로 받을 필요가 없고, 누가 실행해도 같은 숫자가 나오니까요.

```python
import numpy as np
from sklearn.datasets import load_breast_cancer, load_diabetes

암 = load_breast_cancer()
print("유방암 진단 데이터:", 암.data.shape)
print("  특성 예:", 암.feature_names[:3].tolist())
print("  레이블 이름과 개수:", dict(zip(암.target_names.tolist(), np.bincount(암.target).tolist())))
y = 1 - 암.target                     # 0과 1을 뒤집어 1 = 악성으로
print("  뒤집은 뒤 악성(1) 개수:", y.sum())

당뇨 = load_diabetes()
print("당뇨병 진행도 데이터:", 당뇨.data.shape)
print("  특성:", list(당뇨.feature_names))
print("  목표값 범위:", 당뇨.target.min(), "~", 당뇨.target.max())
```

```text
유방암 진단 데이터: (569, 30)
  특성 예: ['mean radius', 'mean texture', 'mean perimeter']
  레이블 이름과 개수: {'malignant': 212, 'benign': 357}
  뒤집은 뒤 악성(1) 개수: 212
당뇨병 진행도 데이터: (442, 10)
  특성: ['age', 'sex', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6']
  목표값 범위: 25.0 ~ 346.0
```

- **유방암 진단 데이터**: 환자 569명의 종양 세포를 측정한 값 30개(반지름, 질감, 둘레 등)와, 그 종양이 악성(malignant)인지 양성(benign)인지가 들어 있습니다. 분류 예제에 씁니다.
- **당뇨병 진행도 데이터**: 환자 442명의 나이·성별·체질량지수(bmi)·혈압(bp)과 혈액 검사 수치 6개(s1~s6), 그리고 1년 뒤 병이 얼마나 진행됐는지를 나타내는 숫자(25~346)가 있습니다. 회귀 예제에 씁니다. 특성 값은 원래 단위가 아니라 미리 평균 0 근처로 맞춰진 상태로 들어 있어요.

유방암 데이터는 원래 악성이 0, 양성이 1로 적혀 있습니다. 그런데 이 장에서는 **찾고 싶은 쪽**, 즉 악성을 1로 두는 편이 3.7절의 평가 지표를 이해하기 훨씬 쉬워요. 그래서 `1 - 암.target`으로 0과 1을 뒤집어 씁니다. 앞으로 나오는 예제에서 `y = 1 - y`라는 줄이 보이면 "1이 악성"이라는 뜻입니다.

## 3.2 선형 회귀: 숫자를 예측하는 직선

### 집값의 숨은 공식 찾기

부동산 중개사무소 사장님이 "이 동네는 기본 1억에, 평당 1,500만 원쯤 해요"라고 말했다고 해 봅시다. 이 말을 식으로 쓰면 `가격 = 1.0 + 0.15 × 넓이`(억 원)입니다. 사장님은 수많은 거래를 지켜보면서 이 공식을 머릿속에 만들어 둔 거예요.

**선형 회귀(linear regression)** 는 이 일을 컴퓨터가 하게 합니다. 넓이와 가격 기록을 주면, 점들 사이를 가장 잘 지나가는 직선의 기울기와 절편을 찾아 줘요. 실제로 "기본 1억, 평당 0.15억"이라는 숨은 규칙에 잡음을 섞어 예제용 데이터를 만들고, 모델이 그 규칙을 찾아내는지 보겠습니다.

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# 예제용으로 만든 데이터: 집 넓이(평)와 가격(억 원)
rng = np.random.default_rng(0)
넓이 = rng.uniform(10, 40, size=50)
가격 = 1.0 + 0.15 * 넓이 + rng.normal(0, 0.3, size=50)   # 숨은 규칙 + 잡음

모델 = LinearRegression()
모델.fit(넓이.reshape(-1, 1), 가격)     # X는 언제나 (샘플 수, 특성 수) 2차원
print(f"기울기(평당 가격): {모델.coef_[0]:.3f}억 원")
print(f"절편(기본 가격):   {모델.intercept_:.3f}억 원")
print("30평, 35평 예상 가격:", 모델.predict([[30], [35]]).round(2))
```

```text
기울기(평당 가격): 0.155억 원
절편(기본 가격):   0.875억 원
30평, 35평 예상 가격: [5.53 6.31]
```

모델이 찾은 기울기는 0.155, 절편은 0.875입니다. 숨겨 둔 0.15와 1.0에 꽤 가깝죠? 잡음 때문에 정확히 같지는 않지만, 점 50개만 보고 규칙의 모양을 거의 알아냈어요. 이제 이 모델에 30평을 물으면 "기본값 + 30 × 평당 가격"을 계산해서 5.53억이라고 답합니다.

여기서 "가장 잘 지나가는 직선"의 기준은 **예측과 실제의 차이를 제곱해서 모두 더한 값이 가장 작은 직선**입니다. 이 기준을 만족하는 기울기와 절편은 공식으로 한 번에 구할 수 있어서, `LinearRegression`은 학습이 눈 깜짝할 새에 끝나요. 같은 문제를 "조금씩 고쳐 가며" 푸는 방법이 5장의 경사하강법인데, 거기서 이 직선을 PyTorch로 직접 다시 찾아봅니다.

코드에서 `넓이.reshape(-1, 1)`을 눈여겨보세요. 특성이 하나뿐이어도 `X`는 (샘플 수, 특성 수) 2차원이어야 해서 `(50,)`을 `(50, 1)`로 세웠습니다. `reshape`의 `-1`은 "나머지는 알아서 계산하라"는 뜻이에요(4장에서 텐서로 자세히 봅니다). 예측할 때도 `[[30], [35]]`처럼 2차원으로 줍니다.

### 특성이 여러 개일 때: 계수 읽기

특성이 열 개라면 직선 대신 `예측 = 절편 + 계수1 × 특성1 + … + 계수10 × 특성10` 꼴이 됩니다. 계수 하나하나가 "그 특성이 1만큼 커지면 예측이 얼마나 바뀌는가"예요. 당뇨병 데이터로 어떤 특성이 진행도와 관련이 큰지 계수를 읽어 보겠습니다.

```python
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

당뇨 = load_diabetes()
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    당뇨.data, 당뇨.target, test_size=0.25, random_state=42)

모델 = make_pipeline(StandardScaler(), LinearRegression())
모델.fit(X_학습, y_학습)

선형 = 모델[-1]                        # 파이프라인의 마지막 단계 꺼내기
계수 = sorted(zip(당뇨.feature_names, 선형.coef_), key=lambda 쌍: -abs(쌍[1]))
for 이름, 값 in 계수:
    print(f"{이름:>4}: {값:+7.1f}")
print(f"절편: {선형.intercept_:.1f}")
print(f"시험 세트 R²: {모델.score(X_시험, y_시험):.3f}")
```

```text
  s1:   -44.1
  s5:   +33.4
 bmi:   +25.1
  s2:   +24.5
  bp:   +18.2
  s4:   +13.0
 sex:   -11.5
  s3:    +5.5
 age:    +2.2
  s6:    +1.2
절편: 154.3
시험 세트 R²: 0.485
```

`make_pipeline(StandardScaler(), LinearRegression())`은 2장에서 배운 파이프라인입니다. 특성을 먼저 **표준화**(평균 0, 표준편차 1)한 뒤 선형 회귀에 넘겨요. 계수를 비교하려면 이 단계가 꼭 필요합니다. 원래 단위 그대로라면(나이는 수십, 혈액 수치는 수백) 계수 크기가 단위에 휘둘리거든요. 이 데이터는 3.1절에서 말했듯 미리 눈금을 맞춰 둔 상태라 효과가 크지 않지만, 계수를 비교할 때는 습관처럼 표준화를 넣어 두는 게 안전합니다. 모두 같은 눈금으로 맞춰 두면 "표준편차 하나만큼 커질 때의 영향"으로 공평하게 비교할 수 있습니다. `모델[-1]`은 파이프라인의 마지막 단계, 즉 선형 회귀 모델을 꺼내는 방법이에요.

계수를 크기순으로 정렬한 결과(1권 10장의 `sorted`와 `key=lambda`)를 보면 bmi가 +25.1로, 체질량지수가 높을수록 진행도가 높게 예측됩니다. 의학 상식과도 맞죠. 그런데 혈액 수치 s1과 s2를 보면 이상합니다. s1은 -44.1로 모든 계수 중 가장 크고, s2는 +24.5로 부호가 반대예요. 둘은 서로 아주 비슷하게 움직이는 수치라서, 모델이 "한쪽은 크게 더하고 다른 쪽은 크게 빼는" 식으로 균형을 맞춘 결과입니다. 이렇게 서로 비슷하게 움직이는 특성이 함께 들어 있는 상태를 **다중공선성(multicollinearity)** 이라고 합니다. 다중공선성이 있으면 계수를 곧이곧대로 해석하기 어려워져요. 5장 5.13절에서는 같은 두 특성이 경사하강법에서 어떻게 보이는지 다시 만납니다. 시험 세트 R²(3.8절)는 0.485로, 진행도 차이의 절반쯤을 설명하는 수준입니다.

### 계수에 고삐 매기: 릿지와 라소

계수가 서로 크게 밀고 당기는 상황을 막는 방법이 있습니다. 학습할 때 "예측을 잘하라"는 목표에 "**계수는 되도록 작게**"라는 벌점을 더하는 거예요. 고삐를 매어 계수가 멀리 뛰쳐나가지 못하게 하는 셈입니다. 벌점을 계수의 제곱으로 매기면 **릿지(Ridge)**, 절댓값으로 매기면 **라소(Lasso)** 라고 부릅니다.

```python
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

당뇨 = load_diabetes()
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    당뇨.data, 당뇨.target, test_size=0.25, random_state=42)

print("     " + "".join(f"{이름:>6}" for 이름 in 당뇨.feature_names) + "   시험 R²")
for 이름, 회귀 in [("선형", LinearRegression()), ("릿지", Ridge(alpha=10.0)),
                   ("라소", Lasso(alpha=1.0))]:
    모델 = make_pipeline(StandardScaler(), 회귀).fit(X_학습, y_학습)
    계수 = 모델[-1].coef_.round(1) + 0.0          # + 0.0은 -0.0을 0.0으로 정리
    print(f"{이름} " + "".join(f"{값:6.1f}" for 값 in 계수)
          + f"   {모델.score(X_시험, y_시험):.3f}")
```

```text
        age   sex   bmi    bp    s1    s2    s3    s4    s5    s6   시험 R²
선형    2.2 -11.5  25.1  18.2 -44.1  24.5   5.5  13.0  33.4   1.2   0.485
릿지    2.4 -11.0  25.1  17.6 -13.1   0.5  -7.8   8.5  21.2   1.9   0.488
라소    1.2  -9.3  25.7  17.0  -8.4   0.0 -10.8   3.3  21.1   1.1   0.496
```

`alpha`가 고삐의 세기입니다. 릿지에서는 -44.1과 +24.5로 싸우던 s1·s2가 -13.1과 0.5로 얌전해졌고, 라소는 s2의 계수를 아예 **0으로** 만들어 버렸어요. 라소는 쓸모가 적은 특성을 지워 버리는 성질이 있어서, 특성이 많을 때 "어떤 특성이 정말 필요한가"를 고르는 데도 씁니다. 그리고 계수를 눌렀는데도 시험 R²는 오히려 조금씩 올랐습니다(0.485 → 0.488 → 0.496). 차이가 작아서 한 번 나눈 결과만으로 단정할 수는 없지만(3.9절), 계수가 과하게 커지는 것이 학습 데이터의 우연한 무늬까지 외운 결과일 수 있다는 신호예요.

이 "가중치를 작게 유지하라"는 벌점은 8장에서 신경망의 **가중치 감쇠(weight decay)** 라는 이름으로 다시 만납니다. 생각은 똑같아요.

## 3.3 로지스틱 회귀: 확률로 답하는 분류

### 점수를 확률로 바꾸는 S자 곡선

이번에는 숫자가 아니라 "악성인가, 아닌가"를 맞혀야 합니다. 선형 회귀처럼 `절편 + 계수 × 특성`으로 점수를 낼 수는 있는데, 이 점수는 -100이 될 수도 1000이 될 수도 있어요. 우리가 원하는 건 "악성일 확률 87%" 같은 0과 1 사이 값입니다.

그래서 점수를 0과 1 사이로 눌러 담는 함수를 하나 끼웁니다. 아무리 세게 눌러도 일정 높이 이상 올라가지 않는 스프링 저울을 떠올려 보세요. 이 함수를 **시그모이드(sigmoid)** 라고 해요.

```python
import numpy as np


def 시그모이드(z: np.ndarray) -> np.ndarray:
    """어떤 실수든 0과 1 사이 값으로 눌러 담는다."""
    return 1 / (1 + np.exp(-z))


점수 = np.array([-6.0, -2.0, -0.5, 0.0, 0.5, 2.0, 6.0])
for z, p in zip(점수, 시그모이드(점수)):
    print(f"점수 {z:+5.1f} → 확률 {p:.3f}")
```

```text
점수  -6.0 → 확률 0.002
점수  -2.0 → 확률 0.119
점수  -0.5 → 확률 0.378
점수  +0.0 → 확률 0.500
점수  +0.5 → 확률 0.622
점수  +2.0 → 확률 0.881
점수  +6.0 → 확률 0.998
```

점수가 0이면 확률은 딱 0.5, 점수가 커질수록 1에, 작아질수록 0에 다가가지만 넘지는 않습니다. 점수 +2만 돼도 확률 0.88, +6이면 0.998이에요. **로지스틱 회귀(logistic regression)** 는 "선형 회귀로 점수를 내고, 시그모이드로 확률을 만들고, 0.5를 넘으면 1이라고 답하는" 모델입니다. 이름에 회귀가 들어 있지만 분류 모델이라는 점이 처음엔 헷갈려요.

### 유방암 진단에 써 보기

```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

암 = load_breast_cancer()
X, y = 암.data, 1 - 암.target            # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

모델 = make_pipeline(StandardScaler(), LogisticRegression())
모델.fit(X_학습, y_학습)

확률 = 모델.predict_proba(X_시험[:5])     # 열 0: 악성 아님, 열 1: 악성
print("예측 확률:\n", 확률.round(3))
print("예측 레이블:", 모델.predict(X_시험[:5]))
print("실제 레이블:", y_시험[:5])

계수 = 모델[-1].coef_[0]                  # 특성 30개에 하나씩
for i in 계수.argsort()[::-1][:3]:       # 큰 것부터 세 개
    print(f"{암.feature_names[i]:>15}: {계수[i]:+.2f}")
```

```text
예측 확률:
 [[0.001 0.999]
 [0.996 0.004]
 [0.    1.   ]
 [1.    0.   ]
 [0.965 0.035]]
예측 레이블: [1 0 1 0 0]
실제 레이블: [1 0 1 0 0]
  worst texture: +1.37
   radius error: +1.27
 worst symmetry: +1.04
```

`predict_proba`는 환자마다 두 칸짜리 확률을 돌려줍니다. 앞 칸이 0(악성 아님), 뒤 칸이 1(악성)일 확률이고 둘을 더하면 1이에요. 첫 환자는 악성일 확률이 0.999라 1로, 다섯째 환자는 0.035라 0으로 예측했고, 다섯 명 모두 실제 레이블과 맞았습니다. `predict`는 이 확률이 0.5를 넘는지만 보고 답을 고르는 거예요. 3.7절에서 이 0.5라는 **문턱**을 바꾸면 무슨 일이 생기는지 봅니다.

계수의 읽는 법은 선형 회귀와 같습니다. 양수이면 그 값이 클수록 악성 쪽으로 점수를 밀고, 음수이면 반대쪽으로 밀어요. 여기서는 worst texture(가장 거친 부위의 질감)가 +1.37로 악성 쪽으로 가장 세게 밉니다. 다만 앞의 s1·s2처럼 비슷한 특성이 많은 데이터라, 계수 하나를 "원인"으로 해석하는 데는 조심해야 합니다.

> **Q. 로지스틱 회귀가 신경망과 관계가 있나요?**
> 아주 깊은 관계가 있습니다. 로지스틱 회귀는 "입력 × 가중치 + 편향"을 계산한 뒤 시그모이드를 거치는 계산이죠. 신경망의 층 하나도 결국 "입력 @ 가중치 + 편향"이라는 같은 계산이라(4장에서 행렬 곱으로 만나요), 로지스틱 회귀는 **층이 하나뿐인 신경망**과 같습니다. 6장에서 `nn.Linear`로 이 계산을 만들고, 층을 여러 겹 쌓으면 신경망이 돼요.

## 3.4 결정 트리: 스무고개로 답 찾기

### 질문을 이어 가며 좁혀 가기

스무고개 놀이를 해 본 적 있죠? "살아 있는 건가요?" "네." "다리가 네 개인가요?" "아니요." 이렇게 예/아니요 질문을 이어 가며 답을 좁혀 갑니다. 잘하는 사람은 **한 번에 후보를 가장 많이 떨어내는 질문**부터 해요.

**결정 트리(decision tree)** 가 바로 이 놀이를 하는 모델입니다. 학습할 때 "어떤 특성을 어떤 값에서 나누면 두 무리가 가장 깔끔하게 갈리는가"를 모든 특성에 대해 따져서 가장 좋은 질문을 고르고, 나뉜 무리 안에서 또 같은 일을 반복해요. 질문을 딱 두 번만 하도록(`max_depth=2`) 묶어 두고, 어떤 질문을 골랐는지 글로 뽑아 보겠습니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

암 = load_breast_cancer()
X, y = 암.data, 1 - 암.target            # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

나무 = DecisionTreeClassifier(max_depth=2, random_state=42)
나무.fit(X_학습, y_학습)
print(export_text(나무, feature_names=암.feature_names.tolist(), show_weights=True))
print(f"질문 두 번만으로 시험 정확도 {나무.score(X_시험, y_시험):.3f}")
```

```text
|--- worst perimeter <= 112.80
|   |--- worst concave points <= 0.18
|   |   |--- weights: [257.00, 12.00] class: 0
|   |--- worst concave points >  0.18
|   |   |--- weights: [0.00, 8.00] class: 1
|--- worst perimeter >  112.80
|   |--- mean texture <= 14.95
|   |   |--- weights: [5.00, 2.00] class: 0
|   |--- mean texture >  14.95
|   |   |--- weights: [5.00, 137.00] class: 1

질문 두 번만으로 시험 정확도 0.895
```

`export_text`가 나무를 글로 그려 줬습니다. 첫 질문은 "worst perimeter(가장 큰 부위의 둘레)가 112.80 이하인가?"예요. 둘레가 작은 쪽에서는 다시 오목한 부위 수치를 묻고, 큰 쪽에서는 질감을 묻습니다. `weights: [257.00, 12.00]`은 그 잎(마지막 칸)에 도착한 학습 데이터가 0(악성 아님) 257명, 1(악성) 12명이라는 뜻이고, 그래서 그 잎의 답은 `class: 0`입니다.

결정 트리의 가장 큰 장점은 이렇게 **사람이 읽을 수 있다**는 점이에요. "둘레가 112.8보다 크고 질감 값이 14.95보다 크면 악성 가능성이 높다"는 규칙은 의사에게 그대로 설명할 수 있습니다. 질문 두 번만으로도 시험 정확도가 0.895나 나왔죠. 또 각 질문이 "이 값보다 큰가 작은가"뿐이라, 3.2절과 달리 특성을 표준화할 필요가 없습니다.

### 너무 깊은 나무는 외워 버립니다

질문을 무한정 하게 두면 어떻게 될까요? 스무고개에 질문 제한이 없으면 "혹시 철수네 집 강아지 초코인가요?"처럼 아주 구체적인 질문까지 해서 결국 맞히겠죠. 결정 트리도 깊이 제한이 없으면 학습 데이터를 **한 명도 빠짐없이** 맞힐 때까지 자랍니다. 잡음이 섞인 예제용 데이터에서 깊이를 바꿔 보겠습니다.

```python
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

# 예제용으로 만든 데이터: 잡음 섞인 두 반달 모양의 점 400개
X, y = make_moons(n_samples=400, noise=0.35, random_state=0)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.3, random_state=0)

print("깊이  잎 수  학습 정확도  시험 정확도")
for 깊이 in [1, 2, 4, 6, 8, None]:
    나무 = DecisionTreeClassifier(max_depth=깊이, random_state=0).fit(X_학습, y_학습)
    print(f"{str(깊이):>4} {나무.get_n_leaves():>5} {나무.score(X_학습, y_학습):>12.3f}"
          f" {나무.score(X_시험, y_시험):>12.3f}")
```

```text
깊이  잎 수  학습 정확도  시험 정확도
   1     2        0.800        0.800
   2     4        0.879        0.900
   4    12        0.882        0.900
   6    23        0.904        0.875
   8    32        0.950        0.875
None    51        1.000        0.867
```

`make_moons`는 두 반달이 맞물린 모양으로 점을 만드는 함수인데, `noise=0.35`로 점들을 꽤 흩뜨려서 경계가 지저분합니다. 깊이가 깊어질수록 잎이 늘고(2개 → 51개) 학습 정확도는 꾸준히 올라 제한이 없을 때(`None`) 1.000이 됩니다. 그런데 시험 정확도는 깊이 2~4에서 0.900으로 가장 높았다가 그 뒤로는 오히려 떨어져 0.867까지 내려가요. 깊은 나무가 반달의 진짜 모양이 아니라 **잡음으로 튀어나온 점 하나하나를 외우는 질문**까지 만든 결과입니다.

1장에서 본 **과적합**이 바로 이 모습이에요. 학습 점수와 시험 점수가 벌어지기 시작하면 모델이 외우고 있다는 신호입니다. 결정 트리에서는 `max_depth`(최대 깊이), `min_samples_leaf`(잎에 남아야 할 최소 샘플 수) 같은 하이퍼파라미터로 나무를 적당히 잘라 줘요. 어디서 자를지는 3.10절에서 자동으로 찾아봅니다.

## 3.5 여럿이 함께: 랜덤 포레스트와 그래디언트 부스팅

나무 한 그루는 이해하기 쉽지만 작은 변화에도 휘청입니다. 학습 데이터가 조금만 달라져도 첫 질문이 바뀌고, 그 아래가 통째로 달라지거든요. 그래서 실전에서는 나무를 **여러 그루** 모아 씁니다. 모으는 방법이 크게 두 가지예요.

### 랜덤 포레스트: 각자 풀고 다수결로

퀴즈 방송에서 "청중에게 묻기" 찬스를 쓰면 정답률이 꽤 높다고 하죠. 한 사람 한 사람은 자주 틀려도, 서로 다른 이유로 틀리기 때문에 다수결을 하면 틀린 답이 서로 상쇄되는 겁니다. 이것을 **집단 지성**이라고 해요.

**랜덤 포레스트(random forest)** 는 나무들을 일부러 서로 다르게 키웁니다. 나무마다 학습 데이터를 무작위로 다시 뽑아(같은 샘플이 여러 번 뽑히기도 합니다) 주고, 질문을 고를 때도 특성 일부만 후보로 보여 줘요. 그렇게 다르게 자란 나무 수백 그루가 투표해서 답을 정합니다. 3.4절에서 외우기만 하던 반달 데이터에 써 보겠습니다.

```python
from sklearn.datasets import make_moons
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

# 3.4절과 같은 예제용 두 반달 데이터
X, y = make_moons(n_samples=400, noise=0.35, random_state=0)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.3, random_state=0)

나무 = DecisionTreeClassifier(random_state=0).fit(X_학습, y_학습)
print(f"끝까지 자란 나무 한 그루: 시험 정확도 {나무.score(X_시험, y_시험):.3f}")
for 그루_수 in [1, 10, 50, 200]:
    숲 = RandomForestClassifier(n_estimators=그루_수, random_state=0).fit(X_학습, y_학습)
    print(f"나무 {그루_수:>3}그루짜리 숲: 학습 {숲.score(X_학습, y_학습):.3f},"
          f" 시험 {숲.score(X_시험, y_시험):.3f}")
```

```text
끝까지 자란 나무 한 그루: 시험 정확도 0.867
나무   1그루짜리 숲: 학습 0.939, 시험 0.833
나무  10그루짜리 숲: 학습 0.986, 시험 0.908
나무  50그루짜리 숲: 학습 1.000, 시험 0.900
나무 200그루짜리 숲: 학습 1.000, 시험 0.900
```

끝까지 자란 나무 한 그루는 시험 정확도 0.867이었습니다. 숲 안의 나무도 깊이 제한 없이 끝까지 자라서, 나무가 50그루 넘게 모이면 학습 정확도는 1.000이에요. 그런데도 시험 정확도는 0.900으로, 3.4절에서 깊이를 공들여 골랐을 때의 최고 점수와 같습니다. 나무 하나하나는 외우고 있지만, 각자 다른 잡음을 외웠기 때문에 투표를 하면 그 실수들이 묻히는 거예요. 1그루짜리 숲(0.833)은 데이터 일부만 보고 자란 나무 하나라서 오히려 가장 나빴고, 10그루만 모여도 크게 좋아졌습니다.

숲의 투표를 직접 들여다보고, 숲이 어떤 특성을 중요하게 여겼는지도 보겠습니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

암 = load_breast_cancer()
X, y = 암.data, 1 - 암.target            # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

숲 = RandomForestClassifier(n_estimators=200, random_state=42).fit(X_학습, y_학습)
print(f"숲의 시험 정확도: {숲.score(X_시험, y_시험):.3f}")

# 확률이 가장 애매한 시험 환자 한 명에 대한 나무들의 투표
애매도 = abs(숲.predict_proba(X_시험)[:, 1] - 0.5)
환자 = X_시험[애매도.argmin()].reshape(1, -1)
표 = sum(int(그루.predict(환자)[0]) for 그루 in 숲.estimators_)
print(f"가장 애매한 환자: 악성 {표}표, 악성 아님 {200 - 표}표")

중요도 = 숲.feature_importances_
for i in 중요도.argsort()[::-1][:4]:
    print(f"{암.feature_names[i]:>20}: {중요도[i]:.3f}")
```

```text
숲의 시험 정확도: 0.958
가장 애매한 환자: 악성 94표, 악성 아님 106표
     worst perimeter: 0.150
          worst area: 0.121
worst concave points: 0.103
 mean concave points: 0.101
```

`숲.estimators_`에는 학습된 나무 200그루가 들어 있습니다. 확률이 0.5에 가장 가까운 애매한 환자 한 명을 골라 나무마다 답을 물었더니 악성 94표, 악성 아님 106표로 팽팽했어요. 이렇게 표가 갈리는 환자는 사람이 한 번 더 살펴봐야 할 대상이라는 정보가 되기도 합니다.

`feature_importances_`는 각 특성이 나무들의 질문에서 얼마나 큰 역할을 했는지를 모두 더하면 1이 되도록 나눠 준 값입니다. 둘레, 넓이, 오목한 부위 수치가 위쪽에 있죠. 3.4절의 나무 한 그루가 첫 질문으로 고른 worst perimeter가 여기서도 1등입니다.

### 그래디언트 부스팅: 오답 노트를 이어서 고치기

시험공부를 할 때 오답 노트를 만들어 본 적 있나요? 문제집을 한 번 풀고, 틀린 문제만 모아 다시 공부하고, 그래도 틀린 걸 또 모아서 공부합니다. **부스팅(boosting)** 은 나무들을 이렇게 **차례로** 세웁니다. 랜덤 포레스트가 나무를 각자 따로 키워 투표한다면, 부스팅은 앞 나무가 틀린 만큼을 다음 나무가 고쳐요.

말로만 들으면 감이 잘 안 오니, 당뇨병 데이터로 직접 해 보겠습니다. 처음엔 모두를 평균으로 찍고, 그다음부터는 "지금까지 틀린 양(**잔차**)"을 맞히는 작은 나무를 하나씩 더해 갑니다.

```python
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
```

```text
0단계(평균으로 찍기) 평균 오차(RMSE): 77.0
1단계 뒤 평균 오차(RMSE): 68.0
2단계 뒤 평균 오차(RMSE): 62.2
3단계 뒤 평균 오차(RMSE): 58.6
4단계 뒤 평균 오차(RMSE): 56.1
5단계 뒤 평균 오차(RMSE): 54.3
```

평균으로만 찍었을 때 평균 오차는 77.0이었습니다. 질문 두 번짜리 작은 나무로 잔차를 맞혀 더하니 68.0, 또 하나를 더하니 62.2, 다섯 그루 뒤에는 54.3까지 내려가요. 나무 하나하나는 아주 약한 모델인데, 서로의 빈틈을 이어서 메우면서 점점 강해집니다.

`학습률 = 0.3`은 나무가 알려 준 고칠 양을 그대로 다 반영하지 않고 30%만 반영한다는 뜻입니다. 오답 노트를 한 번에 통째로 믿으면 그 노트의 실수까지 따라 하게 되니, 조금씩 고치고 다음 나무에게 기회를 넘기는 거예요. 이 "틀린 만큼, 조금씩 고친다"는 생각은 5장의 경사하강법과 같은 뿌리를 가지고 있습니다. 부스팅의 이름에 **그래디언트**(기울기)가 붙은 이유이기도 해요.

실전에서는 이 과정을 손으로 짜지 않고 scikit-learn의 `HistGradientBoostingClassifier`(회귀는 `HistGradientBoostingRegressor`)를 씁니다. 특성 값을 최대 255개 구간으로 묶어서(히스토그램) 질문 후보를 줄인 덕분에 큰 데이터에서도 빠른 부스팅 모델이에요.

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

부스팅 = HistGradientBoostingClassifier(random_state=42).fit(X_학습, y_학습)
print(f"그래디언트 부스팅 시험 정확도: {부스팅.score(X_시험, y_시험):.3f}")
print("실제로 만든 나무 수:", 부스팅.n_iter_)

# 값의 10%를 일부러 지워도(결측치) 그대로 학습한다
rng = np.random.default_rng(0)
X_구멍 = X_학습.copy()
X_구멍[rng.random(X_구멍.shape) < 0.1] = np.nan
print("빈칸 개수:", np.isnan(X_구멍).sum())
부스팅.fit(X_구멍, y_학습)
print(f"빈칸 있는 데이터로 배운 뒤 시험 정확도: {부스팅.score(X_시험, y_시험):.3f}")
```

```text
그래디언트 부스팅 시험 정확도: 0.965
실제로 만든 나무 수: 100
빈칸 개수: 1311
빈칸 있는 데이터로 배운 뒤 시험 정확도: 0.972
```

설정을 하나도 바꾸지 않았는데 시험 정확도 0.965가 나왔고, 나무 100그루를 차례로 세웠습니다(`max_iter`의 기본값). 아래 절반은 이 모델의 숨은 장점입니다. 학습 데이터의 10%를 일부러 지워 빈칸(`NaN`) 1,311개를 만들었는데도 오류 없이 학습했어요. 2장에서는 결측치를 채우는 단계를 파이프라인에 넣었지만, `HistGradientBoosting` 계열은 질문마다 "빈칸은 어느 쪽으로 보낼지"까지 스스로 배워서 빈칸을 그대로 받습니다. 시험 정확도가 0.972로 조금 오른 건 빈칸 때문에 좋아졌다기보다, 데이터가 조금 달라지면 결과도 이 정도는 흔들린다는 정도로 읽어 두세요. 그 흔들림을 다루는 법이 3.9절의 교차 검증입니다.

> **Q. XGBoost나 LightGBM이라는 이름도 많이 들리던데요?**
> 둘 다 그래디언트 부스팅을 아주 빠르게 구현한 별도 라이브러리입니다. 데이터 분석 대회에서 표 데이터 부문을 오랫동안 휩쓸어서 유명해졌어요. scikit-learn의 `HistGradientBoosting`은 LightGBM의 방법을 본떠 만든 것이라 생각이 같고, `fit`·`predict` 약속도 똑같이 따릅니다. 이 장에서 익힌 사용법과 하이퍼파라미터 감각은 그대로 옮겨 쓸 수 있으니, 데이터가 수백만 줄을 넘어갈 때 바꿔 보세요.

## 3.6 정답 없이 묶기: k-means 군집

### 깃발 세 개 주위로 모이기

지금까지는 정답 `y`를 주고 배우는 **지도 학습**이었습니다. 이번에는 정답이 없어요. 쇼핑몰 고객 데이터는 많은데 "이 고객은 어떤 유형"이라는 레이블은 아무도 붙여 두지 않은 상황입니다. 이럴 때 비슷한 것끼리 무리를 짓는 것이 **군집(clustering)** 이고, 가장 널리 쓰는 방법이 **k-means**입니다.

운동장에 학생들이 흩어져 있고 선생님이 깃발 세 개를 아무 데나 꽂았다고 해 봅시다.

1. 학생들은 **가장 가까운 깃발**로 모입니다.
2. 선생님은 각 무리의 **한가운데**로 깃발을 옮깁니다.
3. 깃발이 옮겨졌으니 학생들은 다시 가장 가까운 깃발을 찾아 움직입니다.

2와 3을 깃발이 더 움직이지 않을 때까지 반복하면, 서로 가까운 학생끼리 세 무리가 지어져요. 깃발의 개수가 k, 깃발 위치가 무리의 평균(mean)이라서 k-means입니다.

```python
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

# 예제용으로 만든 데이터: 정답 레이블 없이 점 300개만 있다고 하자
X, _ = make_blobs(n_samples=300, centers=3, cluster_std=1.0, random_state=7)

군집 = KMeans(n_clusters=3, n_init=10, random_state=0)
번호 = 군집.fit_predict(X)              # 배우고 곧바로 각 점의 무리 번호 받기
print("처음 10개 점의 무리 번호:", 번호[:10])
print("무리별 점 개수:", np.bincount(번호))
print("무리 중심:\n", 군집.cluster_centers_.round(2))
print("새 점 두 개의 무리:", 군집.predict([[9.0, 1.0], [-8.0, 5.0]]))
```

```text
처음 10개 점의 무리 번호: [0 2 2 0 1 2 0 1 2 0]
무리별 점 개수: [100 100 100]
무리 중심:
 [[-8.55  5.57]
 [ 9.63  0.54]
 [-1.26  4.38]]
새 점 두 개의 무리: [1 0]
```

`make_blobs`로 세 덩어리 모양의 예제용 점 300개를 만들었고, 정답 레이블(`_`)은 버리고 점의 위치만 줬습니다. k-means는 이 점들을 100개씩 세 무리로 나눴어요. `cluster_centers_`가 최종 깃발 위치이고, `predict`로 새 점을 주면 가장 가까운 깃발의 번호를 돌려줍니다. (9, 1)은 1번 무리, (-8, 5)는 0번 무리예요.

무리 번호 0, 1, 2에는 아무 의미가 없다는 점에 주의하세요. "0번이 우수 고객"처럼 정해진 게 아니라 그냥 이름표일 뿐이고, 씨앗을 바꾸면 번호가 뒤바뀔 수도 있습니다. 각 무리가 어떤 무리인지는 중심값과 소속 데이터를 보고 사람이 해석해야 해요. `n_init=10`은 깃발을 처음 꽂는 위치를 10번 바꿔 시도해서 가장 좋은 결과를 고르라는 뜻입니다. 처음 위치가 나쁘면 이상한 무리로 굳어 버릴 수 있거든요.

### 깃발은 몇 개를 꽂아야 할까요?

위에서는 덩어리가 셋인 걸 알고 `n_clusters=3`을 줬지만, 실제 데이터에서는 무리가 몇 개인지 모릅니다. k를 바꿔 가며 두 가지 점수를 보겠습니다.

```python
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score

X, _ = make_blobs(n_samples=300, centers=3, cluster_std=1.0, random_state=7)

print(" k   관성(inertia)   실루엣 점수")
for k in range(2, 7):
    군집 = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    print(f"{k:>2} {군집.inertia_:>14.1f} {silhouette_score(X, 군집.labels_):>13.3f}")
```

```text
 k   관성(inertia)   실루엣 점수
 2         3302.8         0.745
 3          573.4         0.790
 4          501.4         0.647
 5          434.8         0.471
 6          374.2         0.329
```

- **관성(inertia)**: 각 점에서 자기 깃발까지 거리의 제곱을 모두 더한 값입니다. 깃발을 많이 꽂을수록 누구나 가까운 깃발을 갖게 되니 k가 커지면 **항상** 줄어들어요. 그래서 가장 작은 값을 고르면 안 되고, **줄어드는 폭이 갑자기 완만해지는 곳**을 봅니다. 2에서 3으로 갈 때 3302.8에서 573.4로 크게 줄었다가, 그 뒤로는 조금씩만 줄죠. 그래프로 그리면 팔꿈치처럼 꺾이는 곳이라 **엘보(elbow) 방법**이라고 부릅니다.
- **실루엣 점수(silhouette score)**: 점마다 "우리 무리와는 얼마나 가깝고, 옆 무리와는 얼마나 먼가"를 -1~1 사이로 잰 값의 평균입니다. 클수록 무리가 또렷하게 갈렸다는 뜻이에요. k=3일 때 0.790으로 가장 높습니다.

두 점수 모두 k=3을 가리켰습니다. 실제 데이터에서는 이렇게 깔끔하지 않은 경우가 많아서, 점수는 참고로 삼고 "몇 무리로 나눠야 쓸모가 있는가"라는 업무 판단을 함께 해요.

### 거리를 쓰는 모델은 눈금을 맞춰야 합니다

k-means는 "가까운 깃발"을 찾으니 **거리**가 전부입니다. 그런데 특성마다 단위가 크게 다르면 어떻게 될까요? 와인 178병의 화학 성분 13가지로 무리를 지어 보고, 실제 품종(정답은 채점할 때만 씁니다)과 얼마나 맞는지 보겠습니다.

```python
from sklearn.cluster import KMeans
from sklearn.datasets import load_wine
from sklearn.metrics import adjusted_rand_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

와인 = load_wine()
X, 품종 = 와인.data, 와인.target          # 품종은 채점할 때만 쓴다
print("특성 범위 예:", 와인.feature_names[12], X[:, 12].min(), "~", X[:, 12].max(),
      "/", 와인.feature_names[7], X[:, 7].min(), "~", X[:, 7].max())

그대로 = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(X)
맞춘_뒤 = make_pipeline(StandardScaler(),
                        KMeans(n_clusters=3, n_init=10, random_state=0)).fit_predict(X)
print(f"스케일링 없이: 품종과 일치도 {adjusted_rand_score(품종, 그대로):.3f}")
print(f"스케일링 후:   품종과 일치도 {adjusted_rand_score(품종, 맞춘_뒤):.3f}")
```

```text
특성 범위 예: proline 278.0 ~ 1680.0 / nonflavanoid_phenols 0.13 ~ 0.66
스케일링 없이: 품종과 일치도 0.371
스케일링 후:   품종과 일치도 0.897
```

proline이라는 성분은 278~1680 범위인데, nonflavanoid_phenols는 0.13~0.66 범위입니다. 그대로 거리를 재면 proline의 차이가 거리를 거의 혼자 결정해 버려서, 나머지 12가지 성분은 무시되다시피 해요. 그 결과 품종과의 일치도가 0.371에 그쳤습니다. 표준화를 먼저 하니 모든 성분이 같은 눈금에서 목소리를 내게 되어 일치도가 0.897로 올랐어요.

`adjusted_rand_score`는 두 가지 묶음 방법이 얼마나 같은지를 재는 점수로, 1이면 완전히 같고 무작위로 묶으면 0 근처입니다. 무리 번호 자체는 의미가 없으니 "같은 품종끼리 같은 무리에 들어갔는가"만 봐요. 1장의 최근접 이웃도 거리를 쓰는 모델이라 같은 이유로 표준화가 중요했습니다. 반대로 결정 트리 계열은 "이 값보다 큰가"만 묻기 때문에 눈금에 영향을 받지 않아요.

## 3.7 분류 모델 평가하기: 정확도만 보면 속는 이유

### 99% 정확한 엉터리 검사기

코로나19가 유행할 때 신속 항원 검사를 많이 했죠. 어떤 검사기가 "정확도 99%"라고 광고한다면 믿고 써도 될까요? 감염자가 100명 중 1명뿐인 상황에서, **누구에게나 무조건 "음성"이라고 말하는 검사기**를 생각해 봅시다.

```python
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, recall_score

# 예제용으로 만든 데이터: 1,000명 중 10명(1%)만 감염자(1)
rng = np.random.default_rng(0)
y = np.zeros(1000, dtype=int)
y[rng.choice(1000, size=10, replace=False)] = 1
X = rng.normal(size=(1000, 3))          # 의미 없는 특성 (게으른 검사기는 보지도 않는다)

게으른_검사기 = DummyClassifier(strategy="most_frequent").fit(X, y)
예측 = 게으른_검사기.predict(X)          # 누구에게나 "음성"
print("양성 판정 수:", 예측.sum())
print(f"정확도: {accuracy_score(y, 예측):.3f}")
print(f"감염자 중 찾아낸 비율(재현율): {recall_score(y, 예측):.3f}")
```

```text
양성 판정 수: 0
정확도: 0.990
감염자 중 찾아낸 비율(재현율): 0.000
```

`DummyClassifier(strategy="most_frequent")`는 특성을 보지도 않고 학습 데이터에서 가장 흔한 답만 말하는 "게으른" 모델입니다. 양성 판정을 한 번도 하지 않았는데 정확도는 0.990이에요. 1,000명 중 990명이 원래 음성이니까요. 그런데 정작 찾아야 할 감염자 10명은 **한 명도** 찾지 못했습니다(재현율 0). 찾고 싶은 쪽이 드물 때 정확도는 이렇게 사람을 속입니다. 그래서 다른 눈금들이 필요해요. 이런 불균형 데이터를 학습 단계에서 다루는 방법은 2장에서 봤으니, 여기서는 **채점하는 법**에 집중하겠습니다.

> **Q. 이렇게 뻔한 모델을 왜 만들어 보나요?**
> 기준선이 되기 때문입니다. 실제 프로젝트에서 어떤 모델의 정확도가 0.95라고 하면 좋아 보이지만, 아무것도 안 하는 `Dummy` 모델이 0.94라면 이야기가 완전히 달라져요. 새 모델을 만들면 언제나 `DummyClassifier`(회귀는 `DummyRegressor`)의 점수부터 재 두는 습관을 들이세요. 3.13절 실습에서도 그렇게 시작합니다.

### 혼동 행렬: 네 가지 칸

검사 결과는 네 가지 중 하나입니다. 감염자에게 양성(맞음), 감염자에게 음성(놓침), 비감염자에게 양성(헛경보), 비감염자에게 음성(맞음). 이 네 칸을 세어 놓은 표가 **혼동 행렬(confusion matrix)** 이에요.

| | 예측: 음성(0) | 예측: 양성(1) |
|---|---|---|
| **실제: 음성(0)** | TN 진짜 음성 | FP 거짓 양성 (헛경보) |
| **실제: 양성(1)** | FN 거짓 음성 (놓침) | TP 진짜 양성 |

이름이 헷갈리면 뒤 글자부터 읽으세요. P/N은 모델이 **뭐라고 말했는지**(양성/음성), 앞의 T/F는 그 말이 **맞았는지**입니다. FN은 "음성이라고 말했는데(N) 틀렸다(F)", 즉 놓친 환자예요. 유방암 데이터의 로지스틱 회귀로 네 칸을 세고, 여기서 나오는 지표들을 손으로 계산해 보겠습니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (confusion_matrix, f1_score, precision_score,
                             recall_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성 (찾고 싶은 쪽 = 양성 판정)
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)
모델 = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_학습, y_학습)
예측 = 모델.predict(X_시험)

표 = confusion_matrix(y_시험, 예측)
print(표)
tn, fp, fn, tp = 표.ravel()
print(f"TN={tn}, FP={fp}, FN={fn}, TP={tp}")

정밀도 = tp / (tp + fp)
재현율 = tp / (tp + fn)
f1 = 2 * 정밀도 * 재현율 / (정밀도 + 재현율)
print(f"직접 계산: 정밀도 {정밀도:.3f}, 재현율 {재현율:.3f}, F1 {f1:.3f}")
print(f"sklearn : 정밀도 {precision_score(y_시험, 예측):.3f}, "
      f"재현율 {recall_score(y_시험, 예측):.3f}, F1 {f1_score(y_시험, 예측):.3f}")
```

```text
[[89  1]
 [ 4 49]]
TN=89, FP=1, FN=4, TP=49
직접 계산: 정밀도 0.980, 재현율 0.925, F1 0.951
sklearn : 정밀도 0.980, 재현율 0.925, F1 0.951
```

시험 환자 143명 중 악성 아님을 맞힌 TN이 89명, 악성을 맞힌 TP가 49명입니다. 틀린 건 헛경보(FP) 1명과 놓친 환자(FN) 4명이에요. 이 네 숫자에서 세 가지 지표가 나옵니다.

- **정밀도(precision)** = TP / (TP + FP): 모델이 **"양성"이라고 말한 것 중** 진짜 양성의 비율. "양성 판정을 믿어도 되는가?"에 답합니다. 50번 양성이라고 했는데 49번이 맞아서 0.980이에요.
- **재현율(recall)** = TP / (TP + FN): **진짜 양성 중** 모델이 찾아낸 비율. "환자를 빠뜨리지 않는가?"에 답합니다. 악성 53명 중 49명을 찾아 0.925예요. 앞의 게으른 검사기는 이 값이 0이었죠.
- **F1 점수** = 2 × 정밀도 × 재현율 / (정밀도 + 재현율): 두 값의 **조화 평균**입니다. 둘 중 하나라도 낮으면 F1이 크게 떨어져서, 한쪽만 좋은 모델을 걸러 냅니다. 여기서는 0.951이에요.

직접 계산한 값과 `precision_score`, `recall_score`, `f1_score`가 돌려준 값이 똑같습니다. 공식이 이게 전부라는 뜻이에요.

### 문턱을 움직이면 생기는 일

정밀도와 재현율은 시소처럼 움직입니다. 3.3절에서 로지스틱 회귀는 악성 확률이 0.5를 넘으면 양성이라고 답한다고 했죠. 이 **문턱**을 바꿔 보겠습니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)
모델 = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_학습, y_학습)
악성_확률 = 모델.predict_proba(X_시험)[:, 1]

print("문턱   FP   FN   정밀도   재현율")
for 문턱 in [0.9, 0.5, 0.2, 0.05]:
    예측 = (악성_확률 >= 문턱).astype(int)  # 문턱을 넘으면 양성 판정
    tn, fp, fn, tp = confusion_matrix(y_시험, 예측).ravel()
    print(f"{문턱:>4} {fp:>4} {fn:>4} {tp / (tp + fp):>8.3f} {tp / (tp + fn):>8.3f}")
```

```text
문턱   FP   FN   정밀도   재현율
 0.9    0   10    1.000    0.811
 0.5    1    4    0.980    0.925
 0.2    3    2    0.944    0.962
0.05   11    0    0.828    1.000
```

문턱을 0.9로 높이면 아주 확실할 때만 양성이라고 해서 헛경보는 0건, 정밀도는 1.000이 됩니다. 대신 놓친 환자가 10명으로 늘어요. 문턱을 0.05로 낮추면 조금만 의심스러워도 양성이라고 해서 악성은 한 명도 놓치지 않지만(재현율 1.000) 헛경보가 11건으로 늘어납니다.

어느 쪽이 좋은지는 **틀렸을 때의 대가**가 정합니다. 암 검진에서 환자를 놓치면(FN) 치료 시기를 잃지만, 헛경보(FP)는 정밀 검사 한 번이면 바로잡혀요. 그래서 재현율을 중시해 문턱을 낮춥니다. 반대로 스팸 필터는 중요한 메일을 스팸함에 넣는 것(FP)이 더 큰 문제라 정밀도를 중시하죠. 모델을 만든 다음 "문턱을 어디에 둘까"는 업무를 아는 사람과 함께 정해야 하는 질문입니다.

### ROC-AUC: 문턱과 상관없이 매기는 점수

문턱마다 정밀도와 재현율이 달라지니, 문턱을 정하기 전에 "모델 자체가 얼마나 잘 가려내는가"를 재고 싶을 때가 있습니다. 문턱을 1에서 0까지 내리면서 **거짓 경보율**(FP / 실제 음성 수)을 가로축, **재현율**을 세로축에 찍은 선을 **ROC 곡선**이라 하고, 그 아래 넓이를 **ROC-AUC**라고 해요.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

모델들 = {
    "아무 정보 없이 찍기": DummyClassifier(strategy="prior"),
    "질문 두 번짜리 나무": DecisionTreeClassifier(max_depth=2, random_state=42),
    "로지스틱 회귀": make_pipeline(StandardScaler(), LogisticRegression()),
}
for 이름, 모델 in 모델들.items():
    점수 = 모델.fit(X_학습, y_학습).predict_proba(X_시험)[:, 1]
    print(f"{이름}: ROC-AUC {roc_auc_score(y_시험, 점수):.3f}")

# AUC의 뜻: 악성 한 명과 악성 아닌 한 명을 뽑았을 때 악성 쪽 점수가 더 높을 확률
악성, 정상 = 점수[y_시험 == 1], 점수[y_시험 == 0]
이김 = (악성[:, None] > 정상[None, :]).mean() + 0.5 * (악성[:, None] == 정상[None, :]).mean()
print(f"짝 {len(악성) * len(정상)}개를 직접 비교한 비율: {이김:.3f}")

fpr, tpr, 문턱들 = roc_curve(y_시험, 점수)
print("FPR(거짓 경보율):", fpr.round(3).tolist())
print("TPR(재현율):     ", tpr.round(3).tolist())
```

```text
아무 정보 없이 찍기: ROC-AUC 0.500
질문 두 번짜리 나무: ROC-AUC 0.880
로지스틱 회귀: ROC-AUC 0.996
짝 4770개를 직접 비교한 비율: 0.996
FPR(거짓 경보율): [0.0, 0.0, 0.0, 0.011, 0.011, 0.044, 0.044, 0.122, 0.122, 1.0]
TPR(재현율):      [0.0, 0.019, 0.906, 0.906, 0.962, 0.962, 0.981, 0.981, 1.0, 1.0]
```

아무 정보 없이 찍는 모델은 0.500, 질문 두 번짜리 나무는 0.880, 로지스틱 회귀는 0.996입니다. 넓이는 0.5(동전 던지기)에서 1(완벽)까지예요.

ROC-AUC에는 기억하기 쉬운 뜻이 있습니다. **악성 환자 한 명과 악성 아닌 환자 한 명을 무작위로 뽑았을 때, 모델이 악성 환자에게 더 높은 점수를 줄 확률**이에요. 코드 아랫부분에서 이 뜻대로 직접 계산해 봤습니다. 악성 53명 × 악성 아님 90명 = 4,770쌍을 모두 비교해서 악성 쪽 점수가 높은 비율을 구했더니(같으면 반 개로 셉니다) `roc_auc_score`와 같은 0.996이 나왔어요. `(53, 1)`과 `(1, 90)`을 비교해 4,770칸을 한 번에 만든 것은 1장 1.5절에서 거리를 한꺼번에 잴 때 쓴 브로드캐스팅 그대로입니다.

마지막 두 줄은 `roc_curve`가 돌려준 곡선 위의 점들입니다. 거짓 경보율이 0.011일 때 재현율이 이미 0.962에 이르러요. 왼쪽 위 모서리에 바짝 붙은 곡선일수록 넓이가 커집니다. 1권 20장의 matplotlib로 `plt.plot(fpr, tpr)`을 하면 곡선을 직접 그려 볼 수 있어요.

### 한눈에 보는 성적표

지표를 하나씩 부르기 번거로우면 `classification_report`가 클래스별 성적표를 한 번에 만들어 줍니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)
모델 = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_학습, y_학습)

print(classification_report(y_시험, 모델.predict(X_시험),
                            target_names=["benign(0)", "malignant(1)"], digits=3))
```

```text
              precision    recall  f1-score   support

   benign(0)      0.957     0.989     0.973        90
malignant(1)      0.980     0.925     0.951        53

    accuracy                          0.965       143
   macro avg      0.968     0.957     0.962       143
weighted avg      0.966     0.965     0.965       143

```

malignant(1) 줄의 정밀도 0.980, 재현율 0.925, F1 0.951은 앞에서 계산한 값과 같습니다. benign(0) 줄은 "악성 아님"을 양성으로 보고 계산한 값이에요. `support`는 각 클래스의 실제 개수(90명, 53명)입니다. 아래쪽 `macro avg`는 클래스별 값을 그냥 평균한 것이고, `weighted avg`는 개수만큼 가중해서 평균한 것이에요. 클래스가 불균형할 때 작은 클래스의 성적을 놓치지 않으려면 macro 평균을 보세요. 표 이름을 영어로 단 것은 한글이 섞이면 출력 칸이 어긋나기 때문입니다.

## 3.8 회귀 모델 평가하기: MAE, RMSE, R²

숫자를 예측하는 회귀에서는 "맞았다/틀렸다"가 아니라 **얼마나 빗나갔는가**를 잽니다. 날씨 예보로 생각해 보세요. 최고 기온 25도를 예보했는데 실제가 27도면 2도 빗나간 거죠. 이 빗나간 양(**오차**)을 모아서 요약하는 방법이 세 가지 있습니다.

```python
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split

X, y = load_diabetes(return_X_y=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.25, random_state=42)
예측 = LinearRegression().fit(X_학습, y_학습).predict(X_시험)

오차 = y_시험 - 예측
mae = np.abs(오차).mean()
rmse = np.sqrt((오차 ** 2).mean())
r2 = 1 - (오차 ** 2).sum() / ((y_시험 - y_시험.mean()) ** 2).sum()
print(f"직접 계산: MAE {mae:.1f}, RMSE {rmse:.1f}, R² {r2:.3f}")
print(f"sklearn : MAE {mean_absolute_error(y_시험, 예측):.1f}, "
      f"RMSE {root_mean_squared_error(y_시험, 예측):.1f}, R² {r2_score(y_시험, 예측):.3f}")

평균_찍기 = DummyRegressor(strategy="mean").fit(X_학습, y_학습).predict(X_시험)
print(f"평균으로 찍기: MAE {mean_absolute_error(y_시험, 평균_찍기):.1f}, "
      f"RMSE {root_mean_squared_error(y_시험, 평균_찍기):.1f}, R² {r2_score(y_시험, 평균_찍기):.3f}")

# 큰 실수 하나가 섞이면?
망친_예측 = 예측.copy()
망친_예측[0] += 300
print(f"한 명을 300 틀리면: MAE {mean_absolute_error(y_시험, 망친_예측):.1f}, "
      f"RMSE {root_mean_squared_error(y_시험, 망친_예측):.1f}")
```

```text
직접 계산: MAE 41.5, RMSE 53.4, R² 0.485
sklearn : MAE 41.5, RMSE 53.4, R² 0.485
평균으로 찍기: MAE 65.5, RMSE 74.9, R² -0.014
한 명을 300 틀리면: MAE 42.8, RMSE 56.8
```

- **MAE(평균 절대 오차)**: 오차의 절댓값을 평균한 값입니다. "평균적으로 41.5만큼 빗나간다"처럼 목표값과 같은 단위로 바로 읽혀서 설명하기 가장 쉬워요.
- **RMSE(평균 제곱근 오차)**: 오차를 제곱해서 평균한 뒤 제곱근을 씌운 값입니다. 단위는 MAE와 같지만, 제곱 때문에 **큰 실수에 더 무겁게 벌점**을 줘요. 마지막 줄에서 143명 중 한 명만 300 더 틀리게 했더니 MAE는 41.5에서 42.8로 조금 늘었지만 RMSE는 53.4에서 56.8로 훨씬 크게 뛰었습니다. 큰 실수 한 번이 치명적인 일(재고 예측, 전력 수요 예측 등)이면 RMSE를 봅니다.
- **R²(결정 계수)**: "평균으로 찍는 것보다 얼마나 나은가"를 0~1 근처로 나타낸 값입니다. 1이면 완벽, 0이면 평균으로 찍는 것과 같은 수준, 음수면 평균보다도 못하다는 뜻이에요. 공식은 `1 - (모델의 오차 제곱합) / (평균으로 찍었을 때의 오차 제곱합)`으로, 코드의 `r2` 줄 그대로입니다.

평균으로 찍는 `DummyRegressor`의 R²가 0 근처(-0.014)로 나온 것을 보세요. 정확히 0이 아닌 건, 학습 세트의 평균으로 시험 세트를 찍었기 때문이에요. 선형 회귀의 R² 0.485는 "평균으로 찍었을 때의 오차 제곱합을 절반 가까이 줄였다"로 읽으면 됩니다. scikit-learn 회귀 모델의 `score`가 돌려주는 값이 바로 이 R²예요.

| 지표 | 단위 | 큰 실수에 | 이럴 때 |
|---|---|---|---|
| MAE | 목표값과 같음 | 덜 민감 | 사람에게 "평균 몇 만큼 틀린다"고 설명할 때 |
| RMSE | 목표값과 같음 | 민감 | 큰 실수를 특히 피해야 할 때, 모델끼리 비교할 때 |
| R² | 없음(1이 최고) | 민감 | 데이터가 다른 문제끼리 "얼마나 설명하나"를 비교할 때 |

## 3.9 교차 검증: 모의고사는 한 번보다 다섯 번

### 시험 세트 한 번은 운이 섞입니다

학생 실력을 모의고사 한 번으로 판단하면 어떨까요? 그날 마침 아는 문제가 많이 나왔을 수도, 컨디션이 나빴을 수도 있습니다. 모델도 마찬가지예요. 2장에서 데이터를 학습/시험으로 한 번 나눠 채점했는데, **어떻게 나뉘었느냐**에 따라 점수가 얼마나 달라지는지 보겠습니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
점수들 = []
for 씨앗 in range(10):                  # 나누는 방법만 바꿔 열 번
    X_학습, X_시험, y_학습, y_시험 = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=씨앗)
    나무 = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X_학습, y_학습)
    점수들.append(나무.score(X_시험, y_시험))
print("시험 정확도:", [round(s, 3) for s in 점수들])
print(f"가장 낮을 때 {min(점수들):.3f}, 가장 높을 때 {max(점수들):.3f}")
```

```text
시험 정확도: [0.916, 0.944, 0.93, 0.951, 0.937, 0.944, 0.951, 0.923, 0.916, 0.916]
가장 낮을 때 0.916, 가장 높을 때 0.951
```

모델도, 데이터도, 설정도 같습니다. 나누는 씨앗만 바꿨을 뿐인데 시험 정확도가 0.916에서 0.951까지 오르내려요. 두 모델의 차이가 0.02쯤이라면, 그 차이가 실력 차이인지 나누기 운인지 이 방법으로는 알 수 없습니다.

### K-겹 교차 검증

해결책은 모의고사를 여러 번 보는 겁니다. 데이터를 똑같은 크기의 묶음 K개로 나누고, 한 묶음씩 돌아가며 채점용으로 쓰는 거예요. K=5라면 이렇습니다.

- 1회차: 묶음 2~5로 배우고 묶음 1로 채점
- 2회차: 묶음 1, 3~5로 배우고 묶음 2로 채점
- …
- 5회차: 묶음 1~4로 배우고 묶음 5로 채점

모든 샘플이 정확히 한 번씩 채점에 쓰이고, 점수 다섯 개의 평균과 흩어진 정도를 함께 봅니다. 이것이 **K-겹 교차 검증(K-fold cross validation)** 이에요. `KFold`로 묶음을 직접 나눠 보겠습니다.

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import KFold
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
접기 = KFold(n_splits=5, shuffle=True, random_state=0)

점수들 = []
for 번호, (학습_칸, 검증_칸) in enumerate(접기.split(X), start=1):
    나무 = DecisionTreeClassifier(max_depth=3, random_state=0)
    나무.fit(X[학습_칸], y[학습_칸])          # 네 묶음으로 배우고
    점수 = 나무.score(X[검증_칸], y[검증_칸])  # 남은 한 묶음으로 채점
    점수들.append(점수)
    print(f"{번호}번째: 학습 {len(학습_칸)}개, 검증 {len(검증_칸)}개 → 정확도 {점수:.3f}")
print(f"평균 {np.mean(점수들):.3f} ± {np.std(점수들):.3f}")
```

```text
1번째: 학습 455개, 검증 114개 → 정확도 0.965
2번째: 학습 455개, 검증 114개 → 정확도 0.930
3번째: 학습 455개, 검증 114개 → 정확도 0.912
4번째: 학습 455개, 검증 114개 → 정확도 0.939
5번째: 학습 456개, 검증 113개 → 정확도 0.938
평균 0.937 ± 0.017
```

`접기.split(X)`는 회차마다 학습에 쓸 행 번호와 검증에 쓸 행 번호를 돌려줍니다. 569명을 다섯으로 나누니 검증 묶음이 114명 또는 113명이에요. 회차별 정확도가 0.912~0.965로 흔들리지만, 평균 0.937과 표준편차 0.017을 함께 보면 "이 모델은 대략 0.94 안팎, 위아래로 0.02쯤 흔들린다"는 훨씬 믿을 만한 그림이 나옵니다. `shuffle=True`는 나누기 전에 순서를 섞으라는 뜻인데, 왜 필요한지는 잠시 뒤에 봅니다.

### cross_val_score와 cross_validate

반복문을 매번 짤 필요는 없습니다. 함수 하나로 같은 일을 해요.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
모델 = make_pipeline(StandardScaler(), LogisticRegression())
접기 = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

점수 = cross_val_score(모델, X, y, cv=접기)               # 기본 채점: 정확도
print("정확도 5개:", 점수.round(3), f"→ 평균 {점수.mean():.3f}")

결과 = cross_validate(모델, X, y, cv=접기, return_train_score=True,
                      scoring=["accuracy", "recall", "roc_auc"])
for 지표 in ["accuracy", "recall", "roc_auc"]:
    print(f"{지표:>8}: 학습 {결과['train_' + 지표].mean():.3f}, "
          f"검증 {결과['test_' + 지표].mean():.3f} ± {결과['test_' + 지표].std():.3f}")
```

```text
정확도 5개: [0.956 0.974 0.982 1.    0.982] → 평균 0.979
accuracy: 학습 0.988, 검증 0.979 ± 0.014
  recall: 학습 0.976, 검증 0.958 ± 0.031
 roc_auc: 학습 0.998, 검증 0.995 ± 0.006
```

`cross_val_score`는 회차별 점수를 배열로 돌려줍니다. 여러 지표를 한 번에 보고 싶으면 `cross_validate`에 `scoring`으로 지표 이름 목록을 주면 돼요. `return_train_score=True`를 주면 학습 묶음의 점수도 함께 돌려주는데, 학습과 검증 점수의 차이로 과적합 정도를 볼 수 있습니다. 여기서는 정확도가 학습 0.988, 검증 0.979로 거의 붙어 있어서 로지스틱 회귀가 외우지 않고 있다는 걸 알 수 있어요. 재현율은 회차마다 ±0.031로 정확도보다 더 많이 흔들립니다. 악성 환자가 회차마다 40여 명뿐이라 한두 명만 놓쳐도 값이 크게 바뀌기 때문이에요.

여기서 꼭 짚을 점이 있습니다. 교차 검증에 `StandardScaler`만 따로 먼저 적용한 데이터를 넣지 않고, **스케일러가 들어 있는 파이프라인 통째로** 넣었어요. 그래야 회차마다 학습 묶음으로만 평균과 표준편차를 계산하고, 검증 묶음은 진짜 "처음 보는 데이터"로 남습니다. 2장에서 배운 데이터 누수를 교차 검증에서도 똑같이 막는 방법이에요.

### StratifiedKFold: 묶음마다 비율 맞추기

그럼 `shuffle=True`는 왜 줬고, `StratifiedKFold`는 무엇이 다를까요? 극단적인 예를 보겠습니다. 붓꽃(iris) 데이터는 품종 세 가지가 50송이씩 **순서대로** 정렬되어 있어요.

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier

X, y = load_iris(return_X_y=True)
print("레이블 앞부분과 뒷부분:", y[:5], y[-5:])   # 품종 순서대로 정렬되어 있다

for 이름, 접기 in [("KFold(섞지 않음)", KFold(n_splits=3)),
                   ("StratifiedKFold", StratifiedKFold(n_splits=3))]:
    print(이름)
    for _, 검증_칸 in 접기.split(X, y):
        print("  검증 묶음의 품종별 개수:", np.bincount(y[검증_칸], minlength=3))
    점수 = cross_val_score(DecisionTreeClassifier(random_state=0), X, y, cv=접기)
    print("  정확도:", 점수.round(3))
```

```text
레이블 앞부분과 뒷부분: [0 0 0 0 0] [2 2 2 2 2]
KFold(섞지 않음)
  검증 묶음의 품종별 개수: [50  0  0]
  검증 묶음의 품종별 개수: [ 0 50  0]
  검증 묶음의 품종별 개수: [ 0  0 50]
  정확도: [0. 0. 0.]
StratifiedKFold
  검증 묶음의 품종별 개수: [17 17 16]
  검증 묶음의 품종별 개수: [17 16 17]
  검증 묶음의 품종별 개수: [16 17 17]
  정확도: [0.98 0.94 0.98]
```

섞지 않은 `KFold(n_splits=3)`는 앞에서부터 50개씩 잘라서, 검증 묶음마다 한 품종만 들어갔습니다. 그러면 학습 묶음에는 그 품종이 하나도 없으니 모델은 그 품종을 배운 적이 없고, 정확도는 세 번 모두 0이에요. 시험 범위를 1단원만 공부시키고 3단원 시험을 본 꼴입니다.

`StratifiedKFold`는 묶음마다 **클래스 비율을 전체와 똑같이** 맞춰 나눕니다. 품종별로 16~17송이씩 고르게 들어갔고 정확도도 정상으로 돌아왔어요. 분류 문제에서는 `StratifiedKFold`를 기본으로 쓰세요. 특히 3.7절처럼 양성이 드문 데이터에서는 어떤 묶음에 양성이 하나도 안 들어가는 사고를 막아 줍니다. 사실 `cross_val_score(모델, X, y, cv=5)`처럼 숫자만 주면 scikit-learn은 분류 모델에 알아서 `StratifiedKFold`를 쓰지만, 섞지는 않습니다. 순서가 정렬된 데이터일 수 있으니 이 장의 예제처럼 `shuffle=True`와 `random_state`를 준 객체를 직접 넘기는 편이 안전해요. 시간 순서가 있는 데이터는 섞으면 안 된다는 점(미래로 과거를 맞히는 누수)은 2장에서 다뤘습니다.

## 3.10 하이퍼파라미터 탐색

### 손잡이 조합을 모두 돌려 보기: GridSearchCV

결정 트리의 깊이, 최근접 이웃의 이웃 수, 부스팅의 학습률처럼 사람이 정하는 설정을 **하이퍼파라미터**라고 했죠. 어떤 값이 좋은지는 데이터마다 다르니 결국 시험해 봐야 합니다. 라디오 주파수를 맞출 때 다이얼을 조금씩 돌려 가며 가장 깨끗하게 들리는 곳을 찾는 것과 같아요. 다이얼이 두 개라면 모든 조합을 바둑판(grid)처럼 다 시험해 볼 수 있습니다.

`GridSearchCV`는 후보 조합마다 교차 검증을 해서 가장 좋은 조합을 골라 줍니다. 1장에서 만난 최근접 이웃 모델의 이웃 수(`n_neighbors`)와 투표 방식(`weights`)을 탐색해 보겠습니다.

```python
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

파이프 = make_pipeline(StandardScaler(), KNeighborsClassifier())
후보 = {
    "kneighborsclassifier__n_neighbors": [1, 3, 5, 9, 15, 25],   # 단계이름__설정이름
    "kneighborsclassifier__weights": ["uniform", "distance"],
}
탐색 = GridSearchCV(파이프, 후보, scoring="f1",
                    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=0))
탐색.fit(X_학습, y_학습)                   # 6 × 2 = 12조합 × 5묶음 = 60번 학습

print("가장 좋은 조합:", 탐색.best_params_)
print(f"그 조합의 교차 검증 F1: {탐색.best_score_:.3f}")
표 = pd.DataFrame(탐색.cv_results_)[["param_kneighborsclassifier__n_neighbors",
                                     "param_kneighborsclassifier__weights",
                                     "mean_test_score", "rank_test_score"]]
표.columns = ["n_neighbors", "weights", "mean_f1", "rank"]
표 = 표.round(3)
print(표.sort_values("rank").head(4).to_string(index=False))
```

```text
가장 좋은 조합: {'kneighborsclassifier__n_neighbors': 3, 'kneighborsclassifier__weights': 'uniform'}
그 조합의 교차 검증 F1: 0.948
 n_neighbors  weights  mean_f1  rank
           3  uniform    0.948     1
           3 distance    0.948     1
           9 distance    0.943     3
           9  uniform    0.940     4
```

파이프라인 안 모델의 설정을 지정할 때는 **`단계이름__설정이름`** 처럼 밑줄 두 개로 잇습니다. `make_pipeline`은 단계 이름을 클래스 이름의 소문자로 자동으로 붙여서 `kneighborsclassifier`가 돼요. 이웃 수 6가지 × 투표 방식 2가지 = 12조합을 5겹 교차 검증으로 채점했으니 모델을 60번 학습한 셈입니다.

결과는 이웃 3명, `uniform`(모두 똑같이 한 표) 조합이 교차 검증 F1 0.948로 1등이었어요. 그런데 표를 보면 `distance`(가까운 이웃의 표를 더 무겁게)도 같은 점수로 공동 1등이고, 이웃 9명도 0.94대로 큰 차이가 없습니다. 3.9절에서 교차 검증 점수가 ±0.02쯤 흔들리는 걸 봤으니, 이 정도 차이는 사실상 비긴 거예요. 1등 조합에 너무 큰 의미를 두지 말고 "이웃 수 3~9 근처가 무난하다"는 감을 얻는 게 탐색의 진짜 수확입니다.

탐색에는 **학습 세트만** 넣었다는 점도 보세요. `GridSearchCV` 안의 교차 검증이 검증 역할을 하니, 시험 세트는 끝까지 아껴 둡니다. 탐색이 끝나면 `탐색` 객체가 자동으로 최고 조합을 학습 세트 전체에 다시 학습해 두어서(`refit=True`가 기본값), `탐색.predict()`처럼 바로 쓸 수 있어요.

### 조합이 너무 많을 때: RandomizedSearchCV

다이얼이 다섯 개이고 각각 10단계라면 조합이 10만 개입니다. 모두 돌리는 건 무리죠. 이럴 때는 다이얼 위치를 **무작위로** 몇십 번만 골라 시험하는 편이 효율적이에요. 하이퍼파라미터 중에는 결과를 크게 좌우하는 것과 별 영향이 없는 것이 섞여 있는데, 바둑판 탐색은 영향 없는 다이얼에도 똑같이 시간을 쓰지만 무작위 탐색은 중요한 다이얼의 여러 값을 골고루 시험하게 되거든요.

```python
from scipy.stats import loguniform, randint
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

분포 = {
    "learning_rate": loguniform(0.01, 0.3),   # 0.01~0.3을 자릿수 기준으로 고르게
    "max_leaf_nodes": randint(4, 32),         # 4 이상 32 미만 정수
    "min_samples_leaf": randint(5, 40),
}
탐색 = RandomizedSearchCV(HistGradientBoostingClassifier(random_state=0), 분포,
                          n_iter=15, scoring="roc_auc", random_state=0,
                          cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=0))
탐색.fit(X_학습, y_학습)                   # 15조합 × 5묶음 = 75번 학습

최고 = 탐색.best_params_
print(f"learning_rate={최고['learning_rate']:.4f}, max_leaf_nodes={최고['max_leaf_nodes']},"
      f" min_samples_leaf={최고['min_samples_leaf']}")
print(f"교차 검증 ROC-AUC: {탐색.best_score_:.4f}")
# best_estimator_는 최고 조합으로 학습 세트 전체를 다시 배운 모델
시험_점수 = roc_auc_score(y_시험, 탐색.predict_proba(X_시험)[:, 1])
print(f"시험 세트 ROC-AUC: {시험_점수:.4f}")
```

```text
learning_rate=0.2790, max_leaf_nodes=28, min_samples_leaf=34
교차 검증 ROC-AUC: 0.9891
시험 세트 ROC-AUC: 0.9960
```

후보를 목록이 아니라 **분포**로 줍니다. `randint(4, 32)`는 4 이상 32 미만 정수 중 하나를, `loguniform(0.01, 0.3)`은 0.01~0.3 사이 값을 **자릿수 기준으로 고르게** 뽑아요. 학습률처럼 0.01과 0.1의 차이가 0.1과 0.2의 차이만큼 중요한 설정은 이렇게 뽑아야 작은 값 쪽도 충분히 시험됩니다. `n_iter=15`로 15조합만 뽑았으니 학습은 75번이에요.

찾은 조합의 교차 검증 ROC-AUC는 0.9891, 시험 세트에서 마지막에 한 번 잰 값은 0.9960입니다. 3.7절의 로지스틱 회귀(0.996)와 비슷한 수준이에요. 데이터가 작고 깔끔하면 단순한 모델이 이미 충분히 좋아서, 복잡한 모델을 탐색까지 해서 써도 크게 나아지지 않을 수 있습니다. 이것도 탐색이 알려 주는 중요한 정보예요.

> **Q. 탐색이 너무 오래 걸리면 어떻게 하나요?**
> `GridSearchCV`와 `RandomizedSearchCV`에 `n_jobs=-1`을 주면 CPU 코어를 모두 써서 여러 조합을 동시에 학습합니다. 그래도 느리면 데이터 일부로 넓게 탐색해서 범위를 좁힌 뒤 전체 데이터로 좁은 범위만 다시 탐색하세요. 더 영리하게 "지금까지 결과를 보고 다음에 시험할 조합을 고르는" 방법(Optuna 같은 라이브러리)도 있는데, 18장 실험 관리에서 딥러닝 학습과 함께 다룹니다.

## 3.11 모델 저장하고 불러오기

학습한 모델을 프로그램이 끝날 때마다 버리고 다시 학습할 수는 없겠죠. 1권 17장에서 파이썬 객체를 통째로 파일에 저장하는 pickle을 배웠습니다. scikit-learn 모델도 파이썬 객체라 pickle로 저장할 수 있는데, 큰 NumPy 배열을 더 효율적으로 저장해 주는 **joblib**을 쓰는 것이 관례예요.

```python
from pathlib import Path

import joblib
import sklearn
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
모델 = make_pipeline(StandardScaler(), LogisticRegression()).fit(X, y)

폴더 = Path("models")
폴더.mkdir(exist_ok=True)
경로 = 폴더 / "cancer_lr.joblib"
joblib.dump({"model": 모델, "sklearn_version": sklearn.__version__}, 경로)
print(f"저장: {경로} ({경로.stat().st_size:,}바이트)")

꾸러미 = joblib.load(경로)                # 다른 프로그램에서 불러온다고 생각하자
불러온_모델 = 꾸러미["model"]
print("저장할 때 버전:", 꾸러미["sklearn_version"], "/ 지금 버전:", sklearn.__version__)
print("예측 비교(10명):", 모델.predict(X[::57]), 불러온_모델.predict(X[::57]))
print("확률까지 모두 같은가:", (모델.predict_proba(X) == 불러온_모델.predict_proba(X)).all())
print("단계 이름:", list(불러온_모델.named_steps))
```

```text
저장: models/cancer_lr.joblib (2,342바이트)
저장할 때 버전: 1.9.1 / 지금 버전: 1.9.1
예측 비교(10명): [1 1 0 1 0 0 0 0 0 0] [1 1 0 1 0 0 0 0 0 0]
확률까지 모두 같은가: True
단계 이름: ['standardscaler', 'logisticregression']
```

세 가지를 눈여겨보세요.

- **파이프라인 통째로 저장했습니다.** 모델만 저장하면 불러온 쪽에서 표준화를 다시 해 줘야 하는데, 학습 때의 평균과 표준편차를 모르면 할 수가 없어요. 파이프라인을 저장하면 전처리 규칙까지 함께 들어 있어서 원본 데이터를 그대로 넣으면 됩니다. 불러온 뒤에도 단계 이름이 그대로 살아 있죠.
- **저장할 때의 scikit-learn 버전을 함께 적어 뒀습니다.** joblib 파일은 저장한 버전과 다른 버전에서 불러오면 경고가 나거나 동작이 달라질 수 있어요. 서비스 서버의 버전을 학습한 환경과 맞추는 것이 원칙이고, 그러려면 어떤 버전으로 저장했는지 알아야 합니다. 이렇게 딕셔너리로 모델과 정보를 함께 묶어 두면 나중에 편해요.
- **불러온 모델의 예측이 원래와 똑같습니다.** 확률값까지 모든 환자에 대해 같아요.

그리고 1권 17장의 경고가 여기에도 그대로 적용됩니다. joblib 파일도 내부는 pickle이라 **여는 순간 그 안의 코드가 실행될 수 있어요.** 인터넷에서 받은 모르는 모델 파일은 절대 `joblib.load`하지 마세요. 다른 언어나 다른 환경과 모델을 안전하게 주고받는 방법은 19장에서 ONNX로 다루고, 저장한 모델을 웹 서비스로 내보내는 일은 20장 FastAPI 서빙에서 합니다.

## 3.12 언제 딥러닝 대신 고전 머신러닝을 쓸까?

2권의 나머지는 거의 딥러닝 이야기입니다. 그럼 이 장에서 배운 모델들은 딥러닝을 배우기 전의 연습용일까요? 그렇지 않습니다. 현업에서는 오히려 고전 머신러닝이 먼저 나오는 경우가 많아요. 판단 기준을 표로 정리해 보겠습니다.

| 따져 볼 것 | 고전 머신러닝이 유리 | 딥러닝이 유리 |
|---|---|---|
| 데이터 모양 | 표(행 = 샘플, 열 = 특성) | 사진, 소리, 글, 영상 |
| 데이터 양 | 수백~수십만 줄 | 수십만~수억 개 |
| 특성 | 사람이 의미를 아는 값(나이, 금액 등) | 픽셀, 글자처럼 하나하나는 의미가 약한 값 |
| 설명 요구 | 결정 이유를 설명해야 함(대출 심사, 의료) | 성능이 가장 중요함 |
| 자원 | CPU 한 대, 몇 초~몇 분 | GPU, 몇 시간~몇 주 |

표 데이터에서는 지금도 그래디언트 부스팅이 딥러닝과 대등하거나 더 나은 경우가 많다는 연구가 꾸준히 나옵니다. 특성 하나하나에 이미 의미가 담겨 있어서, 딥러닝이 잘하는 "의미 있는 특성을 스스로 만들어 내는 일"이 덜 필요하기 때문이에요. 반대로 사진의 픽셀 하나, 문장의 글자 하나는 그 자체로 의미가 거의 없고 주변과의 관계에서 의미가 생깁니다. 이런 데이터에서는 9장의 CNN이나 12장의 트랜스포머처럼 관계를 스스로 배우는 신경망이 압도적이에요.

그래서 실무의 순서는 대개 이렇습니다. **기준선(Dummy) → 간단한 모델(선형·로지스틱 회귀) → 트리 앙상블(랜덤 포레스트, 부스팅)** 순서로 빠르게 점수를 재 보고, 그래도 부족하고 데이터가 충분할 때 딥러닝을 시도해요. 고전 모델로 잰 점수는 딥러닝 모델이 "정말 나아졌는가"를 판단하는 기준선이 되기도 합니다. 그리고 이 장에서 배운 **평가 지표, 교차 검증, 하이퍼파라미터 탐색, 시험 세트는 마지막에 한 번**이라는 원칙은 딥러닝에서도 하나도 바뀌지 않아요. 모델만 바뀔 뿐입니다.

## 3.13 실습: 캘리포니아 집값 예측 모델 고르기

이 장의 흐름을 한 데이터셋으로 처음부터 끝까지 해 보겠습니다. 할 일은 다섯 가지예요.

1. 데이터를 받고 학습/시험 세트로 나누기
2. 후보 모델 다섯 개를 학습 세트에서 교차 검증으로 비교하기
3. 가장 좋은 모델의 하이퍼파라미터 탐색하기
4. 최종 모델을 시험 세트로 **딱 한 번** 평가하기
5. 저장하고 불러와서 써 보기

데이터는 1990년 미국 캘리포니아 인구 조사의 구역(블록 그룹) 20,640곳 자료입니다. 켈리 페이스(Pace)와 로널드 배리(Barry)가 1997년 논문에 쓰려고 정리해 StatLib 저장소에 공개한 데이터예요. scikit-learn이 제공하는 함수로 처음 한 번만 인터넷에서 받아요(1MB가 안 되는 작은 파일입니다).

### 1단계: 데이터 받고 나누기

```python
import os

from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split

# 처음 한 번은 인터넷에서 받아 data/ 폴더에 저장하고, 다음부터는 거기서 읽는다
집 = fetch_california_housing(data_home=os.environ.get("BOOK_DATA_DIR", "data"), as_frame=True)
X, y = 집.data, 집.target                 # y: 구역의 집값 중앙값(단위 10만 달러)
print(X.shape)
print(X.head(3).round(2).to_string())
print("집값 범위:", y.min(), "~", y.max(), "/ 평균", round(y.mean(), 3))

X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.2, random_state=42)
print("학습:", X_학습.shape, "시험:", X_시험.shape)
```

```text
(20640, 8)
   MedInc  HouseAge  AveRooms  AveBedrms  Population  AveOccup  Latitude  Longitude
0    8.33      41.0      6.98       1.02       322.0      2.56     37.88    -122.23
1    8.30      21.0      6.24       0.97      2401.0      2.11     37.86    -122.22
2    7.26      52.0      8.29       1.07       496.0      2.80     37.85    -122.24
집값 범위: 0.14999 ~ 5.00001 / 평균 2.069
학습: (16512, 8) 시험: (4128, 8)
```

특성 8개는 구역의 소득 중앙값(MedInc, 단위 1만 달러), 집의 나이 중앙값, 가구당 평균 방 수와 침실 수, 인구, 가구당 평균 인원, 위도와 경도입니다. 목표값은 구역의 집값 중앙값으로 단위가 10만 달러라서, 평균 2.069는 약 20만 7천 달러예요. 최댓값이 5.00001로 딱 떨어지는 건 원래 조사에서 50만 달러 이상을 모두 50만 달러로 적었기 때문입니다. 이런 "천장"은 실제 데이터에서 자주 만나는 함정이라 알아 두면 좋아요.

학습 16,512곳, 시험 4,128곳으로 나눴습니다. 시험 세트 4,128곳은 이제 4단계까지 **봉인**합니다.

### 2단계: 후보 모델 교차 검증으로 비교하기

```python
import os

from sklearn.datasets import fetch_california_housing
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = fetch_california_housing(data_home=os.environ.get("BOOK_DATA_DIR", "data"),
                                return_X_y=True, as_frame=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.2, random_state=42)

후보들 = {
    "평균 찍기": DummyRegressor(),
    "선형 회귀": make_pipeline(StandardScaler(), LinearRegression()),
    "최근접 이웃": make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=10)),
    "랜덤 포레스트": RandomForestRegressor(n_estimators=100, min_samples_leaf=2,
                                          n_jobs=-1, random_state=0),
    "부스팅": HistGradientBoostingRegressor(random_state=0),
}
접기 = KFold(n_splits=5, shuffle=True, random_state=0)
for 이름, 모델 in 후보들.items():                  # 시험 세트는 여기서 쓰지 않는다
    결과 = cross_validate(모델, X_학습, y_학습, cv=접기,
                          scoring=["neg_root_mean_squared_error", "r2"])
    rmse = -결과["test_neg_root_mean_squared_error"]
    print(f"{이름}: RMSE {rmse.mean():.3f} ± {rmse.std():.3f}, R² {결과['test_r2'].mean():.3f}")
```

```text
평균 찍기: RMSE 1.156 ± 0.024, R² -0.000
선형 회귀: RMSE 0.720 ± 0.020, R² 0.612
최근접 이웃: RMSE 0.641 ± 0.017, R² 0.692
랜덤 포레스트: RMSE 0.511 ± 0.013, R² 0.805
부스팅: RMSE 0.471 ± 0.010, R² 0.834
```

`cross_validate`의 `scoring`에 `"neg_root_mean_squared_error"`라는 긴 이름을 줬습니다. scikit-learn은 "점수는 클수록 좋다"는 규칙을 모든 지표에 맞추려고, 작을수록 좋은 오차 지표에는 마이너스를 붙여(neg) 돌려줘요. 그래서 결과에 다시 마이너스를 붙여 RMSE로 읽었습니다.

기준선인 평균 찍기의 RMSE는 1.156(약 11만 6천 달러), R²는 정확히 0입니다(-0.000은 아주 작은 음수가 반올림된 표시예요). 선형 회귀가 0.720으로 크게 줄였고, 최근접 이웃이 0.641, 랜덤 포레스트가 0.511, 부스팅이 0.471로 가장 좋았어요. 회차별 흔들림(±0.010~0.024)보다 모델 사이의 차이가 훨씬 크니 이 순위는 믿을 만합니다. 위도·경도와 집값의 관계처럼 직선으로 나타낼 수 없는 패턴을 트리 계열이 잘 잡아낸 결과예요.

### 3단계: 부스팅의 하이퍼파라미터 탐색하기

1등인 부스팅을 기본 설정에서 더 다듬어 보겠습니다. 8조합 × 5겹이라 모델을 40번 학습하므로, 이 책의 실행 환경에서 2분 남짓 걸렸어요.

```python
import os

from scipy.stats import loguniform, randint
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold, RandomizedSearchCV, train_test_split

X, y = fetch_california_housing(data_home=os.environ.get("BOOK_DATA_DIR", "data"),
                                return_X_y=True, as_frame=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.2, random_state=42)

분포 = {
    "learning_rate": loguniform(0.03, 0.3),
    "max_iter": randint(100, 500),           # 나무 수
    "max_leaf_nodes": randint(15, 63),
    "min_samples_leaf": randint(10, 60),
    "l2_regularization": loguniform(1e-3, 10),
}
탐색 = RandomizedSearchCV(HistGradientBoostingRegressor(random_state=0), 분포, n_iter=8,
                          scoring="neg_root_mean_squared_error", random_state=0,
                          cv=KFold(n_splits=5, shuffle=True, random_state=0))
탐색.fit(X_학습, y_학습)

for 이름, 값 in sorted(탐색.best_params_.items()):
    print(f"{이름}: {round(값, 4)}")
print(f"교차 검증 RMSE: {-탐색.best_score_:.3f}  (기본 설정은 0.471)")
```

```text
l2_regularization: 0.0027
learning_rate: 0.0893
max_iter: 470
max_leaf_nodes: 43
min_samples_leaf: 44
교차 검증 RMSE: 0.457  (기본 설정은 0.471)
```

무작위로 고른 8조합 중에서는 학습률 0.0893, 나무 470그루, 잎 43개짜리 조합이 뽑혔고, 교차 검증 RMSE가 기본 설정의 0.471에서 0.457로 줄었습니다. 3% 남짓 나아진 셈이에요. 2단계에서 모델을 바꿨을 때(선형 회귀 0.720 → 부스팅 0.471)와 비교하면 작은 차이죠. 성능의 대부분은 **어떤 모델을 고르느냐**에서 나오고, 하이퍼파라미터 탐색은 마지막에 조금 더 짜내는 단계라고 생각하면 됩니다. 기본값(학습률 0.1, 나무 100그루)보다 학습률은 조금 낮추고 나무는 훨씬 많이 세운 조합이 뽑혔는데, "조금씩 고치되 더 여러 번" 고치는 쪽이 낫다는 3.5절의 이야기와도 맞아요. 다만 넓은 범위에서 8조합만 뽑아 본 것이라, 시간이 넉넉하면 `n_iter`를 늘려 보세요.

### 4단계: 시험 세트로 딱 한 번 평가하고 저장하기

이제 봉인을 풉니다. 3단계에서 찾은 설정을 그대로 적어 최종 모델을 만들고, **학습 세트 전체**로 학습한 뒤 시험 세트로 한 번만 채점해요. 이 블록은 앞 블록과 따로 실행할 수 있도록 탐색 결과를 숫자로 옮겨 적었습니다.

```python
import os
from pathlib import Path

import joblib
import sklearn
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split

X, y = fetch_california_housing(data_home=os.environ.get("BOOK_DATA_DIR", "data"),
                                return_X_y=True, as_frame=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.2, random_state=42)

# 3단계에서 찾은 설정을 옮겨 적는다
최종 = HistGradientBoostingRegressor(
    learning_rate=0.0893, max_iter=470, max_leaf_nodes=43,
    min_samples_leaf=44, l2_regularization=0.0027, random_state=0)
최종.fit(X_학습, y_학습)                  # 학습 세트 전체로 학습

예측 = 최종.predict(X_시험)               # 봉인했던 시험 세트, 딱 한 번
print(f"시험 RMSE {root_mean_squared_error(y_시험, 예측):.3f}, "
      f"MAE {mean_absolute_error(y_시험, 예측):.3f}, R² {r2_score(y_시험, 예측):.3f}")

경로 = Path("models") / "california_hgb.joblib"
경로.parent.mkdir(exist_ok=True)
joblib.dump({"model": 최종, "sklearn_version": sklearn.__version__,
             "features": list(X.columns)}, 경로)

꾸러미 = joblib.load(경로)
새_구역 = X_시험.head(3)
for 예상, 실제 in zip(꾸러미["model"].predict(새_구역), y_시험.head(3)):
    print(f"예상 {예상 * 10:5.2f}만 달러 / 실제 {실제 * 10:5.2f}만 달러")
```

```text
시험 RMSE 0.450, MAE 0.296, R² 0.845
예상  5.40만 달러 / 실제  4.77만 달러
예상 10.59만 달러 / 실제  4.58만 달러
예상 50.79만 달러 / 실제 50.00만 달러
```

봉인했던 시험 세트에서 RMSE 0.450, MAE 0.296, R² 0.845가 나왔습니다. 교차 검증에서 본 0.457과 거의 같으니, 교차 검증으로 짐작한 실력이 처음 보는 데이터에서도 그대로 나온 거예요. MAE 0.296은 구역마다 집값 중앙값을 평균 3만 달러쯤 빗나간다는 뜻입니다.

불러온 모델로 시험 구역 세 곳을 예측해 보면 첫째 구역은 5.40만 달러 대 실제 4.77만 달러로 가깝지만, 둘째 구역은 10.59만 달러로 실제(4.58만 달러)의 두 배 넘게 빗나갔어요. 평균 성적이 좋아도 하나하나의 예측은 크게 틀릴 수 있다는 것, 그래서 큰 실수를 드러내는 RMSE를 MAE와 함께 봐야 한다는 것을 보여 줍니다. 셋째 구역은 실제 값이 50.00만 달러로, 1단계에서 본 "천장"에 걸린 구역이에요. 진짜 집값은 이보다 높을 수도 있습니다.

### 왜 시험 세트는 한 번만 쓸까요?

실습에서 가장 중요한 규칙을 다시 짚겠습니다. 만약 시험 점수를 보고 "조금 아쉬운데 학습률을 바꿔서 다시 재 볼까?"를 반복하면 어떻게 될까요? 그 순간 시험 세트는 더 이상 처음 보는 문제가 아니라 **답을 맞춰 가며 고친 문제**가 됩니다. 기출문제를 외워서 받은 점수로 실력을 판단하는 것과 같아요. 그렇게 얻은 시험 점수는 실제 서비스에서 만날 새 데이터에서의 성능보다 좋게 나오기 마련입니다.

그래서 모델 고르기와 설정 고르기는 모두 학습 세트 안의 교차 검증으로 하고, 시험 세트는 "이 모델을 내보내도 되는가"를 마지막으로 확인하는 데 **한 번만** 씁니다. 시험 점수가 기대보다 나쁘게 나왔다면, 그 사실을 기록하고 원인을 따져 보되 같은 시험 세트로 다시 고르지는 않아요. 딥러닝에서도 학습/검증/시험 세트의 역할은 정확히 이대로입니다(6장, 8장).

## 3.14 정리와 다음 장 미리보기

이 장에서 scikit-learn으로 고전 머신러닝의 대표 모델과 평가 방법을 익혔습니다.

- **약속**: `fit`으로 배우고 `predict`·`predict_proba`로 예측하고 `score`로 채점. 끝에 밑줄이 붙은 속성(`coef_`, `feature_importances_`)은 배운 결과
- **선형 모델**: 선형 회귀는 계수와 절편을 배우고, 릿지·라소는 계수에 벌점을 줘 고삐를 맴. 로지스틱 회귀는 점수를 시그모이드로 확률로 바꾸는 분류 모델
- **트리 모델**: 결정 트리는 스무고개(깊으면 외움), 랜덤 포레스트는 서로 다른 나무들의 다수결, 그래디언트 부스팅은 앞 나무의 잔차를 조금씩 고쳐 가는 오답 노트
- **군집**: k-means는 깃발 옮기기를 반복. k는 관성의 엘보와 실루엣 점수로 고르고, 거리를 쓰니 표준화가 필수
- **분류 지표**: 드문 양성 앞에서 정확도는 속인다. 혼동 행렬의 네 칸에서 정밀도·재현율·F1, 문턱에 따라 움직이는 시소, 문턱과 상관없는 ROC-AUC
- **회귀 지표**: MAE는 설명하기 쉽고, RMSE는 큰 실수에 민감하고, R²는 평균으로 찍기 대비 얼마나 나은지
- **교차 검증과 탐색**: 분류는 섞은 `StratifiedKFold`, 전처리는 파이프라인째로, `GridSearchCV`·`RandomizedSearchCV`는 학습 세트에서만, 시험 세트는 마지막에 한 번
- **저장**: 파이프라인 통째로 `joblib.dump`, 버전을 함께 기록, 모르는 파일은 열지 않기

이것으로 1부 "머신러닝의 감각"을 마칩니다. 다음 4장부터는 PyTorch로 넘어가 딥러닝의 바탕을 쌓아요. 먼저 숫자를 담는 그릇인 **텐서**를 손에 익히고, 5장에서는 이 장의 선형 회귀를 경사하강법으로 직접 풀면서 "틀린 만큼 조금씩 고친다"는 그래디언트 부스팅의 생각이 신경망 학습에서 어떻게 쓰이는지 보게 됩니다.
