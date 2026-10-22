# Chapter 7: 딕셔너리와 집합

> **학습 목표**  
> - 딕셔너리의 키-값 쌍 구조와 활용법 이해
> - 딕셔너리 메서드와 컴프리헨션 습득
> - 집합의 특징과 집합 연산 활용
> - 해시 테이블 기반 자료구조의 성능 이해
> - 한국어 텍스트 분석 시스템 구현
> - 실무 데이터 처리 패턴 학습

---

## 들어가며: 번호 말고 이름으로 찾고 싶어요

6장의 리스트는 "몇 번째"라는 번호로 값을 꺼냈습니다. 그런데 우리가 실생활에서 무언가를 찾을 때 번호로 찾던가요? 국어사전에서 "사과"의 뜻을 찾을 때 "3,812번째 단어"를 떠올리지 않습니다. "사과"라는 **단어 자체**로 찾죠. 휴대폰 연락처도 "엄마"라는 이름으로 전화번호를 찾습니다.

이렇게 **이름표(키)로 값을 찾는** 자료형이 **딕셔너리(dictionary)** 입니다. 이름 그대로 사전이에요. 표제어(키)를 알면 뜻(값)이 바로 나옵니다. 그리고 딕셔너리에서 값은 빼고 이름표만 모아 둔 것이 **집합(set)** 입니다. 집합은 수학 시간에 배운 그 집합처럼 같은 것을 두 번 담지 않아요.

둘에게는 공통된 비밀이 하나 있습니다. 리스트처럼 처음부터 하나씩 훑지 않고, 이름표를 보고 **어디에 있는지 바로 계산해서** 찾아갑니다. 그래서 데이터가 아무리 많아도 찾는 속도가 거의 그대로예요. 이 비밀(해시)은 7.6절에서 풀어 봅니다.

## 7.1 딕셔너리 기본 개념

### 딕셔너리란 무엇인가?

딕셔너리는 키(key)와 값(value)의 쌍으로 데이터를 저장하는 가변 자료구조입니다. 중괄호 안에 `키: 값`을 쉼표로 구분해 적어요. 키는 한 딕셔너리 안에서 **하나뿐**이어야 하고, 같은 키로 다시 넣으면 새 값이 이전 값을 덮어씁니다. 값은 무엇이든 될 수 있고 중복되어도 괜찮아요.

키에는 조건이 하나 있습니다. **바뀌지 않는(불변) 값**이어야 해요. 그래서 예제처럼 문자열, 숫자, 튜플, 불리언은 키가 될 수 있지만, 리스트는 키가 될 수 없습니다. `{[1, 2]: "값"}`이라고 쓰면 `TypeError: unhashable type: 'list'`가 나요. 사물함 이름표가 수시로 바뀐다면 내 물건을 찾을 수 없겠죠? 이 이유도 7.6절에서 자세히 봅니다.

```python
# 기본 딕셔너리 생성
student = {
    "이름": "김철수",
    "나이": 20,
    "전공": "컴퓨터과학과",
    "학점": 3.8
}

# 다양한 키 타입 사용
mixed_dict = {
    "문자열키": "값1",
    42: "숫자키",
    (1, 2): "튜플키",
    True: "불린키"
}

# 빈 딕셔너리 생성
empty_dict1 = {}
empty_dict2 = dict()

print(f"학생 정보: {student}")
print(f"혼합 딕셔너리: {mixed_dict}")
```

> **Q. 키 `1`과 키 `True`를 함께 넣으면 어떻게 되나요?**
> 하나로 합쳐집니다. `{1: "a", True: "b"}`를 출력하면 `{1: 'b'}`만 남아요. 파이썬에서 `True == 1`이 참이라서, 딕셔너리는 둘을 **같은 키**로 봅니다. 그래서 `True`로 넣은 값이 `1`의 값을 덮어쓰고, 키 모양은 처음 들어간 `1`이 유지돼요. 집합도 같아서 `{1, True, "K", (2, 3)}`은 원소가 세 개입니다. 예제의 `mixed_dict`에는 `1`이 없어서 `True` 키가 따로 살아 있는 거예요. 숫자와 불리언을 키로 섞어 쓰는 일은 피하는 게 좋습니다.

### 딕셔너리 접근과 수정

값을 꺼내는 방법은 두 가지입니다.

- `딕셔너리[키]`: 키가 있으면 값을, **없으면 `KeyError`** 를 냅니다.
- `딕셔너리.get(키, 기본값)`: 키가 있으면 값을, 없으면 기본값을 돌려줍니다. 기본값을 안 주면 `None`이에요. 오류가 나지 않으니 "있을 수도, 없을 수도 있는" 키에 씁니다.

넣고 고치는 방법은 하나로 같습니다. `딕셔너리[키] = 값`이라고 쓰면 키가 있으면 값을 바꾸고, 없으면 새로 추가해요. 여러 개를 한꺼번에 넣거나 고칠 때는 `update()`를 씁니다.

```python
# 한국 지역별 인구 데이터
population = {
    "서울": 9720846,
    "부산": 3448737,
    "대구": 2438031,
    "인천": 2963991,
    "광주": 1441970,
    "대전": 1475221,
    "울산": 1124459
}

# 값 접근
print(f"서울 인구: {population['서울']:,}명")
print(f"부산 인구: {population.get('부산'):,}명")

# 안전한 접근 (기본값 사용)
print(f"세종 인구: {population.get('세종', '정보 없음')}")

# 값 수정
population["서울"] = 9700000
print(f"수정된 서울 인구: {population['서울']:,}명")

# 새 항목 추가
population["세종"] = 373096
print(f"세종 추가 후: {len(population)}개 도시")

# 여러 값 동시 업데이트
population.update({"제주": 672948, "강원": 1540681})
print(f"업데이트 후: {len(population)}개 지역")
```

처음 일곱 도시에 세종이 더해져 8개, `update()`로 제주와 강원이 더해져 10개가 됩니다. `update()`에 이미 있는 키가 들어 있었다면 추가가 아니라 값을 덮어썼을 거예요.

두 딕셔너리를 겹쳐 **새 딕셔너리**를 만들고 싶다면 파이썬 3.9부터 생긴 `|` 연산자를 쓸 수 있습니다. `{"one": 1} | {"one": "일", "two": 2}`는 `{'one': '일', 'two': 2}`예요. 겹치는 키는 **오른쪽** 값이 이깁니다. `update()`가 원본을 고치는 것과 달리 `|`는 원본 둘을 그대로 두고 새것을 만들어요. 6장에서 본 `append`와 `+`의 관계와 같습니다.

## 7.2 딕셔너리 메서드

### 키, 값, 항목 접근

딕셔너리 전체를 훑어볼 때는 세 가지 창문을 씁니다. `keys()`는 키들, `values()`는 값들, `items()`는 `(키, 값)` 쌍들을 보여 줘요. 5장에서 본 것처럼 `for`로 딕셔너리를 그냥 돌면 키가 나오고, 키와 값을 함께 쓰려면 `items()`를 돕니다.

이 세 가지가 돌려주는 것은 리스트가 아니라 **뷰(view)** 라는 읽기 전용 창문입니다. 원본 딕셔너리를 들여다보는 창이라 원본이 바뀌면 뷰에도 그대로 보여요. 리스트처럼 인덱스로 꺼내거나 저장해 두고 쓰려면 예제처럼 `list()`로 바꿉니다.

딕셔너리는 넣은 **순서를 기억합니다.** 파이썬 3.7부터 언어 규칙으로 정해진 것이라, 예제의 출력도 넣은 순서 그대로 나와요. 오래된 자료에는 "딕셔너리는 순서가 없다"고 적힌 경우가 있는데, 지금 파이썬에서는 맞지 않습니다.

```python
# 한국 전통 음식과 지역
korean_foods = {
    "김치찌개": "전국",
    "불고기": "서울/경기",
    "냉면": "평양/함흥",
    "갈비탕": "서울",
    "해물탕": "부산",
    "막국수": "강원도",
    "순두부찌개": "강원도"
}

# keys(): 모든 키 조회
food_names = list(korean_foods.keys())
print(f"음식 이름들: {food_names}")

# values(): 모든 값 조회  
regions = list(korean_foods.values())
print(f"지역들: {regions}")

# items(): 키-값 쌍 조회
print("음식별 지역:")
for food, region in korean_foods.items():
    print(f"  {food}: {region}")

# 특정 지역 음식 찾기
gangwon_foods = [food for food, region in korean_foods.items() 
                 if "강원도" in region]
print(f"강원도 음식: {gangwon_foods}")
```

### 딕셔너리 수정 메서드

예제는 학생 이름을 키로, 과목별 점수 딕셔너리를 값으로 담았습니다. 딕셔너리 안에 딕셔너리가 들어 있는 모양이에요. 지우고 고치는 메서드를 하나씩 봅시다.

- `pop(키)`: 그 키의 항목을 지우고 **값을 돌려줍니다.** 키를 꼭 알려 줘야 해요.
- `popitem()`: **마지막으로 넣은** 항목을 지우고 `(키, 값)` 튜플로 돌려줍니다. 6장의 리스트 `pop()`처럼 맨 끝에서 하나씩 빼 주는 셈이에요.
- `setdefault(키, 기본값)`: 키가 있으면 아무것도 바꾸지 않고 그 값을 돌려주고, **없을 때만** 기본값을 넣은 뒤 그 값을 돌려줍니다.
- `del 딕셔너리[키]`: 항목을 지우기만 합니다. `clear()`는 전부 지워요.

```python
# 학생 성적 관리
grades = {
    "김철수": {"국어": 85, "영어": 92, "수학": 78},
    "이영희": {"국어": 95, "영어": 87, "수학": 91},
    "박민수": {"국어": 78, "영어": 82, "수학": 95}
}

# pop(): 항목 제거 후 반환
removed_student = grades.pop("박민수")
print(f"제거된 학생: {removed_student}")

# popitem(): 마지막 항목 제거 (Python 3.7+에서 순서 보장)
last_student = grades.popitem()
print(f"마지막 학생: {last_student}")

# 다시 추가
grades["박민수"] = {"국어": 88, "영어": 85, "수학": 92}
grades["최지영"] = {"국어": 90, "영어": 88, "수학": 89}

# setdefault(): 키가 없을 때만 추가
grades.setdefault("정수진", {"국어": 0, "영어": 0, "수학": 0})
print(f"새 학생 추가: {'정수진' in grades}")

# clear(): 모든 항목 제거
test_dict = grades.copy()
test_dict.clear()
print(f"clear 후 크기: {len(test_dict)}")

# del 문으로 특정 키 제거
del grades["정수진"]
print(f"정수진 제거 후: {list(grades.keys())}")
```

`박민수`를 `pop()`으로 뺀 뒤 `popitem()`을 하면 남은 김철수와 이영희 중 나중에 넣은 `이영희`가 빠집니다. 오래된 자료에는 `popitem()`이 "무작위 항목"을 꺼낸다고 적혀 있기도 한데, 파이썬 3.7부터는 항상 마지막 항목을 꺼내요. 그래서 마지막 출력에는 김철수, 박민수, 최지영만 남습니다.

딕셔너리의 값에는 함수도 넣을 수 있습니다. 4장에서 `if-elif`를 딕셔너리로 바꿨던 것을 기억하나요? 값 대신 할 일(함수)을 넣으면 명령 이름에 따라 다른 동작을 고르는 **분기**를 딕셔너리로 할 수 있어요.

```python
def 인사():
    return "안녕하세요"

def 작별():
    return "안녕히 가세요"

명령들 = {"인사": 인사, "작별": 작별}
print(명령들["인사"]())                                  # 안녕하세요
print(명령들.get("춤", lambda: "모르는 명령입니다")())   # 모르는 명령입니다
```

`명령들["인사"]`는 함수 자체이고, 뒤에 `()`를 붙여야 실행됩니다. 없는 명령은 `get()`의 기본값으로 "모르는 명령" 함수를 돌려주니 `case _:`나 `else`의 역할까지 해요. 명령이 수십 개로 늘어나도 `if-elif`를 길게 늘이지 않고 딕셔너리에 한 줄씩만 더하면 됩니다.

## 7.3 딕셔너리 컴프리헨션

### 기본 딕셔너리 컴프리헨션

5장에서 맛본 딕셔너리 컴프리헨션 `{키: 값 for … in …}`을 조금 더 써 봅시다. `enumerate()`와 함께 쓰면 "원소 → 순서 번호" 딕셔너리를 바로 만들 수 있고, 뒤에 `if`를 붙이면 조건에 맞는 것만 남깁니다.

문자 빈도 예제의 `for char in set(text)`도 눈여겨보세요. `set()`으로 중복 글자를 먼저 없앤 뒤, 글자마다 `text.count(char)`로 개수를 셉니다. 집합을 거쳤으니 결과의 순서는 실행할 때마다 달라질 수 있어요. 또 이 방법은 글자 종류마다 문장 전체를 처음부터 다시 훑으니, 긴 글에서는 7.7절의 `Counter`가 훨씬 효율적입니다.

```python
# 숫자와 제곱의 딕셔너리
squares = {x: x**2 for x in range(1, 11)}
print(f"제곱수 딕셔너리: {squares}")

# 한글 자음과 순서
consonants = ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
consonant_order = {char: idx + 1 for idx, char in enumerate(consonants)}
print(f"자음 순서: {consonant_order}")

# 문자열에서 문자 빈도 계산
text = "안녕하세요 파이썬 프로그래밍"
char_frequency = {char: text.count(char) for char in set(text) if char != ' '}
print(f"문자 빈도: {char_frequency}")

# 조건부 딕셔너리 컴프리헨션
korean_numbers = ["하나", "둘", "셋", "넷", "다섯", "여섯", "일곱", "여덟", "아홉", "열"]
long_numbers = {num: len(num) for num in korean_numbers if len(num) >= 2}
print(f"2글자 이상 숫자: {long_numbers}")
```

### 중첩 딕셔너리 컴프리헨션

컴프리헨션 안에 컴프리헨션을 넣으면 "딕셔너리 안의 딕셔너리"를 한 번에 만들 수 있습니다. 구구단 예제의 `multiplication_table[3]`은 3단 딕셔너리이고, `multiplication_table[3][7]`이라고 쓰면 21이 나와요. 데이터를 채우기 전에 **빈 틀부터 만들어 둘 때**도 이 방법을 많이 씁니다.

```python
# 구구단 딕셔너리
multiplication_table = {
    i: {j: i * j for j in range(1, 10)} 
    for i in range(2, 10)
}
print(f"3단: {multiplication_table[3]}")

# 학급별 학생 성적 구조
classes = ["A반", "B반", "C반"]
subjects = ["국어", "영어", "수학"]
class_structure = {
    cls: {subject: [] for subject in subjects}
    for cls in classes
}
print(f"A반 구조: {class_structure['A반']}")

# 지역별 날씨 데이터 구조
regions = ["서울", "부산", "대구"]
weather_data = {
    region: {
        "온도": None,
        "습도": None, 
        "날씨": None
    } for region in regions
}
print(f"부산 날씨 구조: {weather_data['부산']}")
```

`class_structure`에서 과목마다 `[]`가 컴프리헨션 안에 있다는 점이 중요합니다. 반복할 때마다 **새 빈 리스트**가 만들어지니 A반 국어 리스트에 점수를 넣어도 다른 칸은 그대로예요. 비슷해 보이는 `dict.fromkeys(["국어", "영어"], [])`는 리스트 **하나**를 모든 키가 함께 가리키게 만듭니다. 그래서 `["국어"]`에 90을 넣으면 `{'국어': [90], '영어': [90]}`처럼 영어에도 들어가 버려요. 6장의 "`b = a`는 복사가 아니다"와 같은 함정입니다.

## 7.4 집합(Set) 기본 개념

### 집합의 특징과 생성

집합은 중복을 허용하지 않는 순서 없는 자료구조입니다. 딕셔너리에서 값은 빼고 **키만 모아 둔 것**이라고 생각하면 쉬워요. 그래서 딕셔너리 키의 성질을 그대로 물려받습니다.

- 같은 원소는 하나만 남습니다. 그래서 리스트를 `set()`에 넣으면 중복이 사라져요.
- 원소는 불변 값이어야 합니다. 숫자, 문자열, 튜플은 되지만 리스트는 안 됩니다.
- 순서가 없습니다. 출력 순서는 정해져 있지 않고, 문자열 원소는 실행할 때마다 순서가 달라질 수도 있어요. 인덱스(`[0]`)로 꺼낼 수도 없습니다.

집합이 가장 잘하는 일은 두 가지예요. **"몇 종류가 있지?"** (중복 없이 세기)와 **"이게 들어 있나?"** (빠른 `in` 검사)입니다. `frozenset`은 내용을 바꿀 수 없는 집합으로, 불변이라서 딕셔너리의 키나 다른 집합의 원소가 될 수 있습니다.

```python
# 기본 집합 생성
fruits = {"사과", "바나나", "오렌지", "포도"}
numbers = {1, 2, 3, 4, 5}

# 리스트에서 집합 생성 (중복 제거)
duplicated_list = [1, 2, 2, 3, 3, 3, 4, 4, 5]
unique_numbers = set(duplicated_list)
print(f"중복 제거: {unique_numbers}")

# 문자열에서 집합 생성
text = "안녕하세요"
unique_chars = set(text)
print(f"고유 문자: {unique_chars}")

# 빈 집합 생성 (주의: {}는 딕셔너리!)
empty_set = set()
print(f"빈 집합: {empty_set}")

# frozenset (불변 집합)
immutable_set = frozenset([1, 2, 3, 4, 5])
print(f"불변 집합: {immutable_set}")
```

> **Q. 빈 집합을 만들려고 `{}`를 썼는데 `type()`을 찍어 보니 딕셔너리래요.**
> 맞습니다. 중괄호는 딕셔너리가 먼저 차지했기 때문에 `{}`는 빈 **딕셔너리**예요. 빈 집합은 반드시 `set()`으로 만들어야 합니다. 원소가 하나라도 있으면 `{1, 2}`처럼 중괄호로 집합을 만들 수 있고, `{1: 2}`처럼 콜론이 있으면 딕셔너리가 됩니다.

### 집합 메서드

집합은 가변 자료형이라 원소를 넣고 뺄 수 있습니다. 하나는 `add()`, 여러 개는 `update()`로 넣어요. 이미 있는 원소를 `add()`하면 아무 일도 일어나지 않습니다.

빼는 방법은 세 가지입니다. `remove(x)`는 `x`가 없으면 `KeyError`를 내고, `discard(x)`는 없어도 조용히 넘어갑니다. "반드시 있어야 하는데 없으면 문제"인 상황에는 `remove`, "있으면 지우고 없으면 말고"에는 `discard`를 쓰세요. `pop()`은 아무 원소나 하나 꺼내 돌려주는데, 순서가 없는 집합이라 **무엇이 나올지 정해져 있지 않습니다.** 예제에서 제거된 도시는 실행할 때마다 다를 수 있어요.

```python
# 한국 도시 집합
seoul_metro = {"서울", "인천", "수원", "성남", "고양", "안양"}
busan_metro = {"부산", "울산", "창원", "김해"}

# add(): 요소 추가
seoul_metro.add("의정부")
print(f"의정부 추가: {seoul_metro}")

# update(): 여러 요소 추가
seoul_metro.update(["파주", "이천"])
print(f"여러 도시 추가: {seoul_metro}")

# remove(): 요소 제거 (없으면 에러)
seoul_metro.remove("이천")
print(f"이천 제거: {seoul_metro}")

# discard(): 요소 제거 (없어도 에러 안 남)
seoul_metro.discard("존재하지않는도시")
print(f"안전 제거 시도 후: {len(seoul_metro)}")

# pop(): 임의 요소 제거 후 반환
removed_city = seoul_metro.pop()
print(f"제거된 도시: {removed_city}")

# clear(): 모든 요소 제거
test_set = seoul_metro.copy()
test_set.clear()
print(f"clear 후: {test_set}")
```

## 7.5 집합 연산

### 기본 집합 연산

수학 시간에 벤 다이어그램으로 그리던 집합 연산을 파이썬에서도 그대로 할 수 있습니다. 동아리 두 곳의 회원 명단을 떠올려 보세요.

| 연산 | 기호 | 메서드 | 뜻 |
|---|---|---|---|
| 합집합 | `a` \| `b` | `a.union(b)` | 둘 중 한 곳이라도 가입한 사람 |
| 교집합 | `a & b` | `a.intersection(b)` | 두 곳 모두 가입한 사람 |
| 차집합 | `a - b` | `a.difference(b)` | `a`에만 가입한 사람 |
| 대칭차집합 | `a ^ b` | `a.symmetric_difference(b)` | 한 곳에만 가입한 사람 |

기호와 메서드는 결과가 같고, 둘 다 원본을 바꾸지 않고 새 집합을 만듭니다. 차이가 하나 있는데, 기호는 양쪽이 모두 집합이어야 하지만 메서드는 리스트 같은 다른 묶음도 받아 줍니다. `{1, 2, 3} | [3, 4]`는 `TypeError`지만 `{1, 2, 3}.union([3, 4])`는 `{1, 2, 3, 4}`예요.

포함 관계는 `issubset()`(부분집합인가), `issuperset()`(상위집합인가)으로 묻습니다.

```python
# 프로그래밍 언어 선호도 조사
backend_developers = {"Python", "Java", "JavaScript", "Go", "C++"}
frontend_developers = {"JavaScript", "TypeScript", "Python", "HTML", "CSS"}
data_scientists = {"Python", "R", "SQL", "Scala", "Java"}

# 합집합 (union): |, union()
all_languages = backend_developers | frontend_developers | data_scientists
print(f"모든 언어: {all_languages}")

# 교집합 (intersection): &, intersection()
backend_frontend = backend_developers & frontend_developers
print(f"백엔드-프론트엔드 공통: {backend_frontend}")

# 차집합 (difference): -, difference()
only_backend = backend_developers - frontend_developers
print(f"백엔드 전용: {only_backend}")

# 대칭차집합 (symmetric_difference): ^, symmetric_difference()
backend_or_frontend = backend_developers ^ frontend_developers
print(f"백엔드 또는 프론트엔드 전용: {backend_or_frontend}")

# 부분집합 검사
python_users = {"Python"}
print(f"Python 사용자가 데이터 과학자 부분집합인가? {python_users.issubset(data_scientists)}")
print(f"데이터 과학자가 Python 사용자 상위집합인가? {data_scientists.issuperset(python_users)}")
```

결과를 표와 맞춰 보세요. 백엔드와 프론트엔드에 모두 있는 것은 Python과 JavaScript뿐이고, 대칭차집합에는 그 둘을 뺀 나머지가 모두 들어갑니다. 출력 순서는 실행할 때마다 달라질 수 있지만 원소의 구성은 같아요.

### 집합 연산 실무 활용

실무에서는 "전체 몇 개인가", "어느 쪽에 속하는가"를 따질 때 집합을 씁니다. 아래 예제는 계열별 전공 집합을 합쳐 전체 전공 수를 세고, 컴프리헨션으로 "컴퓨터"나 "정보"라는 글자가 들어간 전공을 골라냅니다. `any(…)`는 "키워드 중 하나라도 들어 있니?"를 묻는 내장 함수예요. 마지막 함수는 전공 이름에 쓰인 글자의 빈도를 딕셔너리로 세어 계열마다 많이 쓰인 글자를 뽑습니다.

```python
# 한국 대학교 전공 분석
engineering_majors = {
    "컴퓨터공학과", "전자공학과", "기계공학과", 
    "화학공학과", "건축공학과", "산업공학과"
}

science_majors = {
    "수학과", "물리학과", "화학과", "생물학과",
    "컴퓨터과학과", "통계학과", "지구과학과"
}

business_majors = {
    "경영학과", "경제학과", "회계학과", 
    "마케팅학과", "국제통상학과", "경영정보학과"
}

# 전체 전공
all_majors = engineering_majors | science_majors | business_majors
print(f"총 전공 수: {len(all_majors)}")

# STEM 전공 (Science, Technology, Engineering, Mathematics)
stem_majors = engineering_majors | science_majors
print(f"STEM 전공: {len(stem_majors)}개")

# 컴퓨터 관련 전공 찾기
computer_keywords = {"컴퓨터", "정보"}
computer_majors = {
    major for major in all_majors 
    if any(keyword in major for keyword in computer_keywords)
}
print(f"컴퓨터 관련 전공: {computer_majors}")

# 학과별 특성 분석
def analyze_major_characteristics(majors, category_name):
    char_frequency = {}
    for major in majors:
        for char in major:
            char_frequency[char] = char_frequency.get(char, 0) + 1
    
    common_chars = sorted(char_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"{category_name} 전공 특성 문자: {common_chars}")

analyze_major_characteristics(engineering_majors, "공학계열")
analyze_major_characteristics(science_majors, "자연과학계열")
```

전공 수는 공학 6개, 자연과학 7개, 경영 6개를 합쳐 19개이고, 겹치는 전공이 없으니 합집합도 19개 그대로입니다. 만약 같은 학과가 두 계열에 모두 들어 있었다면 합집합에서는 한 번만 세어졌을 거예요. "컴퓨터 관련 전공"에 경영정보학과가 들어간 것도 확인해 보세요. "정보"라는 글자 때문입니다. 글자로 분류하는 방법은 간단한 대신 이런 의외의 결과가 생길 수 있어요.

## 7.6 딕셔너리와 집합의 성능

### 해시 테이블의 성능 특성

드디어 딕셔너리와 집합의 비밀입니다. 리스트에서 `x in 리스트`는 앞에서부터 하나씩 확인하니 원소가 10만 개면 최악의 경우 10만 번 비교해요. 딕셔너리와 집합은 어떻게 바로 찾을까요?

학교 사물함을 생각해 봅시다. 사물함이 100칸 있고, "이름의 획수를 더해서 100으로 나눈 나머지 번호 칸에 넣는다"는 규칙이 있다고 해요. 그러면 "김철수"의 물건을 찾을 때 1번 칸부터 열어 볼 필요가 없습니다. 이름으로 번호를 계산해서 그 칸만 열면 되죠. 이렇게 **값을 보고 자리 번호를 계산하는 함수**를 **해시 함수**, 그 번호대로 칸에 나눠 담는 표를 **해시 테이블**이라고 합니다. 파이썬의 딕셔너리와 집합이 바로 해시 테이블이에요.

이제 키가 불변이어야 하는 이유도 보입니다. 이름표로 칸 번호를 계산해서 넣어 뒀는데, 그 뒤에 이름표가 바뀌면 계산되는 칸 번호도 바뀌어서 다시는 찾을 수 없게 되거든요.

해시 테이블에서 찾는 시간은 원소 수와 거의 상관이 없습니다. 이것을 "평균 O(1)"이라고 해요. 이 책의 실행 환경에서 `timeit`으로 원소 10만 개 중 마지막 값을 200번씩 찾아 평균을 내 보니, 리스트는 한 번에 약 0.3밀리초, 집합은 약 26나노초로 1만 배 넘게 차이가 났습니다. 아래 `performance_comparison()`이 바로 그 측정입니다. `time.time()`으로 딱 한 번만 재면 집합 쪽 시간이 너무 짧아 `0.000000초`로 찍히기 쉽고, 그러면 마지막 줄의 나눗셈에서 `ZeroDivisionError`가 나요. 그래서 `timeit.timeit()`으로 같은 검색을 200번 반복한 시간을 재고 200으로 나눠 한 번의 평균을 구합니다. 맨 아래 줄의 주석을 풀어 직접 실행해 보세요. 숫자는 컴퓨터마다 다르지만 차이가 수천 배 이상이라는 점은 같을 거예요.

```python
import timeit

def performance_comparison():
    """딕셔너리/집합 vs 리스트 성능 비교"""
    # 테스트 데이터 생성
    size = 100000
    test_data = list(range(size))
    test_list = test_data.copy()
    test_set = set(test_data)
    test_dict = {i: f"값_{i}" for i in test_data}
    
    search_target = size - 1  # 마지막 요소 검색
    repeat = 200  # 한 번만 재면 너무 짧아 0초로 찍히므로 여러 번 재서 평균을 낸다
    
    # 리스트에서 검색 (O(n))
    list_search_time = timeit.timeit(lambda: search_target in test_list, number=repeat) / repeat
    
    # 집합에서 검색 (O(1) 평균)
    set_search_time = timeit.timeit(lambda: search_target in test_set, number=repeat) / repeat
    
    # 딕셔너리에서 검색 (O(1) 평균)
    dict_search_time = timeit.timeit(lambda: search_target in test_dict, number=repeat) / repeat
    
    print("검색 성능 비교 (10만 개 요소, 1회 평균):")
    print(f"리스트 검색: {list_search_time:.9f}초")
    print(f"집합 검색:   {set_search_time:.9f}초")
    print(f"딕셔너리 검색: {dict_search_time:.9f}초")
    print(f"집합이 리스트보다 {list_search_time/set_search_time:,.0f}배 빠름")

# 성능 테스트 실행 (주석 해제 시)
# performance_comparison()
```

> **Q. 해시 값은 직접 볼 수 있나요?**
> 내장 함수 `hash()`로 볼 수 있습니다. `hash((1, 2))`처럼 불변 값은 정수가 나오고, `hash([1, 2])`처럼 리스트를 넣으면 `TypeError: unhashable type: 'list'`가 나요. 이렇게 해시 값을 계산할 수 있는 것을 **해시 가능(hashable)** 하다고 하며, 딕셔너리의 키와 집합의 원소는 해시 가능해야 합니다. 리스트가 든 튜플 `([1],)`도 안쪽 리스트 때문에 해시 가능하지 않아요. 참고로 문자열의 해시 값은 보안상의 이유로 파이썬을 새로 실행할 때마다 달라집니다. `hash("가")`를 두 번 따로 실행해 보면 다른 숫자가 나와요. 그래서 해시 값을 파일에 저장해 두고 나중에 비교하는 식으로 쓰면 안 됩니다.

### 메모리 사용량과 최적화

빠른 데는 대가가 있습니다. 사물함 방식은 칸이 넉넉해야 잘 동작해서 빈칸을 많이 남겨 두거든요. 아래 함수를 실행해 보면 원소 1,000개를 담는 데 리스트와 튜플은 약 8KB인데, 집합은 약 33KB, 딕셔너리는 약 37KB를 씁니다(이 책의 실행 환경 기준). **메모리를 더 쓰는 대신 시간을 아끼는** 거래예요. 그래서 마지막에 출력되는 권장사항처럼 용도에 맞게 고르는 것이 중요합니다.

```python
import sys

def memory_analysis():
    """자료구조별 메모리 사용량 분석"""
    size = 1000
    
    # 같은 데이터를 다른 구조로 저장
    test_list = list(range(size))
    test_tuple = tuple(range(size))
    test_set = set(range(size))
    test_dict = {i: i for i in range(size)}
    
    print("메모리 사용량 비교 (1000개 요소):")
    print(f"리스트:     {sys.getsizeof(test_list):5} bytes")
    print(f"튜플:       {sys.getsizeof(test_tuple):5} bytes") 
    print(f"집합:       {sys.getsizeof(test_set):5} bytes")
    print(f"딕셔너리:   {sys.getsizeof(test_dict):5} bytes")
    
    # 용도별 권장사항
    print("\n용도별 권장사항:")
    print("- 순서가 중요하고 중복 허용: 리스트")
    print("- 불변이고 순서 중요: 튜플")  
    print("- 중복 없는 고유값, 빠른 검색: 집합")
    print("- 키-값 매핑, 빠른 조회: 딕셔너리")

memory_analysis()
```

## 7.7 실무 예제: 한국어 텍스트 분석 시스템

이 장에서 배운 딕셔너리와 집합으로 글을 분석해 봅시다. 이 절의 코드 세 개는 이어지는 하나의 프로그램이라 차례대로 모두 실행해야 동작합니다. 두 번째와 세 번째 블록이 첫 번째 블록의 `KoreanTextAnalyzer`를 쓰거든요.

### 기본 텍스트 분석 클래스

새로 등장하는 도구는 `collections` 모듈의 두 가지 특별한 딕셔너리입니다.

- **`Counter`**: 묶음을 넣으면 원소마다 몇 번 나왔는지 세어 주는 딕셔너리입니다. `Counter([1, 1, 1, 2, 2, 3, 3, 3, 3, 3])`은 `Counter({3: 5, 1: 3, 2: 2})`이고, `.most_common(n)`은 가장 많이 나온 n개를 `(원소, 횟수)` 튜플 리스트로 돌려줘요. 앞에서 `get(키, 0) + 1`로 직접 세던 일을 한 줄로 해 줍니다.
- **`defaultdict`**: 없는 키에 접근하면 `KeyError` 대신 정해 둔 기본값을 자동으로 만들어 넣는 딕셔너리입니다. `defaultdict(int)`는 0, `defaultdict(list)`는 빈 리스트에서 시작해요.

분석기 곳곳에서 집합도 쓰입니다. 불용어("이", "그", "및" 같은 분석에 의미가 적은 말)를 집합에 담아 두고 `word not in self.stop_words`로 빠르게 걸러 내고, `len(set(meaningful_words))`로 서로 다른 단어 수를 셉니다. 클래스(`class`) 문법은 11장에서 배우니, 지금은 관련 함수를 한 상자에 묶어 둔 것으로 읽어 주세요.

```python
from collections import Counter, defaultdict
import re

class KoreanTextAnalyzer:
    """한국어 텍스트 분석기"""
    
    def __init__(self):
        self.stop_words = {
            "이", "그", "저", "것", "수", "등", "들", "및", "또는", 
            "하지만", "그러나", "따라서", "즉", "예를 들어"
        }
        
    def analyze_text(self, text):
        """텍스트 종합 분석"""
        # 기본 통계
        char_count = len(text)
        char_count_no_space = len(text.replace(' ', ''))
        word_count = len(text.split())
        line_count = text.count('\n') + 1
        
        # 문자 분석
        char_frequency = self._analyze_characters(text)
        
        # 단어 분석
        word_frequency = self._analyze_words(text)
        
        # 문장 분석
        sentence_analysis = self._analyze_sentences(text)
        
        return {
            "기본통계": {
                "전체문자수": char_count,
                "공백제외문자수": char_count_no_space,
                "단어수": word_count,
                "줄수": line_count
            },
            "문자분석": char_frequency,
            "단어분석": word_frequency,
            "문장분석": sentence_analysis
        }
    
    def _analyze_characters(self, text):
        """문자 빈도 분석"""
        # 한글, 영문, 숫자, 기타 분류
        korean_chars = set()
        english_chars = set()
        digits = set()
        special_chars = set()
        
        char_frequency = Counter(text.replace(' ', '').replace('\n', ''))
        
        for char in char_frequency:
            if '가' <= char <= '힣' or 'ㄱ' <= char <= 'ㅣ':
                korean_chars.add(char)
            elif 'a' <= char.lower() <= 'z':
                english_chars.add(char)
            elif char.isdigit():
                digits.add(char)
            else:
                special_chars.add(char)
        
        return {
            "총_고유문자수": len(char_frequency),
            "한글문자": {
                "개수": len(korean_chars),
                "빈출문자": char_frequency.most_common(10)
            },
            "영문문자수": len(english_chars),
            "숫자문자수": len(digits),
            "특수문자수": len(special_chars)
        }
    
    def _analyze_words(self, text):
        """단어 분석"""
        # 간단한 한국어 토큰화 (공백 기준)
        words = text.split()
        
        # 불용어 제거
        meaningful_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 1
        ]
        
        word_frequency = Counter(meaningful_words)
        
        return {
            "전체단어수": len(words),
            "유의미단어수": len(meaningful_words),
            "고유단어수": len(set(meaningful_words)),
            "평균단어길이": sum(len(word) for word in meaningful_words) / len(meaningful_words) if meaningful_words else 0,
            "빈출단어": word_frequency.most_common(10),
            "긴단어": sorted(set(meaningful_words), key=len, reverse=True)[:5]
        }
    
    def _analyze_sentences(self, text):
        """문장 분석"""
        # 문장 구분 (간단한 방식)
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        sentence_lengths = [len(s) for s in sentences]
        
        return {
            "문장수": len(sentences),
            "평균문장길이": sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            "최장문장길이": max(sentence_lengths) if sentence_lengths else 0,
            "최단문장길이": min(sentence_lengths) if sentence_lengths else 0
        }
```

### 텍스트 분석 실행 및 보고서

분석 결과는 "딕셔너리 안의 딕셔너리" 모양으로 돌아옵니다. 그래서 `results["문자분석"]["한글문자"]["빈출문자"]`처럼 키를 차례로 따라 들어가 원하는 값을 꺼내요.

```python
def demonstrate_text_analysis():
    """텍스트 분석 시연"""
    
    # 분석할 한국어 텍스트
    sample_text = """
파이썬은 1991년 귀도 반 로섬이 개발한 프로그래밍 언어입니다.
파이썬의 철학은 코드의 가독성과 단순함을 중시합니다.
들여쓰기를 사용하여 코드 블록을 구분하는 특징이 있습니다.
파이썬은 객체지향, 함수형, 절차형 프로그래밍을 모두 지원합니다.
웹 개발, 데이터 분석, 인공지능, 자동화 등 다양한 분야에서 사용됩니다.
배우기 쉽고 강력한 기능을 제공하여 전 세계 개발자들이 사용합니다.
"""
    
    analyzer = KoreanTextAnalyzer()
    results = analyzer.analyze_text(sample_text)
    
    print("한국어 텍스트 분석 결과")
    print("=" * 50)
    
    # 기본 통계
    basic_stats = results["기본통계"]
    print(f"\n기본 통계:")
    print(f"  전체 문자 수: {basic_stats['전체문자수']}자")
    print(f"  공백 제외: {basic_stats['공백제외문자수']}자")
    print(f"  단어 수: {basic_stats['단어수']}개")
    print(f"  줄 수: {basic_stats['줄수']}줄")
    
    # 문자 분석
    char_analysis = results["문자분석"]
    print(f"\n문자 분석:")
    print(f"  고유 문자 수: {char_analysis['총_고유문자수']}개")
    print(f"  한글 문자 수: {char_analysis['한글문자']['개수']}개")
    print(f"  빈출 문자 TOP 5:")
    for char, count in char_analysis['한글문자']['빈출문자'][:5]:
        print(f"    '{char}': {count}회")
    
    # 단어 분석
    word_analysis = results["단어분석"]
    print(f"\n단어 분석:")
    print(f"  전체 단어 수: {word_analysis['전체단어수']}개")
    print(f"  유의미 단어 수: {word_analysis['유의미단어수']}개")
    print(f"  고유 단어 수: {word_analysis['고유단어수']}개")
    print(f"  평균 단어 길이: {word_analysis['평균단어길이']:.1f}자")
    print(f"  빈출 단어 TOP 5:")
    for word, count in word_analysis['빈출단어'][:5]:
        print(f"    '{word}': {count}회")
    
    # 문장 분석
    sentence_analysis = results["문장분석"]
    print(f"\n문장 분석:")
    print(f"  문장 수: {sentence_analysis['문장수']}개")
    print(f"  평균 문장 길이: {sentence_analysis['평균문장길이']:.1f}자")
    print(f"  최장 문장 길이: {sentence_analysis['최장문장길이']}자")

# 텍스트 분석 실행
demonstrate_text_analysis()
```

실행하면 6문장, 47단어가 나오고 빈출 단어 1위는 "파이썬은"(2회)입니다. 빈출 문자 TOP 5에 마침표 `.`와 쉼표 `,`가 끼어 있는 것이 보이죠? "한글문자" 항목이지만 `most_common()`은 공백만 뺀 **모든 글자**를 세었기 때문이에요. 또 "파이썬은"과 "파이썬의"가 다른 단어로 세어지는 것처럼, 공백으로만 단어를 나누면 조사가 붙은 말이 모두 따로 셉니다. 5장의 텍스트 분석기와 같은 한계예요.

### 고급 텍스트 분석 기능

고급 분석기는 기본 분석기를 물려받아(`class AdvancedKoreanAnalyzer(KoreanTextAnalyzer)`, 상속은 13장에서 배웁니다) 기능을 더합니다. 가장 눈여겨볼 곳은 `compare_texts()`의 집합 연산이에요.

- `words1 & words2`: 두 글에 모두 나온 단어(교집합)
- `words1 - words2`: 첫 글에만 나온 단어(차집합)
- `len(교집합) / len(합집합)`: **자카드 유사도**. 두 글에 쓰인 단어 전체 중에서 겹치는 단어의 비율로, 0이면 하나도 안 겹치고 1이면 완전히 같습니다.

집합 연산 몇 줄로 "두 글이 얼마나 비슷한가"라는 질문에 숫자로 답할 수 있다는 점이 핵심입니다.

```python
class AdvancedKoreanAnalyzer(KoreanTextAnalyzer):
    """고급 한국어 텍스트 분석기"""
    
    def __init__(self):
        super().__init__()
        self.pos_patterns = {
            "조사": ["은", "는", "이", "가", "을", "를", "의", "에", "에서", "로", "으로"],
            "어미": ["다", "요", "습니다", "었다", "았다", "겠다", "면서", "지만"],
            "접속사": ["그리고", "하지만", "그러나", "따라서", "그러므로", "또한"]
        }
    
    def compare_texts(self, text1, text2):
        """두 텍스트 비교 분석"""
        analysis1 = self.analyze_text(text1)
        analysis2 = self.analyze_text(text2)
        
        # 공통 단어 찾기
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        common_words = words1 & words2
        unique_to_text1 = words1 - words2
        unique_to_text2 = words2 - words1
        
        # 유사도 계산 (자카드 유사도)
        jaccard_similarity = len(common_words) / len(words1 | words2) if words1 | words2 else 0
        
        return {
            "공통단어": list(common_words),
            "텍스트1_고유단어": list(unique_to_text1),
            "텍스트2_고유단어": list(unique_to_text2),
            "자카드_유사도": jaccard_similarity,
            "분석1": analysis1,
            "분석2": analysis2
        }
    
    def extract_keywords(self, text, top_n=10):
        """키워드 추출"""
        words = [word for word in text.split() if len(word) > 2]
        word_freq = Counter(words)
        
        # 불용어와 조사/어미 제거
        filtered_words = {}
        for word, freq in word_freq.items():
            if (word not in self.stop_words and 
                not any(word.endswith(pattern) for patterns in self.pos_patterns.values() for pattern in patterns)):
                filtered_words[word] = freq
        
        # 빈도순 정렬
        keywords = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return keywords
    
    def generate_summary_stats(self, texts):
        """여러 텍스트의 종합 통계"""
        all_analyses = [self.analyze_text(text) for text in texts]
        
        # 전체 통계 집계
        total_chars = sum(analysis["기본통계"]["전체문자수"] for analysis in all_analyses)
        total_words = sum(analysis["기본통계"]["단어수"] for analysis in all_analyses)
        
        # 모든 단어 수집
        all_words = []
        for text in texts:
            all_words.extend(text.split())
        
        unique_words = set(all_words)
        word_frequency = Counter(all_words)
        
        return {
            "텍스트수": len(texts),
            "총문자수": total_chars,
            "총단어수": total_words,
            "고유단어수": len(unique_words),
            "평균텍스트길이": total_chars / len(texts),
            "전체빈출단어": word_frequency.most_common(20),
            "어휘다양성": len(unique_words) / total_words if total_words > 0 else 0
        }

# 고급 분석 시연
def demonstrate_advanced_analysis():
    """고급 분석 기능 시연"""
    
    texts = [
        "파이썬은 직관적이고 배우기 쉬운 프로그래밍 언어입니다. 다양한 라이브러리가 있어서 개발이 빠릅니다.",
        "자바는 객체지향 프로그래밍 언어입니다. 플랫폼 독립적이며 대규모 애플리케이션 개발에 적합합니다.",
        "자바스크립트는 웹 개발의 핵심 언어입니다. 프론트엔드와 백엔드 모두에서 사용할 수 있습니다."
    ]
    
    analyzer = AdvancedKoreanAnalyzer()
    
    print("\n고급 텍스트 분석")
    print("=" * 50)
    
    # 종합 통계
    summary = analyzer.generate_summary_stats(texts)
    print(f"\n종합 통계:")
    print(f"  분석 텍스트 수: {summary['텍스트수']}개")
    print(f"  총 문자 수: {summary['총문자수']}자")
    print(f"  고유 단어 수: {summary['고유단어수']}개")
    print(f"  어휘 다양성: {summary['어휘다양성']:.3f}")
    
    # 키워드 추출
    combined_text = " ".join(texts)
    keywords = analyzer.extract_keywords(combined_text, 5)
    print(f"\n주요 키워드:")
    for word, freq in keywords:
        print(f"  {word}: {freq}회")
    
    # 텍스트 간 비교
    comparison = analyzer.compare_texts(texts[0], texts[1])
    print(f"\n텍스트 1-2 비교:")
    print(f"  공통 단어: {len(comparison['공통단어'])}개")
    print(f"  유사도: {comparison['자카드_유사도']:.3f}")

demonstrate_advanced_analysis()
```

결과를 보면 첫 번째와 두 번째 글은 "프로그래밍", "언어입니다." 두 단어만 겹쳐서 유사도가 0.105입니다. 그런데 주요 키워드 1위가 "언어입니다."(3회)로, 마침표까지 붙은 채 나왔어요. `extract_keywords()`는 단어 끝이 조사·어미 목록과 같으면 거르는데, "언어입니다."는 마침표로 끝나서 "다"로 끝나는 어미 검사를 통과해 버렸기 때문입니다. 실제 분석에서는 단어를 나누기 전에 문장부호를 지우는 전처리가 필요해요.

## 7.8 실습 문제

### 기본 문제 (1-5번)

```python
# 1번: 한국 도시별 인구 딕셔너리 조작
cities_population = {
    "서울": 9720846, "부산": 3448737, "대구": 2438031,
    "인천": 2963991, "광주": 1441970, "대전": 1475221
}
# 문제: 인구가 300만 이상인 도시만 필터링하세요
# 답:
major_cities = {city: pop for city, pop in cities_population.items() if pop >= 3000000}
print(f"대도시: {major_cities}")

# 2번: 학생 성적 딕셔너리 처리
student_scores = {
    "김철수": [85, 92, 78, 88],
    "이영희": [95, 87, 91, 89],
    "박민수": [78, 95, 85, 92]
}
# 문제: 각 학생의 평균 점수를 계산하세요
# 답:
averages = {name: sum(scores)/len(scores) for name, scores in student_scores.items()}
print(f"평균 점수: {averages}")

# 3번: 집합 연산 활용
group_a = {"김철수", "이영희", "박민수", "최지영"}
group_b = {"이영희", "박민수", "정수진", "한미영"}
# 문제: 두 그룹 모두에 속한 사람과 한 그룹에만 속한 사람을 찾으세요
# 답:
both_groups = group_a & group_b
only_one_group = group_a ^ group_b
print(f"두 그룹 모두: {both_groups}")
print(f"한 그룹만: {only_one_group}")

# 4번: 문자 빈도 계산
text = "안녕하세요 파이썬 프로그래밍을 배워봅시다"
# 문제: 각 문자의 빈도를 딕셔너리로 만드세요 (공백 제외)
# 답:
char_freq = {}
for char in text.replace(' ', ''):
    char_freq[char] = char_freq.get(char, 0) + 1
print(f"문자 빈도: {char_freq}")

# 5번: 딕셔너리 병합
dict1 = {"a": 1, "b": 2, "c": 3}
dict2 = {"b": 4, "c": 5, "d": 6}
# 문제: 두 딕셔너리를 병합하되 dict2의 값을 우선하세요
# 답:
merged = {**dict1, **dict2}
print(f"병합 결과: {merged}")
```

### 중급 문제 (6-10번)

```python
# 6번: 중첩 딕셔너리 처리
company = {
    "개발팀": {
        "김철수": {"직급": "시니어", "연봉": 6000},
        "이영희": {"직급": "주니어", "연봉": 4000}
    },
    "마케팅팀": {
        "박민수": {"직급": "매니저", "연봉": 7000},
        "최지영": {"직급": "사원", "연봉": 3500}
    }
}
# 문제: 부서별 평균 연봉을 계산하세요
# 답:
dept_averages = {}
for dept, employees in company.items():
    salaries = [emp["연봉"] for emp in employees.values()]
    dept_averages[dept] = sum(salaries) / len(salaries)
print(f"부서별 평균 연봉: {dept_averages}")

# 7번: defaultdict 활용
from collections import defaultdict

transactions = [
    ("김철수", "식료품", 15000),
    ("김철수", "교통", 5000),
    ("이영희", "식료품", 20000),
    ("이영희", "문화", 12000),
    ("김철수", "식료품", 8000)
]
# 문제: 사람별 카테고리별 지출 총액을 계산하세요
# 답:
expenses = defaultdict(lambda: defaultdict(int))
for name, category, amount in transactions:
    expenses[name][category] += amount

for name, categories in expenses.items():
    print(f"{name}: {dict(categories)}")

# 8번: Counter 활용
from collections import Counter

korean_text = "가나다라마바사아자차카타파하 가나다 가나 가"
# 문제: 가장 자주 나타나는 문자 3개를 찾으세요
# 답:
char_counter = Counter(korean_text.replace(' ', ''))
most_common = char_counter.most_common(3)
print(f"가장 빈번한 문자 3개: {most_common}")

# 9번: 집합으로 중복 제거와 교집합
sales_2022 = {"사과", "바나나", "오렌지", "포도", "딸기"}
sales_2023 = {"바나나", "오렌지", "키위", "망고", "딸기"}
# 문제: 두 해 연속 판매된 상품, 2023년에 판매가 끝난 상품, 2023년 신상품을 찾으세요
# 답:
continuous_products = sales_2022 & sales_2023
discontinued_2023 = sales_2022 - sales_2023
new_2023 = sales_2023 - sales_2022
print(f"연속 판매: {continuous_products}")
print(f"2023 판매 종료: {discontinued_2023}")
print(f"2023 신상품: {new_2023}")

# 10번: 딕셔너리 컴프리헨션 고급
students = ["김철수", "이영희", "박민수", "최지영", "정수진"]
scores = [85, 92, 78, 88, 95]
# 문제: 점수가 80점 이상인 학생들의 등급(A/B)을 딕셔너리로 만드세요
# 답:
student_grades = {
    student: "A" if score >= 90 else "B"
    for student, score in zip(students, scores)
    if score >= 80
}
print(f"80점 이상 학생 등급: {student_grades}")
```

### 고급 문제 (11-15번)

```python
from collections import defaultdict

# 11번: 복잡한 데이터 구조 변환
raw_data = [
    {"name": "김철수", "dept": "개발", "skills": ["Python", "Java"]},
    {"name": "이영희", "dept": "개발", "skills": ["JavaScript", "Python"]},
    {"name": "박민수", "dept": "마케팅", "skills": ["Excel", "PowerPoint"]},
    {"name": "최지영", "dept": "개발", "skills": ["Java", "C++"]}
]
# 문제: 부서별로 보유 기술과 해당 기술을 가진 사람 수를 계산하세요
# 답:
dept_skills = defaultdict(lambda: defaultdict(int))
for person in raw_data:
    dept = person["dept"]
    for skill in person["skills"]:
        dept_skills[dept][skill] += 1

for dept, skills in dept_skills.items():
    print(f"{dept}: {dict(skills)}")

# 12번: 그래프 표현과 탐색
# 한국 주요 도시 간 연결 관계
city_connections = {
    "서울": {"인천", "수원", "춘천"},
    "인천": {"서울", "수원"},
    "수원": {"서울", "인천", "대전"},
    "대전": {"수원", "대구", "광주"},
    "대구": {"대전", "부산"},
    "부산": {"대구"},
    "광주": {"대전"},
    "춘천": {"서울"}
}
# 문제: 서울에서 시작해서 2단계 이내로 갈 수 있는 모든 도시를 찾으세요
# 답:
start_city = "서울"
reachable_1 = city_connections[start_city]
reachable_2 = set()

for city in reachable_1:
    reachable_2.update(city_connections[city])

all_reachable = reachable_1 | reachable_2
all_reachable.discard(start_city)  # 시작 도시 제외
print(f"서울에서 2단계 이내 도시: {all_reachable}")

# 13번: 역인덱스 구축
documents = {
    "doc1": "파이썬은 강력한 프로그래밍 언어입니다",
    "doc2": "자바는 객체지향 프로그래밍 언어입니다", 
    "doc3": "파이썬과 자바는 인기 있는 언어입니다"
}
# 문제: 단어별로 어떤 문서에 등장하는지 역인덱스를 만드세요
# 답:
inverse_index = defaultdict(set)
for doc_id, content in documents.items():
    words = content.split()
    for word in words:
        inverse_index[word].add(doc_id)

# 특정 단어 검색
search_word = "프로그래밍"
found_docs = inverse_index.get(search_word, set())
print(f"'{search_word}' 포함 문서: {found_docs}")

# 14번: 캐시 구현
class LRUCache:
    """LRU(Least Recently Used) 캐시 구현"""
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.access_order = []
    
    def get(self, key):
        if key in self.cache:
            # 접근 순서 업데이트
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            # 기존 키 업데이트
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # 새 키 추가
            if len(self.cache) >= self.capacity:
                # 가장 오래된 항목 제거
                oldest = self.access_order.pop(0)
                del self.cache[oldest]
            
            self.cache[key] = value
            self.access_order.append(key)

# LRU 캐시 테스트
cache = LRUCache(3)
cache.put("한국어", "Korean")
cache.put("영어", "English") 
cache.put("중국어", "Chinese")
print(f"캐시 상태: {cache.cache}")

cache.put("일본어", "Japanese")  # 한국어가 제거됨
print(f"일본어 추가 후: {cache.cache}")

# 15번: 복잡한 집계 연산
sales_data = [
    {"region": "서울", "product": "노트북", "sales": 150, "month": "2023-01"},
    {"region": "서울", "product": "마우스", "sales": 300, "month": "2023-01"},
    {"region": "부산", "product": "노트북", "sales": 100, "month": "2023-01"},
    {"region": "서울", "product": "노트북", "sales": 200, "month": "2023-02"},
    {"region": "부산", "product": "마우스", "sales": 250, "month": "2023-02"},
]
# 문제: 지역별, 제품별, 월별 매출을 다차원으로 집계하세요
# 답:
multi_dim_sales = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

for record in sales_data:
    region = record["region"]
    product = record["product"]  
    month = record["month"]
    sales = record["sales"]
    
    multi_dim_sales[region][product][month] += sales

# 결과 출력
for region, products in multi_dim_sales.items():
    print(f"\n{region} 지역:")
    for product, months in products.items():
        print(f"  {product}: {dict(months)}")
        
# 총합 계산
region_totals = {}
for region, products in multi_dim_sales.items():
    total = sum(
        sales 
        for product_data in products.values()
        for sales in product_data.values()
    )
    region_totals[region] = total

print(f"\n지역별 총 매출: {region_totals}")
```

## 7.9 다음 장 미리보기

다음 Chapter 8에서는 **고급 데이터 구조**를 학습합니다:

### 주요 내용 미리보기
- **dataclass**: 클래스 정의 간소화와 자동 메서드 생성
- **NamedTuple**: 구조화된 데이터와 타입 힌팅
- **Enum**: 상수 정의와 열거형 활용
- **typing**: 고급 타입 힌팅과 제네릭
- **collections 모듈**: deque, ChainMap, UserDict 등
- **실무 프로젝트**: 한국 부동산 데이터 분석 시스템

### 연결 포인트
- 딕셔너리/집합의 해시 테이블 → dataclass의 성능 최적화
- 기본 자료구조 → 도메인 특화 자료구조
- 동적 타이핑 → 정적 타입 힌팅 도입

딕셔너리와 집합을 완전히 이해했다면, 이제 더욱 구조화되고 타입 안전한 고급 데이터 구조들로 전문적인 애플리케이션을 개발할 준비가 되었습니다!

---

> **학습 팁**: 딕셔너리는 키-값 매핑이 필요할 때, 집합은 중복 제거와 빠른 검색이 필요할 때 사용하세요. 해시 테이블 기반이므로 성능이 뛰어나지만 키는 불변 객체여야 합니다.

**다음 장에서 만나요!** 