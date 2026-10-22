# 부록 D. 자주 만나는 오류와 해결

빨간 글씨가 화면을 가득 채우면 덜컥 겁이 나죠. 그런데 오류 메시지는 파이썬이 화를 내는 게 아니라 **어디가 왜 이상한지 적어 준 쪽지**입니다. 이 부록은 처음 파이썬을 배우는 사람이 실제로 가장 자주 만나는 오류들을 모아, 메시지 원문과 뜻, 흔한 원인, 고치는 법을 짝지어 둔 것이에요. 오류가 나면 마지막 줄의 오류 이름으로 여기서 찾아보세요. 메시지를 읽는 요령부터 알고 싶다면 맨 끝의 D.8절을 먼저 읽어도 좋습니다.

모든 메시지는 Python 3.12(`uv run python main.py`)에서 실제로 실행해 나온 출력을 그대로 옮겼습니다. 다만 파일 경로는 `main.py`로 줄였어요. 버전이 다르면 문구가 조금 다를 수 있습니다(부록 C).

---

## D.1 한눈에 찾기

| 오류 이름 | 한 줄 뜻 | 절 |
|---|---|---|
| `IndentationError`, `TabError` | 들여쓰기가 맞지 않음 | D.2 |
| `SyntaxError` | 문법이 틀려서 실행을 시작조차 못 함 | D.2 |
| `NameError`, `UnboundLocalError` | 그런 이름이 (아직) 없음 | D.3 |
| `TypeError` | 그 자료형으로는 그 일을 할 수 없음 | D.4 |
| `AttributeError` | 그 객체에 그런 속성·메서드가 없음 | D.4 |
| `IndexError`, `KeyError` | 그런 번호·키가 없음 | D.5 |
| `ValueError` | 자료형은 맞는데 값이 이상함 | D.5 |
| `ZeroDivisionError` | 0으로 나눔 | D.5 |
| `RuntimeError` | 반복 중에 딕셔너리 크기를 바꿈 | D.5 |
| `ModuleNotFoundError` | 그런 모듈을 찾을 수 없음 | D.6 |
| `FileNotFoundError` | 그런 파일이 없음(작업 폴더 확인) | D.6 |
| `UnicodeDecodeError` | 파일 인코딩이 다름 | D.6 |
| `RecursionError` | 재귀가 끝나지 않음 | D.6 |
| 오류는 없는데 결과가 이상함 | 무한 루프, 가변 기본 인자, 얕은 복사, 부동소수 비교 | D.7 |

## D.2 들여쓰기와 문법 오류

이 무리의 오류는 프로그램이 **한 줄도 실행되기 전에** 납니다. 파이썬이 파일을 읽다가 문법에 맞지 않는 곳을 만나면 바로 멈추기 때문이에요. 그래서 트레이스백 첫 줄에 `Traceback (most recent call last):`가 없고, 파일 이름과 줄 번호부터 나옵니다.

### 1. IndentationError: expected an indented block

```python
if True:
print('hi')
```

```text
  File "main.py", line 2
    print('hi')
    ^^^^^
IndentationError: expected an indented block after 'if' statement on line 1
```

- **뜻**: 1번 줄의 `if` 다음에는 들여 쓴 블록이 와야 하는데 없습니다.
- **흔한 원인**: 콜론(`:`)으로 끝나는 줄(`if`, `for`, `while`, `def`, `class`, `with`, `try`) 다음 줄을 들여 쓰지 않음.
- **고치는 법**: 블록 안의 줄을 공백 4칸 들여 씁니다. 아직 쓸 내용이 없으면 `pass`를 넣어 두세요.
- **관련 장**: 4장(조건문), 5장(반복문)

### 2. IndentationError: unexpected indent

```python
x = 1
    print(x)
```

```text
  File "main.py", line 2
    print(x)
IndentationError: unexpected indent
```

- **뜻**: 들여 쓸 이유가 없는 곳이 들여 쓰여 있습니다.
- **흔한 원인**: 인터넷에서 코드를 복사해 붙이다가 앞에 공백이 딸려 옴. 블록이 끝났는데 들여쓰기를 그대로 둠.
- **고치는 법**: 그 줄의 앞 공백을 위 줄과 맞춥니다.

### 3. IndentationError: unindent does not match / TabError

```python
if True:
        a = 1
    b = 2
```

```text
  File "main.py", line 3
    b = 2
         ^
IndentationError: unindent does not match any outer indentation level
```

```text
  File "main.py", line 3
    y = 2
TabError: inconsistent use of tabs and spaces in indentation
```

- **뜻**: 내어 쓴 줄의 칸 수가 바깥 어느 블록과도 맞지 않습니다. `TabError`는 탭과 공백이 섞였다는 뜻이에요.
- **흔한 원인**: 들여쓰기를 8칸, 4칸으로 들쭉날쭉 씀. 메모장 같은 편집기에서 탭 키를 누름.
- **고치는 법**: 들여쓰기는 **공백 4칸**으로 통일합니다. VS Code 같은 편집기는 탭 키를 공백 4칸으로 바꿔 줘요. 오른쪽 아래 상태 표시줄에서 `Spaces: 4`인지 확인하세요.

### 4. SyntaxError: expected ':'

```python
for i in range(3)
    print(i)
```

```text
  File "main.py", line 1
    for i in range(3)
                     ^
SyntaxError: expected ':'
```

- **뜻**: 콜론이 있어야 할 자리에 없습니다. `^`가 그 자리를 가리켜요.
- **고치는 법**: `for i in range(3):`처럼 줄 끝에 `:`를 붙입니다.
- **관련 장**: 4장, 5장

### 5. SyntaxError: '(' was never closed

```python
print('합계:', sum([1, 2, 3])
x = 1
```

```text
  File "main.py", line 1
    print('합계:', sum([1, 2, 3])
         ^
SyntaxError: '(' was never closed
```

- **뜻**: 연 괄호를 닫지 않았습니다. `^`는 짝을 못 찾은 **여는** 괄호를 가리킵니다.
- **흔한 원인**: 괄호가 여러 겹일 때 닫는 괄호 하나를 빠뜨림.
- **고치는 법**: 여는 괄호와 닫는 괄호의 개수를 세어 봅니다. 편집기에서 괄호에 커서를 두면 짝이 되는 괄호가 강조돼요. 괄호 오류는 **다음 줄**을 가리키는 경우도 있으니, 표시된 줄이 멀쩡해 보이면 바로 위 줄을 의심하세요.

### 6. SyntaxError: unterminated string literal

```python
msg = '안녕하세요
print(msg)
```

```text
  File "main.py", line 1
    msg = '안녕하세요
          ^
SyntaxError: unterminated string literal (detected at line 1)
```

- **뜻**: 문자열을 열었는데 닫는 따옴표가 없습니다.
- **고치는 법**: 같은 종류의 따옴표로 닫습니다. 여러 줄 문자열이 필요하면 `'''...'''`나 `"""..."""`를 쓰세요.
- **관련 장**: 2장

### 7. SyntaxError: invalid syntax. Maybe you meant '=='

```python
x = 3
if x = 3:
    print(x)
```

```text
  File "main.py", line 2
    if x = 3:
       ^^^^^
SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
```

- **뜻**: 조건 자리에 할당 `=`를 썼습니다.
- **고치는 법**: 비교는 `==`입니다. `=`는 "담아라", `==`는 "같으냐?"예요. 파이썬이 고칠 방법까지 추천해 주죠.
- **관련 장**: 3장 3.2, 3.3

### 8. SyntaxError: invalid character

```python
print(1，2)
print(“안녕”)
```

```text
  File "main.py", line 1
    print(1，2)
           ^
SyntaxError: invalid character '，' (U+FF0C)
```

```text
  File "main.py", line 1
    print(“안녕”)
          ^
SyntaxError: invalid character '“' (U+201C)
```

- **뜻**: 파이썬 문법에 없는 글자가 코드에 들어 있습니다.
- **흔한 원인**: 한글 입력 상태에서 쉼표·괄호를 쳐서 **전각 문자**(`，`, `（`)가 들어감. 워드프로세서나 메신저에서 복사한 코드의 **둥근 따옴표**(`“ ”`, `‘ ’`).
- **고치는 법**: 영문 입력 상태로 바꾸고 그 글자를 다시 칩니다. 눈으로 구분이 어려우니 메시지의 `U+FF0C` 같은 코드 번호를 믿으세요. 코드는 메모장이나 코드 편집기에서 복사하는 습관을 들이면 이 오류가 사라집니다.

## D.3 이름 오류

### 9. NameError: name '...' is not defined (오타)

```python
pirnt('hi')
```

```text
Traceback (most recent call last):
  File "main.py", line 1, in <module>
    pirnt('hi')
    ^^^^^
NameError: name 'pirnt' is not defined. Did you mean: 'print'?
```

- **뜻**: `pirnt`라는 이름이 어디에도 없습니다.
- **흔한 원인**: 오타, 대소문자 틀림(`Print`, `true`), 변수 이름을 중간에 바꿈, `import`를 빠뜨림.
- **고치는 법**: `Did you mean:` 뒤의 추천을 먼저 보세요. `import`를 빠뜨렸으면 3.12는 `Did you forget to import 'sys'?`처럼 알려 줍니다(부록 C.6).
- **관련 장**: 2장(변수 이름 규칙)

### 10. NameError: 정의하기 전에 사용

```python
greet('민수')
def greet(name):
    print(name)
```

```text
Traceback (most recent call last):
  File "main.py", line 1, in <module>
    greet('민수')
    ^^^^^
NameError: name 'greet' is not defined
```

- **뜻**: 1번 줄을 실행하는 순간에는 `greet`가 아직 만들어지지 않았습니다.
- **흔한 원인**: 파이썬은 위에서 아래로 한 줄씩 실행합니다. `def`도 "함수를 만드는" 실행문이라, 그 줄에 도착해야 함수가 생겨요.
- **고치는 법**: 함수 정의를 호출보다 위로 옮깁니다. 보통은 함수 정의를 모두 위에 두고, 실행 코드는 맨 아래 `if __name__ == "__main__":` 안에 둡니다(14장).
- **관련 장**: 9장 9.1

### 11. UnboundLocalError

```python
count = 0
def inc():
    count += 1
inc()
```

```text
Traceback (most recent call last):
  File "main.py", line 4, in <module>
    inc()
  File "main.py", line 3, in inc
    count += 1
    ^^^^^
UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

- **뜻**: 함수 안의 `count`는 지역 변수인데, 값을 받기 전에 읽으려 했습니다.
- **흔한 원인**: 함수 안에서 바깥 변수에 **할당**(`=`, `+=`)을 하면, 파이썬은 그 이름을 함수 안의 새 지역 변수로 봅니다. `count += 1`은 `count = count + 1`이라 오른쪽의 `count`를 읽을 수가 없어요.
- **고치는 법**: 값을 인자로 받고 결과를 `return`하는 것이 가장 좋습니다. 꼭 바깥 변수를 바꿔야 하면 `global count`(모듈 변수)나 `nonlocal count`(감싼 함수의 변수)를 선언합니다.
- **관련 장**: 9장 9.2, 10장 10.5

## D.4 자료형 오류

### 12. TypeError: can only concatenate str (not "int") to str

```python
age = 20
print('나이: ' + age)
```

```text
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    print('나이: ' + age)
          ~~~~~~~~~^~~~~
TypeError: can only concatenate str (not "int") to str
```

- **뜻**: 문자열에는 문자열만 이어 붙일 수 있는데 정수를 붙이려 했습니다.
- **고치는 법**: f-string을 쓰는 것이 가장 깔끔합니다. `print(f'나이: {age}')`. 또는 `'나이: ' + str(age)`.
- **관련 장**: 2장, 3장(들어가며)

### 13. TypeError: unsupported operand type(s) for +: 'int' and 'str'

```python
n = '5'
print(10 + n)
```

```text
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    print(10 + n)
          ~~~^~~
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

- **뜻**: 정수와 문자열은 더할 수 없습니다.
- **흔한 원인**: `input()`은 사용자가 숫자를 쳐도 **항상 문자열**을 돌려줍니다. 파일에서 읽은 값도 문자열이에요.
- **고치는 법**: `int(n)`이나 `float(n)`으로 바꾼 다음 계산합니다. `n = int(input("숫자: "))`.
- **관련 장**: 2장 2.5

### 14. TypeError: missing 1 required positional argument

```python
def greet(name):
    print(name)
greet()
```

```text
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    greet()
TypeError: greet() missing 1 required positional argument: 'name'
```

- **뜻**: `name` 인자를 꼭 넘겨야 하는데 빠졌습니다. 반대로 너무 많이 넘기면 `takes 1 positional argument but 2 were given`이 나와요.
- **고치는 법**: 함수 정의(`def` 줄)와 호출의 인자 개수를 맞춥니다. 생략해도 되게 하려면 `def greet(name="손님"):`처럼 기본값을 둡니다.
- **관련 장**: 9장 9.1

### 15. TypeError: takes 1 positional argument but 2 were given (메서드)

```python
class Dog:
    def bark(sound):
        print(sound)
Dog().bark('멍')
```

```text
Traceback (most recent call last):
  File "main.py", line 4, in <module>
    Dog().bark('멍')
TypeError: Dog.bark() takes 1 positional argument but 2 were given
```

- **뜻**: 인자를 하나(`'멍'`)만 넘겼는데 "2개를 받았다"고 합니다. 메서드를 부르면 객체 자신이 첫 번째 인자로 자동으로 들어가기 때문이에요.
- **고치는 법**: 메서드의 첫 매개변수로 `self`를 씁니다. `def bark(self, sound):`.
- **관련 장**: 11장 11.1

### 16. TypeError: 'NoneType' object is not subscriptable

```python
nums = [3, 1, 2]
sorted_nums = nums.sort()
print(sorted_nums[0])
```

```text
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    print(sorted_nums[0])
          ~~~~~~~~~~~^^^
TypeError: 'NoneType' object is not subscriptable
```

- **뜻**: `None`에 `[0]`을 하려 했습니다. `~~~` 밑줄 부분(`sorted_nums`)이 `None`이었다는 뜻이에요.
- **흔한 원인**: `sort()`, `append()`, `reverse()`처럼 **원본을 바꾸는 메서드는 `None`을 돌려줍니다**. 그 결과를 변수에 담음. 또는 `return`을 빠뜨린 함수의 결과(`None`)를 씀.
- **고치는 법**: 정렬한 새 리스트가 필요하면 `sorted(nums)`, 원본을 정렬하려면 `nums.sort()`만 쓰고 `nums`를 씁니다. 함수라면 `return`이 있는지 확인하세요.
- **관련 장**: 6장 6.2

### 17. AttributeError: 'NoneType' object has no attribute 'append'

```python
items = []
items = items.append(1)
items.append(2)
```

```text
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    items.append(2)
    ^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'append'
```

- **뜻**: `items`가 `None`이 되어서 `append`를 찾을 수 없습니다.
- **흔한 원인**: 16번과 같은 실수입니다. `items.append(1)`의 결과 `None`을 다시 `items`에 담았어요. 딕셔너리 `get()`이 키가 없어서 `None`을 돌려준 경우도 많습니다.
- **고치는 법**: `items.append(1)`만 씁니다. `None`이 들어올 수 있는 값은 `if x is not None:`으로 먼저 확인하세요.
- **관련 장**: 6장, 7장 7.2

### 18. AttributeError: 'str' object has no attribute ...

```python
s = 'hello'
s.push('!')
```

```text
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    s.push('!')
    ^^^^^^
AttributeError: 'str' object has no attribute 'push'
```

- **뜻**: 문자열에는 `push`라는 메서드가 없습니다.
- **흔한 원인**: 다른 언어의 메서드 이름을 씀(`push` 대신 `append`, `length` 대신 `len()`). 자료형을 착각함(리스트인 줄 알았는데 문자열).
- **고치는 법**: `type(s)`로 자료형을 확인하고, `dir(s)`로 쓸 수 있는 메서드 목록을 봅니다. 문자열은 바뀌지 않으므로 `s = s + '!'`처럼 새로 만들어요.
- **관련 장**: 2장, 6장, 부록 B.3

### 19. TypeError: 'str' object does not support item assignment

```python
s = 'hello'
s[0] = 'H'
```

```text
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    s[0] = 'H'
    ~^^^
TypeError: 'str' object does not support item assignment
```

- **뜻**: 문자열(그리고 튜플)은 한번 만들면 바꿀 수 없습니다.
- **고치는 법**: 새 문자열을 만듭니다. `s = 'H' + s[1:]` 또는 `s.replace('h', 'H', 1)`.
- **관련 장**: 2장, 6장 6.4(튜플)

### 20. TypeError: unhashable type: 'list'

```python
seen = {[1, 2]}
```

```text
Traceback (most recent call last):
  File "main.py", line 1, in <module>
    seen = {[1, 2]}
           ^^^^^^^^
TypeError: unhashable type: 'list'
```

- **뜻**: 리스트는 바뀔 수 있어서 집합의 원소나 딕셔너리의 키가 될 수 없습니다.
- **고치는 법**: 바뀌지 않는 튜플로 바꿉니다. `seen = {(1, 2)}`.
- **관련 장**: 7장

### 21. TypeError: 'int' object is not callable / is not iterable

```text
TypeError: 'int' object is not callable
TypeError: 'int' object is not iterable
```

- **뜻**: 첫째는 정수를 함수처럼 `()`로 불렀다는 뜻, 둘째는 정수를 `for`로 돌리려 했다는 뜻입니다.
- **흔한 원인**: `sum = 0`처럼 **내장 함수 이름을 변수로 덮어써서** 나중에 `sum([1, 2])`가 `'int' object is not callable`을 냄. `for i in 10:`처럼 `range()`를 빠뜨림.
- **고치는 법**: `list`, `sum`, `max`, `str`, `input` 같은 이름은 변수로 쓰지 않습니다. 반복은 `for i in range(10):`.
- **관련 장**: 2장, 14장 14.1, 5장 5.1

## D.5 값과 범위 오류

### 22. IndexError: list index out of range

```python
fruits = ['사과', '배', '귤']
print(fruits[3])
```

```text
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    print(fruits[3])
          ~~~~~~^^^
IndexError: list index out of range
```

- **뜻**: 원소가 3개면 번호는 `0`, `1`, `2`까지인데 `3`을 찾았습니다.
- **흔한 원인**: 번호가 0부터 시작한다는 것을 잊음. `range(len(lst) + 1)`처럼 한 번 더 돎. 빈 리스트에서 `lst[0]`.
- **고치는 법**: 마지막 원소는 `fruits[-1]`로 꺼냅니다. 번호가 필요 없으면 `for fruit in fruits:`처럼 원소를 바로 돌고, 필요하면 `enumerate()`를 씁니다. 빈 리스트일 수 있으면 `if fruits:`로 먼저 확인하세요.
- **관련 장**: 6장 6.1

### 23. KeyError

```python
person = {'name': '민수'}
print(person['age'])
```

```text
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    print(person['age'])
          ~~~~~~^^^^^^^
KeyError: 'age'
```

- **뜻**: 딕셔너리에 `'age'`라는 키가 없습니다. 메시지에는 없는 **키 자체**만 나와요.
- **흔한 원인**: 키 오타, 대소문자 차이(`'Name'`과 `'name'`), 숫자 `1`과 문자열 `'1'`의 차이.
- **고치는 법**: 없을 수도 있는 키는 `person.get('age', 0)`이나 `if 'age' in person:`으로 다룹니다. 모으는 용도라면 `defaultdict`가 편해요.
- **관련 장**: 7장 7.1, 8장 8.4

### 24. ValueError: invalid literal for int()

```python
print(int('3.5'))
```

```text
Traceback (most recent call last):
  File "main.py", line 1, in <module>
    print(int('3.5'))
          ^^^^^^^^^^
ValueError: invalid literal for int() with base 10: '3.5'
```

- **뜻**: 자료형(문자열)은 맞는데, 그 내용이 정수로 읽을 수 없는 값입니다.
- **흔한 원인**: 소수가 든 문자열, 빈 문자열 `''`, 앞뒤 공백이 아닌 다른 글자(`'1,000'`, `'10원'`).
- **고치는 법**: 소수면 `int(float('3.5'))`, 쉼표가 있으면 `'1,000'.replace(',', '')`. 사용자 입력은 `try`-`except ValueError`로 감싸서 다시 묻는 것이 정석입니다.
- **관련 장**: 2장, 12장 12.3

### 25. ValueError: too many values to unpack

```python
a, b = [1, 2, 3]
```

```text
Traceback (most recent call last):
  File "main.py", line 1, in <module>
    a, b = [1, 2, 3]
    ^^^^
ValueError: too many values to unpack (expected 2)
```

- **뜻**: 변수는 2개인데 값이 3개입니다. 반대로 값이 모자라면 `not enough values to unpack`이 나와요.
- **흔한 원인**: 딕셔너리를 `for k, v in d:`로 돌림(`d.items()`를 빠뜨림). `split()` 결과의 개수가 예상과 다름.
- **고치는 법**: 개수를 맞추거나 `a, *rest = [1, 2, 3]`처럼 나머지를 받습니다. 딕셔너리는 `for k, v in d.items():`.
- **관련 장**: 6장, 7장

### 26. ZeroDivisionError: division by zero

```python
scores = []
print(sum(scores) / len(scores))
```

```text
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    print(sum(scores) / len(scores))
          ~~~~~~~~~~~~^~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

- **뜻**: 0으로 나눴습니다. `^` 표시가 `/`를 가리키죠.
- **흔한 원인**: 빈 리스트의 평균. 사용자가 0을 입력함.
- **고치는 법**: 나누기 전에 확인합니다. `avg = sum(scores) / len(scores) if scores else 0`.
- **관련 장**: 3장 3.1, 12장 12.3

### 27. RuntimeError: dictionary changed size during iteration

```python
d = {'a': 1, 'b': 2}
for k in d:
    if d[k] == 1:
        del d[k]
```

```text
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    for k in d:
             ^
RuntimeError: dictionary changed size during iteration
```

- **뜻**: 딕셔너리를 돌리는 도중에 원소를 지우거나 더했습니다.
- **고치는 법**: 키 목록을 복사해서 돌리거나(`for k in list(d):`), 남길 것만 모아 새로 만듭니다. `d = {k: v for k, v in d.items() if v != 1}`. 리스트도 돌면서 지우면 오류 없이 원소를 **건너뛰는** 버그가 생기니 같은 방법을 쓰세요.
- **관련 장**: 7장 7.3

## D.6 모듈, 파일, 재귀

### 28. ModuleNotFoundError: No module named '...'

```python
import requests
```

```text
Traceback (most recent call last):
  File "main.py", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

- **뜻**: 지금 실행 중인 파이썬 환경에서 그 모듈을 찾을 수 없습니다.
- **흔한 원인**: 외부 라이브러리를 설치하지 않음. 설치는 했는데 **다른 파이썬**으로 실행함(예: `uv add`로 프로젝트의 `.venv`에 넣고 `python main.py`로 실행). 내 파일 이름이 모듈 이름과 같음.
- **고치는 법**: 프로젝트 폴더에서 `uv add requests`로 설치하고 `uv run python main.py`로 실행합니다. 설치 이름과 import 이름이 다른 경우도 있어요(`uv add pillow` → `import PIL`, `uv add scikit-learn` → `import sklearn`, `uv add python-docx` → `import docx`). 내 모듈인데 못 찾는다면 실행하는 폴더와 `sys.path`를 확인하세요.
- **관련 장**: 14장 14.7, 14.8, 부록 A

> **Q. 파일 이름을 `random.py`로 했더니 `random.randint`가 없대요.**
> `import random`이 표준 라이브러리 대신 **내 파일 자신**을 불러온 것입니다. 3.12에서는 `AttributeError: partially initialized module 'random' has no attribute 'randint' (most likely due to a circular import)`가 나와요. 파일 이름을 `my_random.py`처럼 바꾸고, 같은 폴더에 생긴 `__pycache__` 폴더도 지우세요. 14장 14.1에서 다룬 실수입니다.

### 29. FileNotFoundError

```python
open('data.txt', encoding='utf-8')
```

```text
Traceback (most recent call last):
  File "main.py", line 1, in <module>
    open('data.txt', encoding='utf-8')
FileNotFoundError: [Errno 2] No such file or directory: 'data.txt'
```

- **뜻**: 그 경로에 파일이 없습니다.
- **흔한 원인**: 파일 이름 오타나 확장자(`data.txt.txt`). 가장 흔한 것은 **작업 폴더** 문제입니다. `'data.txt'`처럼 상대 경로를 쓰면 파이썬은 **스크립트가 있는 폴더가 아니라 터미널에서 실행한 폴더**를 기준으로 찾아요. 편집기의 실행 버튼은 다른 폴더에서 실행할 수도 있습니다.
- **고치는 법**: `from pathlib import Path; print(Path.cwd())`로 지금 작업 폴더를 확인합니다. 스크립트 옆의 파일을 늘 찾으려면 스크립트 위치를 기준으로 경로를 만드세요.

```python
from pathlib import Path

BASE = Path(__file__).parent        # 이 스크립트가 있는 폴더
data_file = BASE / "data.txt"
print(data_file.exists())
```

- **관련 장**: 12장 12.1, 12.2

### 30. UnicodeDecodeError

```python
# 윈도우 메모장 등에서 CP949로 저장된 파일을 UTF-8로 읽음
print(open('cp949.txt', encoding='utf-8').read())
```

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xbe in position 0: invalid start byte
```

반대로 UTF-8 파일을 CP949로 읽으면(윈도우에서 `encoding`을 생략했을 때 흔함) 이렇게 나옵니다.

```text
UnicodeDecodeError: 'cp949' codec can't decode byte 0xec in position 0: illegal multibyte sequence
```

- **뜻**: 파일을 저장할 때 쓴 인코딩과 읽을 때 쓴 인코딩이 다릅니다. 같은 "안"이라도 UTF-8은 3바이트, CP949(EUC-KR 확장)는 2바이트로 저장해서 서로 읽지 못해요.
- **흔한 원인**: 오래된 윈도우 프로그램이나 엑셀이 만든 한글 CSV는 CP949인 경우가 많음. 윈도우에서 `encoding`을 생략하면 기본값이 CP949가 됨.
- **고치는 법**: 파일을 열 때 **늘 `encoding`을 적습니다**. 내가 만드는 파일은 `encoding='utf-8'`, 남에게 받은 한글 파일이 이 오류를 내면 `encoding='cp949'`로 다시 읽어 보세요. 엑셀에서 열 CSV를 쓸 때는 `encoding='utf-8-sig'`가 한글 깨짐을 막아 줍니다.
- **관련 장**: 12장 12.1, 12.5

### 31. RecursionError: maximum recursion depth exceeded

```python
def countdown(n):
    print(n)
    countdown(n - 1)
countdown(3)
```

```text
3
2
1
0
-1
...
  File "main.py", line 3, in countdown
    countdown(n - 1)
  [Previous line repeated 996 more times]
RecursionError: maximum recursion depth exceeded
```

- **뜻**: 함수가 자기 자신을 너무 깊이 불렀습니다. 파이썬은 기본으로 1000단계쯤에서 멈춰요(`sys.getrecursionlimit()`은 `1000`).
- **흔한 원인**: **종료 조건**을 빠뜨림. 위 예는 `0`에서 멈춰야 하는데 음수로 끝없이 내려갔어요. 종료 조건이 있어도 도달하지 못하는 경우(`n - 2`로 줄이는데 홀수가 들어옴)도 있습니다.
- **고치는 법**: 맨 앞에 `if n <= 0: return` 같은 종료 조건을 둡니다. 정말 깊은 계산이라면 반복문으로 바꾸는 편이 안전해요.
- **관련 장**: 9장 9.3

## D.7 오류는 안 나는데 결과가 이상할 때

가장 무서운 버그는 오류 메시지가 **없는** 버그입니다. 프로그램은 잘 도는데 답이 틀리거든요. 초보자가 가장 자주 빠지는 함정 다섯 가지입니다.

### 32. 무한 루프

```python
count = 0
while count < 5:
    print("반복 중")
```

`count`를 늘리는 줄이 없어서 조건이 영원히 참입니다. 화면에 "반복 중"이 끝없이 올라가요(0.5초 만에 5천 줄이 넘게 찍혔습니다). 이럴 때는 당황하지 말고 **Ctrl+C**를 누르세요. 프로그램이 멈추면서 이렇게 나옵니다.

```text
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    print("반복 중")
KeyboardInterrupt
```

- **고치는 법**: `while`문 안에서 조건에 쓰인 변수가 바뀌는지 확인합니다(`count += 1`). 횟수가 정해져 있으면 `for _ in range(5):`가 더 안전해요. `while True:`를 쓸 때는 `break`로 빠져나갈 길이 꼭 있어야 합니다.
- **관련 장**: 5장 5.2

### 33. 가변 기본 인자 함정

```python
def add_item(item, box=[]):
    box.append(item)
    return box

print(add_item("사과"))   # ['사과']
print(add_item("배"))     # ['사과', '배']
```

두 번째 호출은 `['배']`를 기대했는데 `'사과'`가 남아 있습니다. 기본값 `[]`는 함수를 **정의할 때 딱 한 번** 만들어지고, 그 뒤로는 모든 호출이 같은 리스트를 함께 쓰기 때문이에요.

```python
def add_item(item, box=None):
    if box is None:
        box = []              # 부를 때마다 새 리스트
    box.append(item)
    return box

print(add_item("사과"), add_item("배"))  # ['사과'] ['배']
```

- **고치는 법**: 리스트·딕셔너리·집합처럼 바뀌는 값은 기본값으로 쓰지 말고 `None`을 기본값으로 둔 뒤 함수 안에서 만듭니다. 데이터 클래스에서는 `field(default_factory=list)`를 씁니다.
- **관련 장**: 9장 9.1(기본값 인자), 8장 8.1(`default_factory`)

### 34. 얕은 복사 함정

```python
board = [[0] * 3] * 3
board[0][0] = 1
print(board)   # [[1, 0, 0], [1, 0, 0], [1, 0, 0]]
```

한 칸만 바꿨는데 세 줄이 모두 바뀌었습니다. `* 3`은 안쪽 리스트를 세 번 **복사**한 게 아니라, 같은 리스트에 이름표를 세 번 붙인 거예요. `copy()`도 비슷한 함정이 있습니다.

```python
import copy

a = [[1, 2], [3, 4]]
b = a.copy()          # 바깥 리스트만 새로, 안쪽은 공유 (얕은 복사)
b[0].append(99)
print(a)              # [[1, 2, 99], [3, 4]]

c = copy.deepcopy(a)  # 안쪽까지 모두 새로 (깊은 복사)
c[0].append(100)
print(a)              # [[1, 2, 99], [3, 4]]

board = [[0] * 3 for _ in range(3)]   # 줄마다 새 리스트
board[0][0] = 1
print(board)          # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
```

- **고치는 법**: 2차원 리스트는 컴프리헨션으로 만듭니다. 중첩된 자료를 통째로 복사하려면 `copy.deepcopy()`를 씁니다. `b = a`는 복사가 아니라 이름표를 하나 더 붙이는 것임을 기억하세요.
- **관련 장**: 6장 6.2(`b = a`와 `copy()`), 9장(인자 전달)

### 35. 부동소수 비교

```python
print(0.1 + 0.2 == 0.3)        # False
print(0.1 + 0.2)               # 0.30000000000000004

import math
print(math.isclose(0.1 + 0.2, 0.3))   # True

from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))  # True
print(round(2.675, 2))         # 2.67
```

컴퓨터는 실수를 2진수로 저장하는데, `0.1`은 2진수로 끝없이 이어지는 소수라 아주 작은 오차가 생깁니다(3장의 사과 나누기 이야기). `round(2.675, 2)`가 `2.68`이 아니라 `2.67`인 것도 `2.675`가 실제로는 `2.67499999…`로 저장되기 때문이에요.

- **고치는 법**: 실수끼리는 `==`로 비교하지 말고 `math.isclose()`를 씁니다. 돈처럼 정확해야 하는 계산은 `Decimal("0.1")`처럼 **문자열로** 만든 `Decimal`을 쓰거나, 원 단위 정수로 계산하세요.
- **관련 장**: 3장 3.1

### 36. 문자열로 된 숫자 비교

```python
print('10' < '9', '사과' > '바나나')   # True True
```

문자열은 사전 순서로 비교합니다. 첫 글자 `'1'`이 `'9'`보다 앞이라 `'10' < '9'`가 참이에요. `input()`이나 파일에서 읽은 숫자를 정렬하거나 비교할 때 자주 생기는 버그입니다. 한글은 가나다순(유니코드 순서)이라 `'사과' > '바나나'`가 참이고요.

- **고치는 법**: 비교하기 전에 `int()`나 `float()`로 바꿉니다. 정렬이라면 `sorted(values, key=int)`.
- **관련 장**: 2장 2.5, 3장 3.2

## D.8 오류 메시지 읽는 법

마지막으로 긴 트레이스백(traceback)을 읽는 요령입니다. 함수가 함수를 부르는 프로그램에서 오류가 나면 이런 출력이 나와요.

```python
def average(scores):
    return sum(scores) / len(scores)

def report(students):
    for name, scores in students.items():
        print(name, average(scores))

report({"민수": [90, 80], "지아": []})
```

```text
민수 85.0
Traceback (most recent call last):
  File "main.py", line 8, in <module>
    report({"민수": [90, 80], "지아": []})
  File "main.py", line 6, in report
    print(name, average(scores))
                ^^^^^^^^^^^^^^^
  File "main.py", line 2, in average
    return sum(scores) / len(scores)
           ~~~~~~~~~~~~^~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

첫 줄의 `most recent call last`는 "가장 최근에 부른 것이 맨 마지막"이라는 뜻입니다. 그래서 트레이스백은 **아래에서 위로** 읽어요.

1. **맨 아래 줄부터 봅니다.** `ZeroDivisionError: division by zero`. 오류의 **종류**와 **설명**입니다. 이 부록에서 찾아볼 곳도 여기예요.
2. **바로 위의 `File ... line ...`을 봅니다.** 오류가 실제로 난 자리입니다. `main.py`의 2번 줄, `average` 함수 안이네요. `~~~^~~~` 표시가 `/`를 가리킵니다.
3. **한 칸씩 위로 올라가며 "누가 불렀나"를 봅니다.** `average`는 6번 줄의 `report`가 불렀고, `report`는 8번 줄의 맨 바깥 코드(`<module>`)가 불렀습니다.
4. **내가 쓴 파일 중 가장 아래 것을 고칩니다.** 트레이스백 중간에 `File ".../site-packages/..."`나 `<frozen ...>`처럼 라이브러리 파일이 끼어 있으면, 대개 문제는 라이브러리가 아니라 그것을 부른 **내 코드**에 있어요. 내 파일 이름이 나오는 가장 아래 줄부터 의심하세요.

이 예에서는 2번 줄이 터졌지만, 진짜 원인은 `"지아"`의 점수가 빈 리스트라는 데이터입니다. 위의 `민수 85.0`이 찍힌 것도 단서예요. 첫 학생은 무사히 지나갔다는 뜻이니까요. 고치는 곳은 `average`에서 빈 리스트를 처리하는 것(26번)입니다.

트레이스백을 읽어도 원인이 안 보이면 이렇게 해 보세요.

- **값을 찍어 봅니다.** 오류 난 줄 바로 앞에 `print(f"{scores=}")`를 넣으면 그 순간의 값이 보입니다(부록 B.4의 `=` 서식).
- **자료형을 찍어 봅니다.** `TypeError`와 `AttributeError`는 대부분 "그 변수가 생각한 자료형이 아님"이 원인이라 `print(type(x))` 한 줄로 풀리는 경우가 많아요.
- **문제를 줄입니다.** 오류가 나는 부분만 새 파일에 옮겨서 최소한의 코드로 다시 만들어 보세요. 줄이다 보면 원인이 보이고, 남에게 물어볼 때도 그 짧은 코드와 **트레이스백 전체**를 함께 보여 주면 훨씬 빨리 답을 얻습니다.
- **메시지 마지막 줄을 그대로 검색합니다.** 파일 경로나 변수 이름처럼 내 코드에만 있는 부분은 빼고, `TypeError: can only concatenate str`처럼 일반적인 부분만 검색창에 넣으세요.
