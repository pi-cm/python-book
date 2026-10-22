# Chapter 6: 리스트와 튜플

> **학습 목표**  
> - 리스트와 튜플의 특징과 차이점 이해
> - 리스트의 다양한 메서드 활용
> - 튜플의 불변성과 활용 사례
> - 시퀀스 공통 연산 습득
> - 리스트/튜플 언패킹과 활용
> - 실제 한국 데이터를 활용한 프로젝트 구현

---

## 들어가며: 여러 개를 한 번에 담으려면?

문자열은 글자 여러 개를 한 줄로 꿰어서 담고 있죠. 그럼 숫자를 여러 개 담으려면 어떻게 할까요? 반 학생 30명의 점수를 `점수1`, `점수2`, …, `점수30`처럼 변수 30개에 하나씩 넣을 수는 없습니다. 평균을 내려면 30개를 일일이 더해야 하고, 한 명이 전학 오면 변수 이름을 새로 지어야 하니까요.

그래서 파이썬에는 값 여러 개를 하나로 묶어 담는 그릇, 즉 **컬렉션** 자료형이 있습니다. 어떤 괄호로 감싸느냐에 따라 종류가 정해져요.

- `[ … ]`로 감싸면 **리스트(list)**
- `( … )`로 감싸면 **튜플(tuple)**
- `{키: 값, … }`로 감싸면 **딕셔너리(dict)**
- `{ … }`로 감싸면 **집합(set)**

이번 장에서는 앞의 두 가지, 리스트와 튜플을 다룹니다. 둘 다 값을 **순서대로** 줄 세워 담는다는 공통점이 있어요. 이렇게 순서가 있어서 "몇 번째"라는 번호(인덱스)로 값을 꺼낼 수 있는 자료형을 **시퀀스(sequence)** 라고 부릅니다. 이미 만나 본 문자열과 `range`도 시퀀스예요. 그래서 문자열에서 배운 인덱싱과 슬라이싱, `len()`, `in`이 리스트와 튜플에서도 똑같이 통합니다.

둘의 차이는 딱 하나, **안의 내용을 바꿀 수 있느냐**입니다. 리스트는 언제든 넣고 빼고 고칠 수 있는 공책이고, 튜플은 한 번 인쇄하면 고칠 수 없는 인쇄물이에요. 딕셔너리와 집합은 다음 장(7장)에서 만납니다.

## 6.1 리스트 기본 개념

### 리스트란 무엇인가?

리스트는 여러 값을 순서대로 저장하는 가변(mutable) 자료구조입니다. 대괄호 안에 값을 쉼표로 구분해 넣으면 돼요. 예제의 `mixed`처럼 문자열, 숫자, 불리언을 섞어 담아도 되고, 리스트 안에 또 리스트를 넣을 수도 있습니다. 빈 리스트는 `[]`나 `list()`로 만듭니다. `list()` 괄호 안에 문자열이나 `range`처럼 하나씩 꺼낼 수 있는 것을 넣으면, 그 원소들을 차례로 담은 리스트가 만들어져요. `list("가나다")`는 `['가', '나', '다']`입니다.

```python
# 기본 리스트 생성
fruits = ["사과", "바나나", "오렌지", "포도"]
numbers = [1, 2, 3, 4, 5]
mixed = ["김철수", 25, True, 3.14]

# 빈 리스트 생성
empty_list1 = []
empty_list2 = list()

print(f"과일: {fruits}")
print(f"숫자: {numbers}")
print(f"혼합: {mixed}")
```

### 리스트 인덱싱과 슬라이싱

리스트의 원소에는 앞에서부터 0, 1, 2, … 번호가 붙습니다. 첫 번째가 1번이 아니라 **0번**이라는 점, 기억하죠? 뒤에서부터 셀 때는 -1, -2, … 를 씁니다. `cities[-1]`은 마지막 원소예요.

여러 개를 한꺼번에 잘라 낼 때는 **슬라이싱** `[시작:끝:간격]`을 씁니다. 규칙은 5장의 `range`와 같아요.

- `시작`부터 `끝` **직전**까지 자릅니다. `끝` 번째는 포함되지 않아요.
- `시작`을 비우면 처음부터, `끝`을 비우면 마지막까지, 둘 다 비우면 전체입니다.
- `간격`을 주면 그만큼 건너뛰고, 음수면 거꾸로 갑니다. 그래서 `[::-1]`은 전체를 뒤집은 것이에요.

예제의 `cities[2:5]`는 인덱스 2, 3, 4, 즉 세 번째부터 다섯 번째 도시를 꺼냅니다. 개수는 `5 - 2 = 3`개로 바로 계산되죠.

```python
cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]

# 인덱싱
print(f"첫 번째 도시: {cities[0]}")
print(f"마지막 도시: {cities[-1]}")
print(f"뒤에서 두 번째: {cities[-2]}")

# 슬라이싱
print(f"처음 3개 도시: {cities[:3]}")
print(f"마지막 3개 도시: {cities[-3:]}")
print(f"3번째부터 5번째까지: {cities[2:5]}")
print(f"홀수 번째 도시들: {cities[::2]}")
print(f"역순으로: {cities[::-1]}")

# 슬라이스로 부분 수정
cities[2:4] = ["창원", "안산"]
print(f"수정 후: {cities}")
```

마지막 두 줄은 리스트만 할 수 있는 일입니다. 슬라이스 자리에 새 값을 넣어서 "대구", "인천"을 "창원", "안산"으로 갈아 끼웠어요. 2장에서 문자열의 첫 글자를 `s[0] = "l"`로 바꾸려다 `TypeError`가 났던 것과 비교해 보세요. 리스트는 **가변(mutable)**, 즉 만든 뒤에도 내용을 바꿀 수 있는 자료형이라 가능한 일입니다.

## 6.2 리스트 메서드

### 요소 추가 메서드

리스트는 내용을 바꿀 수 있으니, 원소를 넣고 빼는 도구(메서드)가 여럿 있습니다. 추가하는 방법부터 볼게요.

- `append(x)`: 맨 끝에 `x` 하나를 붙입니다. 가장 많이 씁니다.
- `insert(i, x)`: `i`번 자리에 `x`를 끼워 넣습니다. 원래 `i`번과 그 뒤의 원소들은 한 칸씩 뒤로 밀려요.
- `extend(묶음)`: 다른 묶음의 원소를 **하나씩 풀어서** 끝에 이어 붙입니다.
- `+`: 두 리스트를 이어 붙인 **새 리스트**를 만듭니다. 원래 리스트는 그대로예요.

`append`, `insert`, `extend`는 원래 리스트 자체를 바꾸고, `+`는 원본을 두고 새것을 만든다는 차이를 기억하세요. 이 "원본을 바꾸느냐, 새것을 만드느냐"는 이 장 내내 나오는 질문입니다.

```python
korean_names = ["김철수", "이영희"]

# append(): 끝에 하나 추가
korean_names.append("박민수")
print(f"append 후: {korean_names}")

# insert(): 지정 위치에 추가
korean_names.insert(1, "최지영")
print(f"insert 후: {korean_names}")

# extend(): 여러 요소 추가
korean_names.extend(["정수진", "한미영"])
print(f"extend 후: {korean_names}")

# + 연산자로 추가
new_names = korean_names + ["윤태호", "강예린"]
print(f"+ 연산 후: {new_names}")
```

`append`와 `extend`의 차이는 리스트를 넣어 보면 분명해집니다. `append(["정수진", "한미영"])`이라고 했다면 리스트 **통째로** 원소 하나가 되어 `[…, ['정수진', '한미영']]`처럼 리스트 안에 리스트가 들어갔을 거예요. `extend`는 포장을 풀어서 두 이름을 각각 넣어 줍니다.

리스트끼리 `+`는 이어 붙이기라서 `[1, 2, 3] + [4, 5, 6]`은 `[1, 2, 3, 4, 5, 6]`입니다. 같은 자리의 원소끼리 더해 `[5, 7, 9]`를 얻고 싶다면 5장의 `zip()`으로 짝을 지어 더하면 돼요(`[a + b for a, b in zip(x, y)]`).

### 요소 제거 메서드

빼는 방법도 여러 가지입니다. **무엇을** 알고 있느냐에 따라 고르세요.

- 값을 알 때: `remove(값)`은 그 값을 찾아 지웁니다. 같은 값이 여러 개면 **처음 것 하나만** 지워요.
- 위치를 알 때: `pop(i)`는 `i`번 원소를 빼서 **돌려줍니다**. 위치를 안 주면 마지막 원소를 빼요. `del 리스트[i]`나 `del 리스트[2:4]`도 위치로 지우지만 돌려주지는 않습니다.
- 전부 지울 때: `clear()`입니다.

`pop()`으로 마지막 원소를 빼는 동작은 접시 쌓기와 같습니다. 접시는 맨 위에 올리고 맨 위에서부터 꺼내죠. 이렇게 나중에 넣은 것을 먼저 꺼내는 구조를 **스택(stack)** 이라고 하는데, 리스트에 `append()`로 넣고 `pop()`으로 꺼내면 바로 스택이 됩니다. 웹 브라우저의 "뒤로 가기"나 문서 편집기의 Ctrl+Z(되돌리기)가 이 구조예요. 반대로 줄을 선 순서대로 먼저 온 사람부터 나가는 구조는 **큐(queue)** 라고 하는데, 이건 8장에서 `deque`와 함께 만납니다.

```python
subjects = ["국어", "영어", "수학", "과학", "역사", "미술", "음악"]

# remove(): 값으로 제거 (첫 번째 일치 항목)
subjects.remove("미술")
print(f"remove 후: {subjects}")

# pop(): 인덱스로 제거 후 반환
removed = subjects.pop(2)  # 수학 제거
print(f"제거된 과목: {removed}")
print(f"pop 후: {subjects}")

# pop(): 마지막 요소 제거
last = subjects.pop()
print(f"마지막 과목: {last}")
print(f"마지막 pop 후: {subjects}")

# clear(): 모든 요소 제거
test_list = subjects.copy()
test_list.clear()
print(f"clear 후: {test_list}")

# del 문: 슬라이스로 제거
del subjects[1:3]
print(f"del 후: {subjects}")
```

`clear()`를 시험하기 전에 `subjects.copy()`로 복사본을 만든 것을 눈여겨보세요. 그냥 `test_list = subjects`라고 했다면 어떻게 됐을까요?

> **Q. `b = a`라고 하면 리스트가 복사되는 거 아닌가요?**
> 아닙니다. `=`는 리스트를 복사하는 게 아니라, 이미 있는 리스트에 **이름표를 하나 더 붙이는** 일이에요. 그래서 `a = [1, 2, 3]`, `b = a` 다음에 `b.append(4)`를 하면 `a`도 `[1, 2, 3, 4]`가 됩니다. 둘이 같은 물건이라 `a is b`가 `True`예요(3장의 `is` 참고). 예제에서 `test_list = subjects` 후에 `clear()`를 했다면 `subjects`까지 텅 비어서, 그다음 `del subjects[1:3]`은 지울 것이 없었을 겁니다. 따로 쓰고 싶으면 `a.copy()`나 `a[:]`, `list(a)`로 진짜 복사본을 만드세요.

리스트에서 원소를 지울 때 조심할 것이 하나 더 있습니다. 60점 미만인 점수를 지우려고 이렇게 써 보면 어떨까요?

```python
점수들 = [90, 45, 30, 80, 55]
for 점수 in 점수들:
    if 점수 < 60:
        점수들.remove(점수)
print(점수들)  # [90, 30, 80] - 30이 살아남았다!

점수들 = [90, 45, 30, 80, 55]
print([점수 for 점수 in 점수들 if 점수 >= 60])  # [90, 80]
```

45를 지우는 순간 뒤의 원소들이 한 칸씩 앞으로 당겨집니다. 30이 45가 있던 자리로 오는데, `for`는 이미 그 자리를 봤다고 생각하고 다음 칸으로 넘어가 버려요. 그래서 30은 검사도 받지 못하고 살아남습니다. **반복하면서 같은 리스트에서 원소를 지우지 마세요.** 남길 것만 골라 새 리스트를 만드는 것이 안전하고, 컴프리헨션을 쓰면 한 줄이면 됩니다.

### 검색과 정렬 메서드

`index(값)`은 그 값이 몇 번 자리에 있는지, `count(값)`은 몇 개 있는지 알려 줍니다. `index()`는 찾는 값이 없으면 `ValueError`를 내니, 있는지 확실하지 않으면 `in`으로 먼저 확인하세요.

정렬에는 두 가지 방법이 있고, 여기서도 "원본을 바꾸느냐, 새것을 만드느냐"가 갈립니다.

- `리스트.sort()`: 리스트 **자체**를 정렬합니다. 원래 순서는 사라져요. 리스트에만 있는 메서드입니다.
- `sorted(묶음)`: 정렬된 **새 리스트**를 돌려주고 원본은 그대로 둡니다. 튜플, 문자열 등 하나씩 꺼낼 수 있는 것이면 무엇이든 넣을 수 있어요.

`sort()`가 원본을 바꾸는 건 단점 같지만, 원래 순서가 더는 필요 없을 때는 복사본을 만들지 않아도 되니 오히려 장점입니다. 둘 다 `reverse=True`를 주면 내림차순이에요.

`reverse()`는 이름 때문에 헷갈리기 쉬운데, **정렬이 아닙니다.** 크기와 상관없이 지금 있는 순서를 그대로 거꾸로 뒤집기만 해요. `[3, 1, 2]`에 `reverse()`를 하면 `[2, 1, 3]`, `sort(reverse=True)`를 하면 `[3, 2, 1]`입니다.

```python
scores = [85, 92, 78, 95, 88, 92, 76, 89]

# index(): 값의 위치 찾기
position = scores.index(95)
print(f"95점의 위치: {position}")

# count(): 값의 개수 세기
count_92 = scores.count(92)
print(f"92점의 개수: {count_92}")

# sort(): 원본 정렬 (오름차순)
scores.sort()
print(f"오름차순 정렬: {scores}")

# sort(): 내림차순 정렬
scores.sort(reverse=True)
print(f"내림차순 정렬: {scores}")

# sorted(): 새로운 리스트 반환
original_scores = [85, 92, 78, 95, 88]
sorted_scores = sorted(original_scores)
print(f"원본: {original_scores}")
print(f"정렬된 복사본: {sorted_scores}")

# reverse(): 순서 뒤집기
korean_alphabet = ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ"]
korean_alphabet.reverse()
print(f"뒤집힌 자음: {korean_alphabet}")
```

### 한글 정렬

한글도 그냥 `sort()`하면 가나다순으로 정렬됩니다. 3장에서 본 것처럼 글자마다 매겨진 유니코드 번호가 가나다 순서대로 붙어 있기 때문이에요.

다른 기준으로 정렬하고 싶으면 `key`를 줍니다. `key`에는 **원소마다 정렬 기준값을 만들어 주는 함수**를 넣어요. `key=len`이면 파이썬이 원소마다 `len(원소)`를 계산해서 그 값으로 줄을 세웁니다. 마지막 예제의 `lambda x: (len(x), x)`는 이름 없는 짧은 함수인데(10장에서 배웁니다), 원소마다 `(길이, 단어)` 튜플을 기준으로 삼아요. 튜플은 앞 원소부터 비교하니 "길이가 짧은 순, 길이가 같으면 가나다순"이 됩니다.

```python
korean_words = ["사과", "바나나", "딸기", "포도", "오렌지"]

# 한글 가나다 순 정렬
korean_words.sort()
print(f"가나다순: {korean_words}")

# 길이순 정렬
korean_words.sort(key=len)
print(f"길이순: {korean_words}")

# 복잡한 정렬 (길이 우선, 같으면 가나다순)
korean_words.sort(key=lambda x: (len(x), x))
print(f"길이+가나다순: {korean_words}")
```

결과에서 "길이순"과 "길이+가나다순"이 똑같이 나왔죠? 파이썬의 정렬은 기준값이 같은 원소끼리는 **원래 순서를 그대로 지키는**(안정 정렬) 성질이 있습니다. 바로 앞에서 이미 가나다순으로 정렬해 두었으니, 길이로만 다시 정렬해도 같은 길이의 단어들은 가나다순을 유지한 거예요. 정렬 전 순서가 뒤죽박죽이었다면 두 결과는 달라집니다.

## 6.3 리스트 컴프리헨션과 고급 활용

### 기본 리스트 컴프리헨션

5장에서 배운 리스트 컴프리헨션을 리스트 관점에서 다시 정리해 봅시다. 첫 예제의 "기존 방식"은 빈 리스트 만들기, `for`로 돌기, `append()`로 넣기까지 세 줄이 필요하지만, 컴프리헨션은 `[i ** 2 for i in range(1, 11)]` 한 줄이면 됩니다. 이때 `i`는 그냥 붙인 이름이라 `x`든 `숫자`든 마음대로 바꿔도 돼요. 이름 문자열에 `name[0]`을 쓰면 첫 글자, 즉 성씨만 뽑을 수 있다는 것도 확인해 보세요.

```python
# 기존 방식
squares = []
for i in range(1, 11):
    squares.append(i ** 2)

# 리스트 컴프리헨션
squares = [i ** 2 for i in range(1, 11)]
print(f"제곱수들: {squares}")

# 한글 이름에서 성씨만 추출
full_names = ["김철수", "이영희", "박민수", "최지영", "정수진"]
surnames = [name[0] for name in full_names]
print(f"성씨들: {surnames}")

# 조건부 리스트 컴프리헨션
ages = [25, 17, 30, 16, 45, 19, 35]
adults = [age for age in ages if age >= 20]
print(f"성인 나이: {adults}")

# if-else 표현식
age_groups = ["성인" if age >= 20 else "미성년" for age in ages]
print(f"연령대: {age_groups}")
```

### 중첩 리스트 컴프리헨션

리스트 안에 리스트를 넣으면 표(2차원 데이터)를 만들 수 있습니다. `matrix[1][2]`처럼 대괄호를 두 번 쓰면 "1번 줄의 2번 칸"을 꺼내요.

행렬 **전치**는 표의 가로줄과 세로줄을 바꾸는 것입니다. `[[row[i] for row in matrix] for i in range(3)]`를 바깥부터 읽어 보세요. "열 번호 `i`마다(바깥), 모든 줄에서 `i`번 칸을 모아(안쪽) 새 줄을 만든다." 그래서 원래 0번 열이었던 `1, 4, 7`이 새 표의 0번 줄이 됩니다.

```python
# 구구단 만들기
multiplication_table = [[i * j for j in range(1, 10)] for i in range(2, 10)]
print("구구단 2단:")
print(multiplication_table[0])

# 행렬 전치
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
print(f"원본 행렬: {matrix}")
print(f"전치 행렬: {transposed}")

# 단어별로 한글 음절만 골라내기
words = ["안녕", "하세요", "파이썬"]
syllables = [[char for char in word if ord(char) >= 0xAC00] for word in words]
print(f"한글 문자들: {syllables}")
```

마지막 예제의 `ord(char)`는 글자의 유니코드 번호를 알려 주는 함수이고, `0xAC00`은 "가"의 번호를 16진수로 쓴 것입니다. 단어마다 "가" 이후 번호의 글자만 모으니 결과는 단어별로 쪼갠 음절 리스트가 돼요. 자음과 모음까지 나누려면 글자 번호를 계산해야 하는데, 2장의 `한글_자모_분리`가 그 방법입니다.

## 6.4 튜플 기본 개념

### 튜플의 특징

튜플이라는 단어는 처음 듣는 분이 대부분일 거예요. 수학에서 온 말로 "순서 있는 n개의 나열"이라는 뜻입니다. 다양한 원소를 순서대로 보관해 둔 묶음이죠. 여기에 하나만 더 외우고 가면 됩니다. 튜플은 **불변(immutable)** 객체입니다. 2장에서 "넘·스·튜(Number, String, Tuple)"로 외운 바로 그 튜플이에요.

튜플은 소괄호로 만든다고들 하지만, 사실 튜플을 만드는 것은 **괄호가 아니라 쉼표**입니다. 예제의 `colors = "빨강", "파랑", "노랑"`처럼 괄호 없이 쉼표만 써도 튜플이 돼요. 괄호는 보기 좋게 묶어 주는 선택 사항입니다. 다만 두 경우에는 괄호가 꼭 필요해요.

- 빈 튜플: `()`처럼 괄호만 쓰거나 `tuple()`로 만듭니다.
- 헷갈릴 수 있는 자리: `f(a, b, c)`는 함수에 값 세 개를 넘기는 것이고, `f((a, b, c))`는 튜플 하나를 넘기는 것입니다.

```python
# 기본 튜플 생성
coordinates = (37.5665, 126.9780)  # 서울 좌표
person = ("김철수", 25, "서울시 강남구")
colors = "빨강", "파랑", "노랑"  # 괄호 생략 가능

# 단일 요소 튜플 (쉼표 필수!)
single = (42,)
single2 = 42,

# 빈 튜플
empty = ()
empty2 = tuple()

print(f"좌표: {coordinates}")
print(f"개인정보: {person}")
print(f"색상들: {colors}")
print(f"단일 요소: {single}, {single2}")
```

> **Q. `(99)`나 `(,)`도 튜플인가요?**
> 아닙니다. 실제로 실행해 보면 `type((99))`는 `<class 'int'>`, 그냥 정수예요. `(,)`는 아예 문법 오류가 납니다. 소괄호는 `2 + 3 * (4 + 2)`처럼 계산 순서를 정하는 기호로도 쓰이기 때문에, 파이썬은 `(99)`를 "99를 먼저 계산하라"로 읽습니다. 그래서 값이 하나뿐인 튜플은 `(99,)` 또는 `99,`처럼 **값 뒤에 쉼표를 붙이는** 것이 규칙이에요. 이상해 보이나요? 최대한 간단한 기호로, 다른 문법과 부딪히지 않게 만들려다 보니 나온 약속입니다. 여러분이라면 어떤 기호를 골랐을지 한번 생각해 보세요.

튜플 안에는 어떤 값이든 들어갈 수 있습니다. 튜플 안에 튜플을 넣을 수도 있어요. `X = (0, (1, (2, (3, (4,)))))`에서 `X[-1][-1][-1][-1]`은 무엇일까요? 마지막 원소의 마지막 원소의 … 를 네 번 따라 들어가면 `(4,)`가 나옵니다.

그럼 "불변"은 정확히 무슨 뜻일까요? `a = ("a", "B", "c")`에서 혼자 대문자인 `a[1]`을 소문자로 바꾸고 싶어도 `a[1] = "b"`는 `TypeError`가 납니다. `del a[0]`으로 원소 하나를 지우는 것도 안 돼요. 한 번 만든 튜플의 원소는 바꾸거나 빼거나 더할 수 없습니다. 물론 `del a`로 튜플 자체를 지우거나, `a = ("a", "b", "c")`처럼 새 튜플을 만들어 이름을 다시 붙이는 건 됩니다. 바꾸고 싶으면 새로 만들어야 한다는 것, 문자열과 똑같죠.

### 튜플 언패킹

튜플에 든 값을 여러 변수에 한꺼번에 나눠 담는 것을 **언패킹(unpacking)** 이라고 합니다. 택배 상자를 풀어 물건을 하나씩 꺼내는 거예요. `x, y = point`라고 쓰면 첫 번째 값은 `x`에, 두 번째 값은 `y`에 들어갑니다. 왼쪽 이름의 개수와 오른쪽 값의 개수가 맞아야 해요.

개수가 정해지지 않은 나머지는 `*`를 붙인 이름 하나로 모두 받을 수 있습니다. `first, second, *rest = scores`에서 `rest`는 남은 값들을 **리스트**로 받아요. 필요 없는 값은 관례적으로 `_`라는 이름으로 받아서 "안 쓴다"는 뜻을 드러냅니다.

```python
# 기본 언패킹
point = (10, 20)
x, y = point
print(f"x={x}, y={y}")

# 여러 값 언패킹
student = ("박영수", 20, "컴퓨터과학과", 3.8)
name, age, major, gpa = student
print(f"{name}({age}세) - {major}, GPA: {gpa}")

# 부분 언패킹 (Python 3.0+)
scores = (95, 87, 92, 78, 88)
first, second, *rest = scores
print(f"1등: {first}, 2등: {second}, 나머지: {rest}")

# 중간 값 무시
data = ("김철수", 25, "서울", "개발자", 5000)
name, age, *_, salary = data
print(f"{name}({age}세) 연봉: {salary}만원")
```

언패킹을 알면 두 변수의 값을 바꾸는 것도 한 줄입니다. 다른 언어에서는 임시 변수를 하나 만들어 세 줄로 하는 일을 파이썬에서는 `a, b = b, a`로 끝내요. 오른쪽의 `b, a`가 먼저 튜플로 묶이고, 그 튜플이 왼쪽의 `a, b`로 풀리기 때문입니다.

### 튜플과 함수

함수가 값을 여러 개 돌려주는 것처럼 보이는 코드를 자주 봅니다. `return "이영희", 22, "경영학과", 3.9`처럼요. 하지만 이건 여러 개를 돌려주는 게 아니라 **튜플 하나**를 돌려주는 것입니다. 쉼표가 튜플을 만든다고 했죠? 받는 쪽에서 언패킹으로 바로 풀어 쓰니 여러 값을 주고받는 것처럼 보일 뿐이에요. 사실 파이썬에서 쉼표로 구분되어 오가는 것은 대부분 튜플입니다.

```python
def get_student_info():
    """학생 정보를 튜플로 반환"""
    return "이영희", 22, "경영학과", 3.9

def calculate_stats(scores):
    """점수 통계를 튜플로 반환"""
    return min(scores), max(scores), sum(scores) / len(scores)

# 함수에서 튜플 반환 받기
student_info = get_student_info()
name, age, major, gpa = get_student_info()  # 직접 언패킹
print(f"학생: {name}, 전공: {major}")

# 통계 계산
test_scores = [85, 92, 78, 96, 87]
min_score, max_score, avg_score = calculate_stats(test_scores)
print(f"최저: {min_score}, 최고: {max_score}, 평균: {avg_score:.1f}")
```

`student_info = get_student_info()`처럼 풀지 않고 받으면 `student_info`에는 `('이영희', 22, '경영학과', 3.9)`라는 튜플이 통째로 들어갑니다. 이렇게 돌려주는 값을 튜플로 묶어 주는 이유는 튜플이 가볍고, 빠르고, 안전하기 때문이에요. 함수가 돌려준 결과를 받는 쪽에서 실수로 고쳐 버릴 걱정이 없죠.

## 6.5 네임드튜플 (namedtuple)

### namedtuple 기본 사용

튜플은 편리하지만 `student[2]`라고 써 놓으면 2번이 전공인지 학점인지 코드만 봐서는 알 수 없습니다. 번호 대신 이름표를 붙이면 좋겠죠? `collections` 모듈의 `namedtuple`은 각 자리에 이름을 붙인 튜플을 만들어 줍니다.

`namedtuple('Student', ['name', 'age', 'major', 'gpa'])`는 "이름, 나이, 전공, 학점 네 칸짜리 튜플 양식"을 만드는 것이고, 그 양식으로 `Student("김철수", 21, …)`처럼 실제 값을 채워 씁니다. 그러면 `student1.major`처럼 이름으로 꺼낼 수 있어요. 여전히 튜플이라서 `student1[0]`처럼 번호로 꺼내도 되고, 불변이라 값을 바꿀 수 없는 것도 같습니다.

```python
from collections import namedtuple

# 학생 정보 namedtuple 정의
Student = namedtuple('Student', ['name', 'age', 'major', 'gpa'])

# 인스턴스 생성
student1 = Student("김철수", 21, "컴퓨터과학과", 3.7)
student2 = Student(name="이영희", age=20, major="경영학과", gpa=3.9)

print(f"학생1: {student1.name}, 전공: {student1.major}")
print(f"학생2: {student2}")

# 튜플처럼 인덱싱도 가능
print(f"첫 번째 필드: {student1[0]}")

# 딕셔너리 변환
student_dict = student1._asdict()
print(f"딕셔너리 형태: {student_dict}")
```

`print(student2)`를 하면 `Student(name='이영희', age=20, …)`처럼 이름표까지 함께 출력되어 디버깅할 때도 편합니다. `_asdict()`는 이름표를 키로 하는 딕셔너리로 바꿔 줘요.

### namedtuple 활용 예제

좌표, 상품 정보처럼 "칸의 구성이 정해져 있고 한 번 만들면 잘 바뀌지 않는" 데이터가 `namedtuple`에 잘 어울립니다. 리스트 컴프리헨션에서 `p.category == "전자제품"`처럼 이름으로 조건을 쓰고, `sorted()`의 `key`에 `lambda p: p.price`를 주어 가격순으로 정렬하는 것을 보세요. `p[1]`이라고 쓴 것보다 훨씬 읽기 쉽습니다.

```python
from collections import namedtuple

# 좌표 시스템
Point = namedtuple('Point', ['x', 'y'])
Rectangle = namedtuple('Rectangle', ['top_left', 'bottom_right'])

# 서울시 주요 지역 좌표
seoul_districts = [
    Point(37.5665, 126.9780),  # 중구 (명동)
    Point(37.5172, 127.0473),  # 강남구 (강남역)
    Point(37.5512, 126.9882),  # 마포구 (홍대)
]

for i, point in enumerate(seoul_districts, 1):
    print(f"지역 {i}: 위도 {point.x}, 경도 {point.y}")

# 제품 정보 관리
Product = namedtuple('Product', ['name', 'price', 'category', 'stock'])

products = [
    Product("삼성 갤럭시", 900000, "전자제품", 50),
    Product("나이키 운동화", 120000, "의류", 30),
    Product("스타벅스 텀블러", 25000, "생활용품", 100),
]

# 카테고리별 분류
electronics = [p for p in products if p.category == "전자제품"]
print(f"전자제품: {electronics}")

# 가격순 정렬
sorted_products = sorted(products, key=lambda p: p.price)
print(f"가격순: {[p.name for p in sorted_products]}")
```

## 6.6 시퀀스 공통 연산

리스트, 튜플, 문자열, `range`는 모두 시퀀스라서 같은 연산을 함께 씁니다. 바꿀 수 있느냐 없느냐와 관계없이 쓸 수 있는 연산들이에요.

| 연산 | 뜻 |
|---|---|
| `x in s`, `x not in s` | `x`가 들어 있는지 |
| `s + t` | 이어 붙이기 |
| `s * n` | `n`번 반복해서 이어 붙이기 |
| `s[i]`, `s[i:j]`, `s[i:j:k]` | 인덱싱, 슬라이싱 |
| `len(s)`, `min(s)`, `max(s)` | 길이, 최솟값, 최댓값 |
| `s.index(x)`, `s.count(x)` | 위치 찾기, 개수 세기 |

같은 종류의 시퀀스끼리는 `==`로 비교할 수도 있습니다. 길이가 같고 같은 자리의 원소가 모두 같아야 `True`예요. 반면 `append`, `remove`, `sort`처럼 내용을 바꾸는 연산은 리스트 같은 가변 시퀀스에서만 됩니다.

### 멤버십 검사

`in`은 4장 조건문에서도 자주 썼죠. 리스트에 쓰면 "이 값과 **똑같은 원소**가 있니?"라고 묻습니다. 그래서 `"밥" in korean_foods`는 `False`예요. "비빔밥"이라는 원소는 있어도 "밥"이라는 원소는 없으니까요. 반면 문자열에 쓰면 부분 문자열을 찾으므로 `"밥" in "비빔밥"`은 `True`입니다. 마지막 예제가 이 둘을 섞어서, 음식 하나하나(문자열)에 "밥"이 들어 있는지 묻습니다.

```python
korean_foods = ["김치", "불고기", "비빔밥", "잡채", "떡볶이"]

# in 연산자
print(f"김치가 있나요? {'김치' in korean_foods}")
print(f"스파게티가 있나요? {'스파게티' in korean_foods}")

# not in 연산자
if "피자" not in korean_foods:
    print("피자는 한국 음식이 아닙니다")

# 부분 문자열 검사
food_with_rice = [food for food in korean_foods if "밥" in food]
print(f"밥이 들어간 음식: {food_with_rice}")
```

### 연결과 반복

`+`와 `*`는 리스트든 튜플이든 원본을 건드리지 않고 **새 시퀀스**를 만듭니다. 튜플도 `+`로 이어 붙일 수 있는 이유예요. 기존 튜플을 바꾸는 게 아니라 새 튜플을 하나 더 만드는 것이니까요. 단, 리스트와 튜플을 섞어 `[1] + (2,)`처럼 더하면 `TypeError`가 납니다. 같은 종류끼리만 이어 붙일 수 있어요.

```python
# 리스트 연결
seoul_districts = ["강남구", "서초구", "송파구"]
busan_districts = ["해운대구", "부산진구", "동래구"]
all_districts = seoul_districts + busan_districts
print(f"모든 구: {all_districts}")

# 튜플 연결
korean_vowels = ("ㅏ", "ㅓ", "ㅗ", "ㅜ")
additional_vowels = ("ㅡ", "ㅣ")
all_vowels = korean_vowels + additional_vowels
print(f"모든 모음: {all_vowels}")

# 반복
emphasis = ["좋아"] * 3
print(f"강조: {emphasis}")

separator = ("=",) * 10
print(f"구분선: {separator}")
```

### 길이와 최대/최소

`len()`, `max()`, `min()`, `sum()`은 시퀀스를 통째로 받아 답 하나를 돌려주는 내장 함수입니다. 5장에서 본 것처럼 반복문을 직접 쓰는 것보다 빠르고 읽기도 쉬워요. 문자열 리스트에 `max()`와 `min()`을 쓰면 사전순으로 비교하고, `key=len`을 주면 길이로 비교합니다.

```python
temperatures = [15, 28, 32, 19, 25, 30, 17]

print(f"측정 횟수: {len(temperatures)}")
print(f"최고 기온: {max(temperatures)}도")
print(f"최저 기온: {min(temperatures)}도")
print(f"총합: {sum(temperatures)}도")
print(f"평균: {sum(temperatures) / len(temperatures):.1f}도")

# 한글에서 최대/최소
korean_words = ["가위", "바위", "보", "사과", "하늘"]
print(f"사전순 첫 번째: {min(korean_words)}")
print(f"사전순 마지막: {max(korean_words)}")
print(f"가장 긴 단어: {max(korean_words, key=len)}")
```

"가장 긴 단어"로 "가위"가 나온 것이 의외인가요? "보"만 한 글자이고 나머지는 모두 두 글자라 길이가 같습니다. 이렇게 기준값이 같은 원소가 여럿이면 `max()`는 **가장 먼저 나온 것**을 돌려줘요.

## 6.7 실무 예제: 학급 성적 관리 시스템

이 장에서 배운 것을 모아 학급 성적을 관리해 봅시다. 이 절의 코드 네 개는 이어지는 하나의 프로그램이라 **차례대로 모두 실행해야** 동작합니다. 앞 블록에서 만든 `students`, `scores`를 뒤 블록에서 그대로 쓰거든요.

### 기본 데이터 구조 설계

데이터를 담을 그릇부터 고릅니다. 학생과 과목처럼 "칸이 정해져 있고 잘 바뀌지 않는" 정보는 `namedtuple`로, 그 묶음 여러 개는 리스트로 담았어요. 학생별 과목 점수는 "이름으로 찾아서 과목으로 찾는" 데이터라 딕셔너리 안에 딕셔너리를 넣었습니다. 딕셔너리는 다음 장에서 자세히 배우지만, 여기서는 `scores["김철수"]["수학"]`처럼 이름표로 값을 꺼낸다는 것만 알면 충분해요.

```python
from collections import namedtuple
from statistics import mean, median

# 학생 정보 구조 정의
Student = namedtuple('Student', ['name', 'student_id', 'grade'])
Subject = namedtuple('Subject', ['name', 'credits'])

# 학생들과 과목 정의
students = [
    Student("김철수", "2023001", 2),
    Student("이영희", "2023002", 2),
    Student("박민수", "2023003", 2),
    Student("최지영", "2023004", 2),
    Student("정수진", "2023005", 2),
]

subjects = [
    Subject("국어", 3),
    Subject("영어", 3),
    Subject("수학", 4),
    Subject("과학", 3),
    Subject("사회", 2),
]

# 성적 데이터 (학생별 과목별 점수)
scores = {
    "김철수": {"국어": 85, "영어": 78, "수학": 92, "과학": 88, "사회": 90},
    "이영희": {"국어": 92, "영어": 95, "수학": 87, "과학": 91, "사회": 89},
    "박민수": {"국어": 78, "영어": 82, "수학": 95, "과학": 85, "사회": 83},
    "최지영": {"국어": 88, "영어": 87, "수학": 89, "과학": 93, "사회": 91},
    "정수진": {"국어": 94, "영어": 89, "수학": 86, "과학": 87, "사회": 92},
}
```

### 성적 분석 함수들

분석 함수들은 이 장의 도구를 고루 씁니다. `statistics` 모듈의 `mean()`과 `median()`으로 평균과 중앙값을 구하고, 과목별 점수는 컴프리헨션으로 모읍니다. 순위를 매길 때는 `(이름, 점수)` 튜플의 리스트를 만든 뒤 `sort(key=lambda x: x[1], reverse=True)`로 두 번째 칸(점수)을 기준으로 내림차순 정렬하고, 슬라이싱 `[:n]`으로 앞의 n명만 잘라 내요.

```python
def calculate_student_average(student_name, scores_dict):
    """개별 학생의 평균 계산"""
    student_scores = list(scores_dict[student_name].values())
    return mean(student_scores)

def calculate_subject_statistics(subject_name, scores_dict):
    """과목별 통계 계산"""
    subject_scores = [scores[subject_name] for scores in scores_dict.values()]
    return {
        "평균": mean(subject_scores),
        "중앙값": median(subject_scores),
        "최고점": max(subject_scores),
        "최저점": min(subject_scores),
        "표준편차": round((sum((x - mean(subject_scores))**2 for x in subject_scores) / len(subject_scores))**0.5, 2)
    }

def get_top_students(scores_dict, n=3):
    """상위 n명 학생 반환"""
    averages = [(name, calculate_student_average(name, scores_dict)) 
                for name in scores_dict.keys()]
    averages.sort(key=lambda x: x[1], reverse=True)
    return averages[:n]

def get_subject_rankings(subject_name, scores_dict):
    """특정 과목 순위 계산"""
    subject_scores = [(name, scores[subject_name]) 
                     for name, scores in scores_dict.items()]
    subject_scores.sort(key=lambda x: x[1], reverse=True)
    return subject_scores
```

### 보고서 생성

보고서 함수는 앞의 분석 함수들을 불러 결과를 표처럼 출력합니다. `for rank, (name, avg) in enumerate(top_students, 1):`에서 5장에서 본 "쌍 안의 쌍" 언패킹이 다시 나오죠. `rankings[0]`을 `winner_name, winner_score`로 풀어 과목별 1등을 꺼내는 것도 튜플 언패킹입니다. `get_grade_letter()`는 4장의 `if-elif` 학점 계산 그대로예요.

```python
def generate_class_report(students, subjects, scores):
    """학급 종합 보고서 생성"""
    print("=" * 50)
    print("학급 성적 종합 보고서")
    print("=" * 50)
    
    # 학생별 평균 성적
    print("\n학생별 평균 성적:")
    print("-" * 30)
    for student in students:
        avg = calculate_student_average(student.name, scores)
        grade_letter = get_grade_letter(avg)
        print(f"{student.name:6} ({student.student_id}): {avg:5.1f}점 ({grade_letter})")
    
    # 과목별 통계
    print("\n과목별 통계:")
    print("-" * 50)
    for subject in subjects:
        stats = calculate_subject_statistics(subject.name, scores)
        print(f"\n{subject.name} (학점: {subject.credits})")
        print(f"  평균: {stats['평균']:5.1f}점")
        print(f"  중앙값: {stats['중앙값']:5.1f}점")
        print(f"  최고점: {stats['최고점']}점")
        print(f"  최저점: {stats['최저점']}점")
        print(f"  표준편차: {stats['표준편차']}")
    
    # 상위 3명 학생
    print("\n상위 3명 학생:")
    print("-" * 25)
    top_students = get_top_students(scores, 3)
    for rank, (name, avg) in enumerate(top_students, 1):
        print(f"{rank}등: {name} ({avg:.1f}점)")
    
    # 각 과목별 1등
    print("\n과목별 1등:")
    print("-" * 25)
    for subject in subjects:
        rankings = get_subject_rankings(subject.name, scores)
        winner_name, winner_score = rankings[0]
        print(f"{subject.name}: {winner_name} ({winner_score}점)")

def get_grade_letter(score):
    """숫자 점수를 등급으로 변환"""
    if score >= 95:
        return "A+"
    elif score >= 90:
        return "A"
    elif score >= 85:
        return "B+"
    elif score >= 80:
        return "B"
    elif score >= 75:
        return "C+"
    elif score >= 70:
        return "C"
    else:
        return "F"

# 보고서 생성 실행
generate_class_report(students, subjects, scores)
```

실행하면 이영희가 평균 90.8점으로 1등입니다. 최지영과 정수진은 둘 다 89.6점으로 동점인데 최지영이 2등으로 나와요. 파이썬의 정렬은 기준값이 같으면 원래 순서를 지키니(안정 정렬), 성적표에 먼저 나온 최지영이 앞에 선 것입니다. 실제 성적 처리라면 동점자를 어떻게 할지 따로 규칙을 정해야겠죠.

### 성적 입력 및 수정 기능

데이터를 바꾸는 함수들입니다. 리스트에는 `append()`로 학생을 더하고, 딕셔너리에는 `scores_dict[이름] = {}`처럼 새 키를 만들어 점수 칸을 준비해요. 이 함수들은 받은 리스트와 딕셔너리를 **직접 고칩니다.** 앞의 Q&A에서 본 것처럼 함수에 넘긴 것은 복사본이 아니라 같은 물건이라, 함수 안에서 `append()`한 결과가 함수 밖의 `students`에도 그대로 남아요. 그래서 마지막에 학생 수가 6명으로 늘어나 있습니다.

```python
def add_new_student(students_list, scores_dict, name, student_id, grade):
    """새 학생 추가"""
    new_student = Student(name, student_id, grade)
    students_list.append(new_student)
    scores_dict[name] = {}
    print(f"[O] {name} 학생이 추가되었습니다.")

def update_score(scores_dict, student_name, subject_name, new_score):
    """점수 수정"""
    if student_name in scores_dict:
        old_score = scores_dict[student_name].get(subject_name, "없음")
        scores_dict[student_name][subject_name] = new_score
        print(f"[O] {student_name}의 {subject_name} 점수가 {old_score} → {new_score}로 변경되었습니다.")
    else:
        print(f"[X] {student_name} 학생을 찾을 수 없습니다.")

def batch_input_scores(scores_dict, student_name, subject_scores):
    """한 학생의 모든 점수 일괄 입력"""
    if student_name not in scores_dict:
        scores_dict[student_name] = {}
    
    for subject, score in subject_scores.items():
        scores_dict[student_name][subject] = score
    
    print(f"[O] {student_name}의 성적이 일괄 입력되었습니다.")

# 사용 예제
print("\n" + "="*50)
print("성적 관리 기능 테스트")
print("="*50)

# 새 학생 추가
add_new_student(students, scores, "한미영", "2023006", 2)

# 점수 수정
update_score(scores, "김철수", "수학", 94)

# 일괄 점수 입력
new_scores = {"국어": 87, "영어": 91, "수학": 89, "과학": 85, "사회": 88}
batch_input_scores(scores, "한미영", new_scores)

# 수정된 보고서 확인
print(f"\n현재 학생 수: {len(students)}명")
print(f"한미영 평균: {calculate_student_average('한미영', scores):.1f}점")
```

## 6.8 성능 최적화와 메모리 관리

### 리스트 vs 튜플 성능 비교

리스트와 튜플은 둘 다 원소를 순서대로 담고, 인덱스로 원하는 원소를 **한 번에** 꺼낼 수 있습니다. 원소가 1억 개인 리스트에서 5천만 번째를 꺼내는 것과 원소가 하나뿐인 리스트에서 0번째를 꺼내는 것이 거의 같은 시간이 걸려요. 아파트 호수를 알면 1층부터 문을 두드리지 않고 바로 찾아가는 것과 같습니다. 이렇게 크기와 상관없이 한 번에 끝나는 것을 O(1)이라고 표기해요. 반대로 인덱스를 모르고 값으로 찾을 때(`in`, `index()`)는 앞에서부터 하나씩 확인해야 하니, 리스트가 두 배 길어지면 시간도 두 배쯤 걸립니다(O(n)).

그런데 왜 비슷한 것을 굳이 둘로 나눠 놓았을까요? 리스트는 언제든 늘어날 수 있으니 **여유 공간을 미리 잡아 둡니다.** `sys.getsizeof()`로 빈 리스트에 원소를 하나씩 `append()`하며 크기를 재 보면, 이 책의 실행 환경에서 원소 1~4개일 때는 88바이트로 그대로이다가 5개째에 120바이트로 한꺼번에 늘어나요. 바로 아래 `memory_comparison()`의 결과에서도 원소 1,000개짜리 리스트(8,856바이트)가 같은 내용의 튜플(8,040바이트)보다 큽니다. 튜플은 크기가 정해져 있으니 딱 필요한 만큼만 쓰죠. 그래서 **바뀔 일이 있으면 리스트, 바뀌면 안 되거나 바뀔 일이 없으면 튜플**을 고르는 것이 기본입니다.

아래 함수는 생성 시간과 접근 시간을 재 봅니다. 실행하려면 마지막 줄의 주석을 푸세요. 결과는 컴퓨터마다 다르고 차이도 크지 않을 수 있으니, 속도보다는 "의도에 맞는 자료형"을 고르는 것이 먼저입니다.

```python
import time

def performance_test():
    """리스트와 튜플의 성능 비교"""
    size = 1000000
    
    # 리스트 생성 시간
    start = time.time()
    test_list = list(range(size))
    list_creation_time = time.time() - start
    
    # 튜플 생성 시간
    start = time.time()
    test_tuple = tuple(range(size))
    tuple_creation_time = time.time() - start
    
    # 인덱스 접근 시간 (리스트)
    start = time.time()
    for _ in range(1000):
        _ = test_list[size // 2]
    list_access_time = time.time() - start
    
    # 인덱스 접근 시간 (튜플)
    start = time.time()
    for _ in range(1000):
        _ = test_tuple[size // 2]
    tuple_access_time = time.time() - start
    
    print("성능 비교 결과:")
    print(f"리스트 생성: {list_creation_time:.6f}초")
    print(f"튜플 생성: {tuple_creation_time:.6f}초")
    print(f"리스트 접근: {list_access_time:.6f}초")
    print(f"튜플 접근: {tuple_access_time:.6f}초")

# 성능 테스트 실행 (주석 해제 시 실행)
# performance_test()
```

### 메모리 효율적인 리스트 사용

5장에서 본 제너레이터를 리스트·튜플과 나란히 놓고 메모리를 비교해 봅시다. 리스트와 튜플은 원소 1,000개를 모두 담고 있으니 8KB 남짓을 쓰지만, 제너레이터는 "다음 값을 어떻게 만들지"만 기억하니 원소 수와 상관없이 크기가 작습니다(이 책의 실행 환경에서 192바이트). 다만 `sys.getsizeof()`는 그릇 자체의 크기만 재고 안에 담긴 원소들의 크기는 더하지 않는다는 점은 알아 두세요. `process_large_dataset()`과 `process_in_chunks()`는 5장의 제너레이터와 청크 처리를 함수로 만들어 둔 것입니다.

```python
import sys

def memory_comparison():
    """메모리 사용량 비교"""
    # 일반 리스트
    normal_list = [i for i in range(1000)]
    
    # 제너레이터 표현식
    generator_expr = (i for i in range(1000))
    
    # 튜플
    tuple_data = tuple(range(1000))
    
    print("메모리 사용량 비교:")
    print(f"리스트: {sys.getsizeof(normal_list)} bytes")
    print(f"제너레이터: {sys.getsizeof(generator_expr)} bytes")
    print(f"튜플: {sys.getsizeof(tuple_data)} bytes")

# 대용량 데이터 처리 최적화
def process_large_dataset(data):
    """대용량 데이터 효율적 처리"""
    # 나쁜 예: 모든 데이터를 메모리에 로드
    # result = [process_item(item) for item in data]
    
    # 좋은 예: 제너레이터 사용
    def process_items():
        for item in data:
            yield process_item(item)
    
    return process_items()

def process_item(item):
    """개별 아이템 처리 (예제)"""
    return item * 2

# 청크 단위 처리
def process_in_chunks(data, chunk_size=1000):
    """데이터를 청크 단위로 처리"""
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        yield [process_item(item) for item in chunk]

# 메모리 비교 실행
memory_comparison()
```

## 6.9 실습 문제

### 기본 문제 (1-5번)

```python
# 1번: 한국 도시 리스트 조작
cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]
# 문제: 인구 순으로 도시를 정렬하고, 상위 3개 도시만 남기세요
# 답:
population_order = ["서울", "부산", "인천", "대구", "대전"]
top3_cities = [city for city in population_order if city in cities][:3]
print(f"상위 3개 도시: {top3_cities}")

# 2번: 학생 점수 튜플 처리
student_scores = ("김철수", 85, 92, 78, 88, 90)
# 문제: 이름과 점수들을 분리하고 평균을 계산하세요
# 답:
name, *scores = student_scores
average = sum(scores) / len(scores)
print(f"{name}의 평균: {average:.1f}점")

# 3번: 중복 제거와 정렬
korean_foods = ["김치", "불고기", "김치", "비빔밥", "불고기", "떡볶이", "김치"]
# 문제: 중복을 제거하고 가나다순으로 정렬하세요
# 답:
unique_foods = list(set(korean_foods))
unique_foods.sort()
print(f"정렬된 음식: {unique_foods}")

# 4번: 리스트 컴프리헨션 활용
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# 문제: 짝수의 제곱만 구하세요
# 답:
even_squares = [n**2 for n in numbers if n % 2 == 0]
print(f"짝수의 제곱: {even_squares}")

# 5번: 튜플 언패킹
coordinates = [(37.5665, 126.9780), (35.1796, 129.0756), (35.8714, 128.6014)]
# 문제: 각 좌표의 위도와 경도를 따로 리스트로 만드세요
# 답:
latitudes = [lat for lat, lng in coordinates]
longitudes = [lng for lat, lng in coordinates]
print(f"위도: {latitudes}")
print(f"경도: {longitudes}")
```

### 중급 문제 (6-10번)

```python
# 6번: 중첩 리스트 처리
class_scores = [
    ["김철수", [85, 92, 78]],
    ["이영희", [95, 87, 91]],
    ["박민수", [78, 95, 85]]
]
# 문제: 각 학생의 이름과 평균 점수로 구성된 리스트를 만드세요
# 답:
student_averages = [(name, sum(scores)/len(scores)) for name, scores in class_scores]
print(f"학생별 평균: {student_averages}")

# 7번: namedtuple 활용
from collections import namedtuple
Book = namedtuple('Book', ['title', 'author', 'year', 'pages'])

books = [
    Book("파이썬 프로그래밍", "김철수", 2023, 350),
    Book("웹 개발 기초", "이영희", 2022, 280),
    Book("데이터 과학", "박민수", 2023, 420)
]
# 문제: 2023년에 출간된 책의 제목을 리스트로 만드세요
# 답:
books_2023 = [book.title for book in books if book.year == 2023]
print(f"2023년 출간 도서: {books_2023}")

# 8번: 리스트 슬라이싱 고급
korean_alphabet = list("가나다라마바사아자차카타파하")
# 문제: 홀수 번째 문자들만 뽑아서 역순으로 정렬하세요
# 답:
odd_chars = korean_alphabet[::2][::-1]
print(f"홀수번째 문자 역순: {odd_chars}")

# 9번: 복잡한 정렬
students_data = [
    ("김철수", 2, 3.7),
    ("이영희", 1, 3.9),
    ("박민수", 2, 3.5),
    ("최지영", 1, 4.0),
    ("정수진", 3, 3.8)
]
# 문제: 학년 우선, 같으면 GPA 높은 순으로 정렬하세요
# 답:
sorted_students = sorted(students_data, key=lambda x: (x[1], -x[2]))
print(f"정렬된 학생: {sorted_students}")

# 10번: 리스트 병합과 중복 처리
list1 = ["사과", "바나나", "오렌지"]
list2 = ["바나나", "포도", "딸기"]
list3 = ["오렌지", "키위", "망고"]
# 문제: 모든 리스트를 합치고 중복을 제거하되, 원래 순서를 보존하세요
# 답:
merged = []
for lst in [list1, list2, list3]:
    for item in lst:
        if item not in merged:
            merged.append(item)
print(f"순서 보존 병합: {merged}")
```

### 고급 문제 (11-15번)

```python
# 11번: 행렬 연산
matrix1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
matrix2 = [[9, 8, 7], [6, 5, 4], [3, 2, 1]]
# 문제: 두 행렬의 원소별 곱셈 결과를 구하세요
# 답:
result_matrix = [[matrix1[i][j] * matrix2[i][j] for j in range(len(matrix1[0]))] 
                 for i in range(len(matrix1))]
print(f"원소별 곱셈 결과: {result_matrix}")

# 12번: 데이터 그룹화
sales_data = [
    ("김철수", "서울", 1500000),
    ("이영희", "부산", 1200000),
    ("박민수", "서울", 1800000),
    ("최지영", "대구", 900000),
    ("정수진", "서울", 1400000),
]
# 문제: 지역별로 매출을 그룹화하고 총합을 계산하세요
# 답:
region_sales = {}
for name, region, sales in sales_data:
    if region not in region_sales:
        region_sales[region] = []
    region_sales[region].append(sales)

region_totals = {region: sum(sales) for region, sales in region_sales.items()}
print(f"지역별 총 매출: {region_totals}")

# 13번: 문자열 리스트 고급 처리
sentences = [
    "파이썬은 강력한 프로그래밍 언어입니다",
    "리스트와 튜플은 중요한 자료구조입니다", 
    "함수형 프로그래밍도 지원합니다"
]
# 문제: 각 문장에서 5글자 이상인 단어만 추출하세요
# 답:
long_words = []
for sentence in sentences:
    words = sentence.split()
    long_words.extend([word for word in words if len(word) >= 5])
print(f"5글자 이상 단어: {long_words}")

# 14번: 리스트 평탄화 (Flattening)
nested_list = [[1, 2, [3, 4]], [5, [6, 7, [8, 9]]], [10]]
# 문제: 중첩된 리스트를 완전히 평탄화하세요
# 답:
def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

flattened = flatten(nested_list)
print(f"평탄화된 리스트: {flattened}")

# 15번: 복합 데이터 구조 분석
company_data = [
    {
        "부서": "개발팀",
        "직원": [
            ("김철수", "시니어", 5500),
            ("이영희", "주니어", 3500),
            ("박민수", "시니어", 6000)
        ]
    },
    {
        "부서": "마케팅팀", 
        "직원": [
            ("최지영", "매니저", 7500),
            ("정수진", "주니어", 3000)
        ]
    }
]
# 문제: 부서별 평균 연봉을 계산하고, 가장 높은 부서를 찾으세요
# 답:
dept_averages = {}
for dept_info in company_data:
    dept_name = dept_info["부서"]
    salaries = [salary for _, _, salary in dept_info["직원"]]
    dept_averages[dept_name] = sum(salaries) / len(salaries)

highest_avg_dept = max(dept_averages.items(), key=lambda x: x[1])
print(f"부서별 평균 연봉: {dept_averages}")
print(f"평균 연봉이 가장 높은 부서: {highest_avg_dept[0]} ({highest_avg_dept[1]:.0f}만원)")
```

## 6.10 다음 장 미리보기

다음 Chapter 7에서는 **딕셔너리와 집합**을 학습합니다:

### 주요 내용 미리보기
- **딕셔너리**: 키-값 쌍을 통한 데이터 저장과 검색
- **딕셔너리 메서드**: keys(), values(), items(), get(), pop() 등
- **딕셔너리 컴프리헨션**: 효율적인 딕셔너리 생성
- **집합(Set)**: 중복 없는 데이터 모음과 집합 연산
- **집합 연산**: 합집합, 교집합, 차집합, 여집합
- **실무 프로젝트**: 한국어 단어 빈도 분석 시스템

### 연결 포인트
- 리스트와 튜플의 순서 있는 데이터 → 딕셔너리의 키-값 매핑
- 시퀀스 자료형 → 비시퀀스 자료형(딕셔너리, 집합)
- 인덱스 기반 접근 → 키 기반 접근

리스트와 튜플을 마스터했다면, 이제 더욱 유연하고 강력한 딕셔너리와 집합을 활용해 복잡한 데이터를 효율적으로 처리할 준비가 되었습니다!

---

> **학습 팁**: 리스트는 순서가 중요하고 수정 가능한 데이터에, 튜플은 불변하고 구조적인 데이터에 사용하세요. namedtuple은 가독성이 중요한 구조화된 데이터에 매우 유용합니다.

**다음 장에서 만나요!** 