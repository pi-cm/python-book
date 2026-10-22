# Chapter 14: 모듈과 패키지

> **학습 목표**  
> - 모듈·패키지·라이브러리의 차이를 설명하고 import로 불러 쓰기
> - 패키지를 만들고 상대 import와 절대 import를 구분해 쓰기
> - 모듈 검색 경로를 이해하고 ModuleNotFoundError 해결하기
> - uv로 의존성을 관리하고 패키지 배포 흐름 익히기

---

파이썬에서 코드가 길어지면 하나의 파일로 관리하기 어려워집니다. 이때 모듈과 패키지를 사용하면 코드를 논리적으로 분리하고 재사용할 수 있습니다. 실무에서 필수적인 개념이므로 차근차근 알아보겠습니다.

## 들어가며: 모듈, 패키지, 라이브러리는 다 같은 건가요?

처음 파이썬을 배우면 "모듈", "패키지", "라이브러리"라는 말이 뒤섞여 나와서 헷갈립니다. 다 같은 말일까요? 비슷하지만 크기가 다릅니다. 공구로 비유해 볼게요.

- **함수와 클래스**는 망치, 드라이버 같은 **공구 하나**입니다. 한 가지 기능을 합니다.
- **모듈(module)** 은 공구 여러 개를 담은 **공구함 하나**입니다. 함수, 클래스, 변수를 모아 둔 파이썬 파일 1개(`cafe_utils.py` 같은)가 모듈이에요.
- **패키지(package)** 는 공구함 여러 개를 넣어 둔 **창고 한 칸**입니다. 관련된 모듈 파일들을 모아 둔 폴더예요.
- **라이브러리(library)** 는 그런 창고들이 모인 **철물점**입니다. 패키지 여러 개를 묶어 부르는 말이고, 파이썬 문법에 정해진 단위라기보다 "남이 만들어 둔 코드 묶음"을 넓게 부르는 이름입니다.

우리는 이미 모듈을 써 왔습니다. `import random`이나 `import math`가 바로 남이 만들어 둔 공구함을 꺼내 오는 문장이죠. 이 장에서는 반대로 **내가 공구함을 만들고, 창고를 정리하고, 남에게 나눠 주는 방법**까지 차례로 살펴봅니다.

## 14.1 모듈의 기본 개념

### 모듈이란?

모듈(module)은 파이썬 코드가 담긴 `.py` 파일입니다. 함수, 클래스, 변수 등을 정의해두고 다른 파일에서 불러와 사용할 수 있습니다.

남이 만든 모듈부터 써 볼까요? 파이썬에 기본으로 들어 있는 `random` 모듈로 로또 번호를 뽑아 보겠습니다. `random.sample(모집단, k)`는 모집단에서 **겹치지 않게** k개를 골라 리스트로 돌려줍니다. 원본은 건드리지 않아요. 1부터 45까지 중에서 6개를 뽑으면 로또 번호가 되죠.

```python
import random

번호 = sorted(random.sample(range(1, 46), 6))
print(f"이번 주 로또 번호: {번호}")
```

실행할 때마다 다른 번호가 나옵니다. 우리는 번호를 뽑는 방법을 한 줄도 짜지 않았어요. `random.py`라는 파일 하나, 즉 모듈 하나를 불러와서 그 안에 있는 `sample` 함수를 빌려 썼을 뿐입니다. `random.sample`의 점(`.`)은 "random 모듈 안에 있는 sample"이라는 뜻이고요. 모듈의 힘은 이것입니다. **한 번 잘 만들어 두면 누구나 `import` 한 줄로 가져다 쓸 수 있다**는 것.

### 첫 번째 모듈 만들기

이제 직접 만들어 볼 차례입니다. 모듈을 만드는 데 특별한 문법은 필요 없습니다. 평소처럼 `.py` 파일에 함수와 클래스를 쓰고 저장하면 그 파일이 곧 모듈이에요. 서울의 카페 관리 시스템을 예제로 모듈을 만들어보겠습니다.

파일 이름은 그대로 모듈 이름이 되니 조금 신경 써서 짓습니다. PEP 8(파이썬 공식 스타일 가이드)은 모듈 이름을 **짧은 소문자**로 짓고, 읽기 쉬워진다면 밑줄(`_`)을 써도 좋다고 권합니다. `cafe-utils.py`처럼 하이픈을 넣으면 `import cafe-utils`가 "cafe 빼기 utils"로 읽혀서 불러올 수가 없어요. 숫자로 시작하는 이름이나 띄어쓰기가 들어간 이름도 같은 이유로 안 됩니다.

```python
# cafe_utils.py
"""
서울 카페 관리를 위한 유틸리티 모듈
"""

# 상수 정의
DEFAULT_PRICE = 4500
MENU_CATEGORIES = ['커피', '차', '디저트', '베이커리']

# 함수 정의
def calculate_total(items):
    """주문 항목들의 총액을 계산합니다."""
    total = 0
    for item in items:
        total += item.get('price', DEFAULT_PRICE)
    return total

def format_menu_item(name, price, category='커피'):
    """메뉴 항목을 형식에 맞게 포맷팅합니다."""
    return {
        'name': name,
        'price': price,
        'category': category,
        'formatted': f"{name} - {price:,}원 ({category})"
    }

# 클래스 정의
class CafeManager:
    """카페 관리 클래스"""
    
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.menu = []
        self.orders = []
    
    def add_menu_item(self, name, price, category='커피'):
        item = format_menu_item(name, price, category)
        self.menu.append(item)
        return item
    
    def get_daily_sales(self):
        return sum(calculate_total(order['items']) for order in self.orders)

# 모듈 레벨 변수
cafe_locations = ['강남', '홍대', '명동', '건대', '신촌']

# 실행 시점 확인
if __name__ == '__main__':
    # 이 부분은 모듈이 직접 실행될 때만 실행됩니다
    print("카페 유틸리티 모듈 테스트")
    test_cafe = CafeManager("테스트 카페", "강남")
    test_cafe.add_menu_item("아메리카노", 4500)
    print(f"메뉴: {test_cafe.menu}")
```

파일 하나에 상수, 함수, 클래스, 변수가 다 들어 있죠? 이름 모양을 눈여겨보세요. PEP 8의 이름 규칙을 그대로 따른 것입니다.

| 종류 | 규칙 | 예 |
|---|---|---|
| 모듈(파일) | 짧은 소문자, 필요하면 밑줄 | `cafe_utils` |
| 패키지(폴더) | 짧은 소문자, 밑줄은 되도록 쓰지 않음 | `json`, `email` (이 장의 `seoul_restaurants`처럼 밑줄을 쓰기도 함) |
| 클래스 | 단어 첫 글자를 대문자로 이어 붙임 | `CafeManager` |
| 함수·변수 | 소문자, 단어 사이는 밑줄 | `calculate_total`, `cafe_locations` |
| 상수 | 모두 대문자, 단어 사이는 밑줄 | `DEFAULT_PRICE`, `MENU_CATEGORIES` |
| 모듈 안에서만 쓸 것 | 이름 앞에 밑줄 하나 | `_validate_price` |

이름만 보고도 "이건 바꾸면 안 되는 값이구나", "이건 클래스구나" 하고 알 수 있으니 코드를 읽는 사람이 편해집니다. PEP 8이 인용하는 말처럼 코드는 쓰는 횟수보다 읽히는 횟수가 훨씬 많거든요. 다만 이것은 **권고**입니다. 이미 다른 규칙으로 일관되게 짜여 있는 프로젝트라면, 그 프로젝트의 규칙을 따르는 것이 더 중요합니다. 하나 더, 소문자 `l`, 대문자 `O`, 대문자 `I`는 글꼴에 따라 숫자 1, 0과 구분이 안 돼서 한 글자 이름으로는 쓰지 말라고 합니다.

맨 아래 `if __name__ == '__main__':` 부분이 이 모듈의 비밀 장치입니다. 파이썬은 파일을 실행할 때마다 `__name__`이라는 변수에 이름표를 붙여 줍니다. `python cafe_utils.py`처럼 **직접 실행하면** 이름표가 `'__main__'`이 되고, 다른 파일에서 `import cafe_utils`로 **불러오면** 이름표가 모듈 이름인 `'cafe_utils'`가 됩니다. 그래서 이 `if` 아래에 둔 테스트 코드는 직접 실행할 때만 돌고, 다른 파일이 불러갈 때는 조용히 건너뜁니다. 직접 실행해 보면 이렇게 나옵니다.

```
카페 유틸리티 모듈 테스트
메뉴: [{'name': '아메리카노', 'price': 4500, 'category': '커피', 'formatted': '아메리카노 - 4,500원 (커피)'}]
```

### 피해야 할 이름: 예약어와 내장 이름

모듈 이름이든 변수 이름이든 절대 쓸 수 없는 이름이 있습니다. 파이썬이 문법용으로 미리 찜해 둔 **예약어(keyword)** 예요. `if`, `for`, `class` 같은 것들이죠. 어떤 것들이 있는지는 `keyword` 모듈로 직접 출력해 볼 수 있습니다.

```python
import keyword

print(keyword.kwlist)       # 예약어
print(keyword.softkwlist)   # soft keyword
```

파이썬 3.12에서 실행하면 예약어 35개와 soft keyword 4개(`_`, `case`, `match`, `type`)가 나옵니다. soft keyword는 특정 문법 안에서만 예약어처럼 동작하는 이름이라, 변수 이름으로 써도 당장 에러는 나지 않습니다. 하지만 읽는 사람이 헷갈리니 피하는 게 좋아요.

> **Q. 저는 출력이 조금 다른데요? `match`나 `type`이 없어요.**
> 파이썬 버전이 다르면 충분히 그럴 수 있습니다. `match`와 `case`는 3.10에서 패턴 매칭 문법과 함께, `type`은 3.12에서 새로 생겼어요. 예약어도 시간이 지나면서 새로 등장하는 거죠. 내 버전은 `import sys; print(sys.version)`으로 확인할 수 있습니다.

더 조심해야 할 것은 `print`, `list`, `sum` 같은 **내장 이름**입니다. 이들은 예약어가 아니라서 덮어써도 에러가 나지 않아요. 그래서 더 위험합니다. `list = [1, 2, 3]`이라고 한 번 쓰고 나면 그 아래에서 `list("abc")`를 부를 때 `TypeError: 'list' object is not callable`이 납니다. 내장 이름 목록은 `import builtins; print(dir(builtins))`로 볼 수 있습니다.

모듈 이름도 마찬가지입니다. 연습하다가 파일 이름을 `random.py`로 저장하고 그 안에서 `import random`을 하면, 파이썬은 표준 라이브러리 대신 **내 파일 자신**을 불러옵니다. 파이썬 3.12에서는 `AttributeError: partially initialized module 'random' has no attribute 'randint' (most likely due to a circular import)` 같은 알쏭달쏭한 에러가 나요. 표준 모듈과 같은 이름의 파일은 만들지 마세요.

## 14.2 모듈 불러오기 (Import)

### 기본적인 import 방법

`import 모듈이름`은 공구함을 통째로 들고 오는 방법입니다. 안에 든 것을 쓸 때마다 `cafe_utils.format_menu_item`처럼 **공구함 이름을 앞에 붙여야** 하죠. 조금 길지만 "이 함수가 어디서 왔는지"가 코드에 그대로 드러나는 장점이 있습니다.

```python
# main.py
import cafe_utils

# 모듈의 함수 사용
menu_item = cafe_utils.format_menu_item("라떼", 5000)
print(menu_item['formatted'])  # 라떼 - 5,000원 (커피)

# 모듈의 클래스 사용
my_cafe = cafe_utils.CafeManager("민수네 카페", "강남")
my_cafe.add_menu_item("아메리카노", 4500)
my_cafe.add_menu_item("크로와상", 3500, "베이커리")

print(f"카페명: {my_cafe.name}")
print(f"메뉴 개수: {len(my_cafe.menu)}")
```

`main.py`와 `cafe_utils.py`를 같은 폴더에 두고 실행하면 `라떼 - 5,000원 (커피)`, `카페명: 민수네 카페`, `메뉴 개수: 2`가 차례로 찍힙니다. 이때 `cafe_utils.py`의 `if __name__ == '__main__':` 아래 테스트 코드는 실행되지 않았다는 점도 확인해 보세요.

### from import 사용하기

공구함에서 자주 쓰는 공구 몇 개만 꺼내 책상 위에 올려 두는 방법도 있습니다. `from 모듈 import 이름`이라고 쓰면 그 이름을 내 파일로 직접 가져와서, 모듈 이름 없이 바로 부를 수 있어요.

```python
# main2.py
from cafe_utils import calculate_total, format_menu_item, CafeManager

# 모듈명 없이 직접 사용
orders = [
    {'price': 4500},  # 아메리카노
    {'price': 5000},  # 라떼
    {'price': 3500}   # 크로와상
]

total = calculate_total(orders)
print(f"총 주문금액: {total:,}원")  # 총 주문금액: 13,000원

# 클래스도 직접 사용
hongdae_cafe = CafeManager("수진네 카페", "홍대")
```

`calculate_total(orders)`처럼 짧게 쓸 수 있어서 편하죠. 대신 코드만 봐서는 `calculate_total`이 어느 모듈에서 왔는지 알 수 없으니, 파일 맨 위의 `import` 줄을 확인하는 습관을 들이세요.

### as를 사용한 별칭 지정

모듈이나 함수 이름이 길면 `as`로 별명을 붙일 수 있습니다. 친구 이름이 길면 줄여 부르는 것과 같아요. `import numpy as np`, `import pandas as pd`처럼 업계에서 굳어진 별명도 많아서 20장에서 자주 보게 됩니다. 다만 아래의 `CM`, `DP`처럼 나만 아는 별명을 남발하면 읽는 사람이 원래 이름을 찾아 헤매게 되니, 널리 쓰이는 별명이 아니라면 아껴 쓰세요.

```python
# main3.py
import cafe_utils as cu
from cafe_utils import CafeManager as CM, DEFAULT_PRICE as DP

# 긴 모듈명을 짧게 사용
cafe = cu.CafeManager("지훈네 카페", "명동")
print(f"기본 가격: {DP}원")

# 클래스명도 짧게 사용
another_cafe = CM("은혜네 카페", "신촌")
```

### 전체 import (주의해서 사용)

`from 모듈 import *`는 공구함을 책상 위에 통째로 쏟아 버리는 방법입니다. 편해 보이지만 왜 주의하라고 할까요?

제 이름은 아주 흔한 이름이라 수업 시간에 같은 이름이 네 명이나 있었던 적이 있습니다. 결국 이름 뒤에 A, B, C를 붙여서 불렀죠. 파이썬도 똑같은 문제를 겪습니다. 이름은 한정되어 있는데 코드가 길어질수록 같은 이름을 쓸 일이 생기거든요. 그래서 파이썬은 이름을 **네임스페이스(namespace, 이름 공간)** 라는 칸에 나눠 담습니다. 그리고 모듈 하나가 곧 네임스페이스 하나입니다. 내 파일의 `pi`와 `math` 모듈 안의 `pi`는 이름이 같아도 사는 칸이 달라서 부딪히지 않아요.

```python
import math

pi = 3                 # 내 파일(모듈)의 pi
print(pi, math.pi)     # 3 3.141592653589793
```

`math.pi`라고 칸 이름을 붙여 부르니 둘이 섞이지 않죠. 파이썬의 철학을 담은 "The Zen of Python"(`import this`로 볼 수 있습니다)의 마지막 줄도 "네임스페이스는 정말 훌륭한 아이디어다, 더 많이 쓰자!"입니다. 함수 안과 밖의 이름이 어떻게 나뉘는지는 9.2절(네임스페이스와 스코프)에서 다루고, 모듈은 그 칸을 파일 단위로 나누는 셈이에요.

그런데 `import *`는 이 칸막이를 없애고 모듈의 이름들을 내 칸에 쏟아붓습니다. 내 파일에 이미 같은 이름이 있으면 소리 없이 덮어써 버리고, 나중에 코드를 읽는 사람은 어떤 이름이 어디서 왔는지 알 수가 없게 되죠. 이것을 **네임스페이스 오염**이라고 부릅니다.

```python
# main4.py
from cafe_utils import *

# 모든 public 객체를 직접 사용할 수 있음
cafe = CafeManager("전체임포트 카페", "건대")
total = calculate_total([{'price': 4000}])

# 하지만 네임스페이스 오염이 발생할 수 있으므로 권장하지 않음
```

PEP 8도 `import *`는 어떤 이름이 들어왔는지 불분명하게 만드니 쓰지 말라고 권합니다. 대화형 셸에서 잠깐 실험할 때 정도만 쓰고, 파일로 저장하는 코드에서는 필요한 이름을 직접 적어 주세요.

> **Q. 같은 모듈을 여러 파일에서 `import` 하면 모듈 코드가 여러 번 실행되나요?**
> 아닙니다. 파이썬은 한 번 불러온 모듈을 `sys.modules`라는 사전에 기억해 두고, 다음 `import`부터는 기억해 둔 것을 그대로 돌려줍니다. 모듈 맨 위에 `print("모듈 실행됨")`을 넣고 `import`를 두 번 해 보면 한 번만 찍히는 것을 볼 수 있어요. 개발 중에 모듈을 고친 뒤 다시 읽어 들이고 싶다면 이 장 끝의 실전 팁에 나오는 `importlib.reload()`를 씁니다.

## 14.3 모듈의 고급 기능

### 모듈의 속성 확인하기

모듈도 객체라서 자기 자신에 대한 정보를 속성으로 들고 있습니다. 이름이 밑줄 두 개로 둘러싸인 속성들이에요. `__name__`은 앞에서 본 이름표, `__file__`은 모듈 파일이 실제로 있는 경로, `__doc__`은 모듈 맨 위에 쓴 설명 문자열(docstring)입니다. 그리고 `dir(모듈)`은 모듈 안에 있는 이름을 전부 목록으로 돌려줍니다.

```python
# module_info.py
import cafe_utils

# 모듈 정보 확인
print(f"모듈명: {cafe_utils.__name__}")
print(f"파일 경로: {cafe_utils.__file__}")
print(f"모듈 문서: {cafe_utils.__doc__}")

# 모듈에 정의된 모든 이름 확인
print("모듈의 모든 속성:")
for name in dir(cafe_utils):
    if not name.startswith('_'):  # private 속성 제외
        obj = getattr(cafe_utils, name)
        print(f"  {name}: {type(obj).__name__}")
```

실행하면 `모듈명: cafe_utils`와 파일 경로가 나오고, `모듈 문서:` 뒤에는 `cafe_utils.py` 맨 위에 적어 둔 "서울 카페 관리를 위한 유틸리티 모듈"이 그대로 찍힙니다. 속성 목록에는 `CafeManager: type`, `DEFAULT_PRICE: int`, `calculate_total: function`처럼 이름과 종류가 나란히 나와요. 남이 만든 모듈을 처음 받았을 때 이렇게 들여다보면 무엇이 들어 있는지 빠르게 파악할 수 있습니다.

### 모듈 문서화: 작성자, 일자, 사용법

`__doc__`에 담기는 모듈 docstring은 그 모듈의 **사용 설명서 첫 장**입니다. 파이썬이 실행할 때는 아무 일도 하지 않지만, `help(cafe_utils)`를 실행하거나 편집기에서 모듈 위에 마우스를 올리면 이 글이 나타나요. docstring 작성 관례를 정리한 PEP 257은 모든 모듈에 docstring을 두라고 권합니다. 첫 줄에는 한 줄 요약을 쓰고, 한 줄을 띄운 다음 자세한 설명을 씁니다. 팀에서 함께 쓰는 모듈이라면 작성자, 작성 일자, 입력과 출력, 주의할 점처럼 다른 사람이 알아야 할 것들을 여기에 적어 두세요.

```python
"""서울 카페 주문 금액을 계산하는 모듈.

작성자: 김개발
작성일: 2024-01-15
입력: 주문 항목 리스트 ({'price': 정수} 형태의 딕셔너리들)
출력: 총 금액(원)
"""

__author__ = "김개발"
__version__ = "1.0.0"

import json
```

작성자와 버전은 `__author__`, `__version__` 같은 모듈 수준 변수로 따로 두기도 합니다. 14.4절의 `seoul_restaurants/__init__.py`에도 이 변수들이 나옵니다. 위치에도 권고가 있는데, PEP 8은 이런 밑줄 두 개짜리 변수를 **docstring 바로 다음, `import` 문보다 위**에 두라고 합니다. 위 예제가 그 순서예요.

### __all__ 속성으로 public API 정의

모듈 안에는 남에게 쓰라고 내놓는 이름(공개 API)과 내부에서만 쓰는 이름이 섞여 있습니다. 가게로 치면 손님에게 보여 주는 메뉴판과 주방 안쪽의 재료 창고 같은 관계죠. 파이썬은 이 둘을 두 가지 방법으로 구분합니다. 하나는 앞에서 본 **밑줄로 시작하는 이름**이고, 다른 하나는 공개할 이름을 목록으로 적어 두는 `__all__`입니다.

```python
# cafe_utils_v2.py
"""
개선된 카페 유틸리티 모듈
"""

# public API 명시적으로 정의
__all__ = [
    'calculate_total',
    'format_menu_item', 
    'CafeManager',
    'DEFAULT_PRICE'
]

DEFAULT_PRICE = 4500
_INTERNAL_CONFIG = {'debug': False}  # private 변수

def calculate_total(items):
    """공개 함수"""
    return sum(item.get('price', DEFAULT_PRICE) for item in items)

def _validate_price(price):
    """내부 함수 (private)"""
    return price > 0

def format_menu_item(name, price, category='커피'):
    """공개 함수"""
    if not _validate_price(price):
        raise ValueError("가격은 0보다 커야 합니다")
    
    return {
        'name': name,
        'price': price,
        'category': category,
        'formatted': f"{name} - {price:,}원 ({category})"
    }

class CafeManager:
    """공개 클래스"""
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.menu = []
```

`__all__`에 적은 이름들이 이 모듈의 메뉴판입니다. `_INTERNAL_CONFIG`와 `_validate_price`는 밑줄로 시작하니 내부용이라는 표시고요. 이제 다른 파일에서 `import *`로 불러와 보겠습니다.

```python
# test_public_api.py
from cafe_utils_v2 import *

# __all__에 정의된 것만 import됨
print("사용 가능한 함수들:")
try:
    calculate_total([])  # 성공
    print("[O] calculate_total")
except NameError:
    print("[X] calculate_total")

try:
    _validate_price(100)  # 실패 - private 함수
    print("[O] _validate_price")
except NameError:
    print("[X] _validate_price (private)")
```

실행하면 `calculate_total`은 성공하고 `_validate_price`는 `NameError`가 나서 "(private)" 쪽이 찍힙니다. 그런데 사실 밑줄로 시작하는 이름은 `__all__`이 없어도 `import *`에 딸려 오지 않습니다. 그럼 `__all__`은 왜 필요할까요? 모듈 안에서 `import json`처럼 다른 모듈을 불러오면 `json`이라는 이름도 그 모듈의 이름이 됩니다. `__all__`이 없으면 `from 모듈 import *`를 할 때 이 `json`까지 따라 들어와요. 밑줄이 없는 이름 중에서도 **정말 내놓을 것만 고르는 목록**이 `__all__`인 셈입니다.

한 가지 기억할 점은, 파이썬에는 다른 언어처럼 진짜로 접근을 막는 `private`이 없다는 것입니다. `from cafe_utils_v2 import _validate_price`라고 이름을 콕 집어 부르면 얼마든지 가져올 수 있어요. 밑줄과 `__all__`은 자물쇠가 아니라 "여기부터는 내부용이에요, 나중에 예고 없이 바뀔 수 있어요"라는 **약속의 표시**입니다. PEP 8도 그래서 "private" 대신 "non-public"이라는 말을 씁니다. 공개 여부가 애매하면 일단 내부용(밑줄)으로 시작하세요. 내부용을 나중에 공개하는 것은 쉽지만, 공개한 것을 거둬들이면 그걸 쓰던 사람들의 코드가 깨집니다.

## 14.4 패키지 기초

### 패키지란?

패키지(package)는 관련된 모듈들을 하나의 디렉토리로 묶어놓은 것입니다. `__init__.py` 파일이 있는 디렉토리가 패키지가 됩니다.

모듈이 공구함이라면 패키지는 공구함을 종류별로 정리한 창고입니다. 파일이 열 개, 스무 개로 늘어나면 한 폴더에 다 두기 어렵죠. 그래서 비슷한 일을 하는 모듈끼리 폴더로 묶고, 폴더 안에 또 폴더를 둡니다. 불러올 때는 폴더 경로를 점으로 이어서 `seoul_restaurants.models.restaurant`처럼 씁니다. 파일 탐색기의 `seoul_restaurants/models/restaurant.py`를 파이썬식으로 적은 주소예요.

`__init__.py`는 이 폴더가 패키지라는 **간판**이자, 패키지를 처음 불러올 때 자동으로 실행되는 **입구 코드**입니다. 비워 둬도 되고, 아래 예제처럼 자주 쓰는 클래스를 미리 꺼내 두는 데 써도 됩니다. 참고로 파이썬 3.3부터는 `__init__.py`가 없는 폴더도 "네임스페이스 패키지"라는 특별한 형태로 불러올 수는 있습니다. 하지만 여러 곳에 흩어진 폴더를 하나로 합칠 때 쓰는 고급 기능이니, 보통의 패키지에는 `__init__.py`를 꼭 넣어 주세요.

### 실전 패키지 구조 만들기

서울시 맛집 관리 시스템을 패키지로 구성해보겠습니다. 데이터의 모양을 정하는 `models`, 검색과 추천 같은 기능을 맡는 `services`, 거리 계산처럼 여기저기서 쓰는 도구를 모은 `utils`로 역할을 나눴습니다. 실무 프로젝트도 대개 이렇게 "데이터 / 기능 / 도구"로 칸을 나눕니다.

```
seoul_restaurants/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── restaurant.py
│   └── review.py
├── services/
│   ├── __init__.py
│   ├── search.py
│   └── recommendation.py
└── utils/
    ├── __init__.py
    ├── location.py
    └── rating.py
```

폴더마다 `__init__.py`가 하나씩 들어 있죠? 이 파일이 있어야 각 폴더가 패키지가 됩니다. 이제 안쪽부터 하나씩 채워 보겠습니다.

### models 패키지 구현

먼저 `models/__init__.py`입니다. `from .restaurant import Restaurant`의 맨 앞 점(`.`)은 "지금 이 패키지 안의"라는 뜻이에요(14.6절에서 자세히 봅니다). 이렇게 해 두면 바깥에서는 `seoul_restaurants.models.restaurant.Restaurant`라는 긴 주소 대신 `seoul_restaurants.models.Restaurant`로 바로 꺼내 쓸 수 있습니다. 창고 입구에 자주 찾는 물건을 내놓아 두는 것과 같아요.

```python
# seoul_restaurants/models/__init__.py
"""
맛집 데이터 모델 패키지
"""
from .restaurant import Restaurant
from .review import Review

__all__ = ['Restaurant', 'Review']
```

다음은 맛집 한 곳의 정보를 담는 `Restaurant` 클래스입니다. `@dataclass`를 붙이면 `__init__`을 직접 쓰지 않아도 필드 목록대로 객체를 만들어 줍니다. `__post_init__`은 객체가 만들어진 직후에 불리는 메서드라서, 평점이 0~5 범위를 벗어나면 그 자리에서 `ValueError`를 냅니다. 잘못된 데이터는 들어오는 문 앞에서 막는 거죠.

```python
# seoul_restaurants/models/restaurant.py
"""
맛집 모델
"""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Restaurant:
    """서울 맛집 정보를 담는 클래스"""
    name: str
    district: str  # 강남구, 종로구 등
    cuisine_type: str  # 한식, 중식, 일식 등
    price_range: str  # 저렴, 보통, 비쌈
    rating: float = 0.0
    review_count: int = 0
    address: Optional[str] = None
    phone: Optional[str] = None
    
    def __post_init__(self):
        """초기화 후 검증"""
        if not (0 <= self.rating <= 5):
            raise ValueError("평점은 0-5 사이여야 합니다")
        
        if self.review_count < 0:
            raise ValueError("리뷰 수는 0 이상이어야 합니다")
    
    @property
    def display_name(self) -> str:
        """표시용 이름"""
        return f"{self.name} ({self.district})"
    
    def update_rating(self, new_rating: float, review_count_delta: int = 1):
        """새 리뷰 반영하여 평점 업데이트"""
        total_score = self.rating * self.review_count + new_rating
        self.review_count += review_count_delta
        self.rating = round(total_score / self.review_count, 1)
```

리뷰도 같은 방식으로 `review.py`라는 별도 파일에 둡니다. 맛집과 리뷰는 서로 관련이 있지만, 파일을 나눠 두면 리뷰 규칙이 바뀔 때 `review.py`만 열어 보면 됩니다.

```python
# seoul_restaurants/models/review.py
"""
리뷰 모델
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Review:
    """맛집 리뷰 클래스"""
    restaurant_id: str
    author_name: str
    rating: float
    content: str
    visit_date: datetime
    created_at: datetime = None
    helpful_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        
        if not (1 <= self.rating <= 5):
            raise ValueError("평점은 1-5 사이여야 합니다")
    
    @property
    def is_recent(self) -> bool:
        """최근 리뷰인지 확인 (30일 이내)"""
        days_ago = (datetime.now() - self.created_at).days
        return days_ago <= 30
    
    def get_summary(self) -> str:
        """리뷰 요약"""
        short_content = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.author_name} ({self.rating}점): {short_content}"
```

### services 패키지 구현

`services`는 모델을 가지고 실제 일을 하는 칸입니다. 여기서는 `search.py`의 `from ..models import Restaurant`를 눈여겨보세요. 점이 두 개(`..`)면 "한 칸 위 패키지", 즉 `seoul_restaurants`를 가리킵니다. 그 안의 `models`에서 `Restaurant`를 가져오라는 뜻이에요. 같은 창고의 옆 칸에서 물건을 빌려 오는 셈입니다.

```python
# seoul_restaurants/services/__init__.py
"""
맛집 서비스 로직 패키지
"""
from .search import RestaurantSearch
from .recommendation import RecommendationEngine

__all__ = ['RestaurantSearch', 'RecommendationEngine']
```

```python
# seoul_restaurants/services/search.py
"""
맛집 검색 서비스
"""
from typing import List, Optional, Dict, Any
from ..models import Restaurant

class RestaurantSearch:
    """맛집 검색 엔진"""
    
    def __init__(self, restaurants: List[Restaurant]):
        self.restaurants = restaurants
        self._build_indices()
    
    def _build_indices(self):
        """검색 성능을 위한 인덱스 구축"""
        self.district_index = {}
        self.cuisine_index = {}
        
        for restaurant in self.restaurants:
            # 지역별 인덱스
            district = restaurant.district
            if district not in self.district_index:
                self.district_index[district] = []
            self.district_index[district].append(restaurant)
            
            # 음식 종류별 인덱스
            cuisine = restaurant.cuisine_type
            if cuisine not in self.cuisine_index:
                self.cuisine_index[cuisine] = []
            self.cuisine_index[cuisine].append(restaurant)
    
    def search_by_district(self, district: str) -> List[Restaurant]:
        """지역별 맛집 검색"""
        return self.district_index.get(district, [])
    
    def search_by_cuisine(self, cuisine_type: str) -> List[Restaurant]:
        """음식 종류별 검색"""
        return self.cuisine_index.get(cuisine_type, [])
    
    def search_by_rating(self, min_rating: float) -> List[Restaurant]:
        """평점 이상 맛집 검색"""
        return [r for r in self.restaurants if r.rating >= min_rating]
    
    def advanced_search(self, **criteria) -> List[Restaurant]:
        """고급 검색"""
        results = self.restaurants.copy()
        
        if 'district' in criteria:
            results = [r for r in results if r.district == criteria['district']]
        
        if 'cuisine_type' in criteria:
            results = [r for r in results if r.cuisine_type == criteria['cuisine_type']]
        
        if 'min_rating' in criteria:
            results = [r for r in results if r.rating >= criteria['min_rating']]
        
        if 'price_range' in criteria:
            results = [r for r in results if r.price_range == criteria['price_range']]
        
        # 평점 순으로 정렬
        return sorted(results, key=lambda x: x.rating, reverse=True)
```

`_build_indices`는 객체를 만들 때 한 번만 지역별, 음식별로 맛집을 미리 분류해 두는 내부 메서드입니다(밑줄로 시작하니 바깥에서 부르라고 만든 것이 아니죠). 덕분에 `search_by_district`는 매번 전체 목록을 훑지 않고 사전에서 바로 꺼내 옵니다. 도서관이 책을 분야별 서가에 꽂아 두는 것과 같은 원리예요.

### utils 패키지 구현

`utils`에는 특정 기능에 묶이지 않고 여러 곳에서 두루 쓰는 도구를 둡니다. `location.py`는 서울 각 구의 좌표를 상수 `SEOUL_DISTRICTS`로 갖고 있고, 두 좌표 사이의 거리를 지구 반지름으로 계산하는 하버사인(haversine) 공식을 `DistanceCalculator`에 담았습니다. 권역 이름을 정하는 `_get_region_name`은 밑줄로 시작하니 이 모듈 안에서만 쓰는 함수예요.

```python
# seoul_restaurants/utils/__init__.py
"""
공통 유틸리티 패키지
"""
from .location import DistanceCalculator, get_district_info
from .rating import RatingAnalyzer

__all__ = ['DistanceCalculator', 'get_district_info', 'RatingAnalyzer']
```

```python
# seoul_restaurants/utils/location.py
"""
위치 관련 유틸리티
"""
import math
from typing import Any, Dict, Tuple

# 서울 주요 지역 좌표 (위도, 경도)
SEOUL_DISTRICTS = {
    '강남구': (37.5172, 127.0473),
    '강동구': (37.5301, 127.1238),
    '강북구': (37.6396, 127.0257),
    '강서구': (37.5509, 126.8495),
    '관악구': (37.4781, 126.9515),
    '광진구': (37.5384, 127.0822),
    '구로구': (37.4954, 126.8874),
    '금천구': (37.4519, 126.9018),
    '노원구': (37.6544, 127.0565),
    '도봉구': (37.6686, 127.0471),
    '동대문구': (37.5814, 127.0098),
    '동작구': (37.5124, 126.9393),
    '마포구': (37.5663, 126.9019),
    '서대문구': (37.5791, 126.9368),
    '서초구': (37.4837, 127.0324),
    '성동구': (37.5636, 127.0365),
    '성북구': (37.6066, 127.0182),
    '송파구': (37.5145, 127.1059),
    '양천구': (37.5167, 126.8665),
    '영등포구': (37.5264, 126.8962),
    '용산구': (37.5384, 126.9654),
    '은평구': (37.6176, 126.9227),
    '종로구': (37.5735, 126.9788),
    '중구': (37.5640, 126.9975),
    '중랑구': (37.6061, 127.0925)
}

def get_district_info(district: str) -> Dict[str, Any]:
    """지역 정보 조회"""
    coords = SEOUL_DISTRICTS.get(district)
    if not coords:
        return {'error': f'알 수 없는 지역: {district}'}
    
    return {
        'name': district,
        'latitude': coords[0],
        'longitude': coords[1],
        'region': _get_region_name(district)
    }

def _get_region_name(district: str) -> str:
    """지역별 권역 이름"""
    gangbuk = ['종로구', '중구', '용산구', '성동구', '광진구', '동대문구', '중랑구', '성북구', '강북구', '도봉구', '노원구', '은평구', '서대문구', '마포구']
    gangnam = ['강남구', '서초구', '송파구', '강동구']
    
    if district in gangbuk:
        return '강북'
    elif district in gangnam:
        return '강남'
    else:
        return '기타'

class DistanceCalculator:
    """거리 계산기"""
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """두 지점 간 거리 계산 (km)"""
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @classmethod
    def distance_between_districts(cls, district1: str, district2: str) -> float:
        """두 지역 간 거리"""
        coords1 = SEOUL_DISTRICTS.get(district1)
        coords2 = SEOUL_DISTRICTS.get(district2)
        
        if not coords1 or not coords2:
            raise ValueError(f"알 수 없는 지역: {district1} 또는 {district2}")
        
        return cls.haversine_distance(coords1[0], coords1[1], coords2[0], coords2[1])
```

`utils/__init__.py`가 불러오는 `rating.py`에는 평점 목록을 요약해 주는 `RatingAnalyzer`를 둡니다. 평균과 함께 1~5점이 각각 몇 개인지 세어 주는 작은 도구예요.

```python
# seoul_restaurants/utils/rating.py
"""
평점 분석 유틸리티
"""
from collections import Counter
from typing import Dict, List


class RatingAnalyzer:
    """평점 목록을 요약하는 분석기"""

    def average(self, ratings: List[float]) -> float:
        """평균 평점 (평점이 없으면 0.0)"""
        if not ratings:
            return 0.0
        return round(sum(ratings) / len(ratings), 1)

    def distribution(self, ratings: List[float]) -> Dict[int, int]:
        """1~5점 각각의 개수 (소수점 아래는 버림)"""
        counts = Counter(int(r) for r in ratings)
        return {score: counts.get(score, 0) for score in range(1, 6)}
```

### 메인 패키지 초기화

마지막으로 맨 바깥 폴더의 `__init__.py`입니다. 안쪽 패키지들에서 핵심 클래스를 한 번 더 끌어올려서, 사용하는 쪽은 `from seoul_restaurants import Restaurant`처럼 **창고 이름만 알면** 되게 만들었어요. 맨 위의 긴 docstring은 앞에서 본 모듈 문서화 그대로, 이 패키지를 어떻게 쓰는지 보여 주는 사용 설명서입니다. 패키지의 docstring은 이렇게 `__init__.py`에 씁니다.

```python
# seoul_restaurants/__init__.py
"""
서울 맛집 관리 시스템

Usage:
    from seoul_restaurants import Restaurant, RestaurantSearch
    
    # 맛집 생성
    restaurant = Restaurant(
        name="김수한무 한정식",
        district="강남구",
        cuisine_type="한식",
        price_range="비쌈",
        rating=4.5
    )
    
    # 검색 엔진 사용
    search = RestaurantSearch([restaurant])
    results = search.search_by_district("강남구")
"""

# 패키지 정보 (PEP 8: docstring 바로 다음, import보다 위)
__version__ = "1.0.0"
__author__ = "Seoul Restaurant Team"

# 주요 클래스들을 패키지 레벨에서 import
from .models import Restaurant, Review
from .services import RestaurantSearch, RecommendationEngine
from .utils import DistanceCalculator, get_district_info

# 공개 API 정의
__all__ = [
    # Models
    'Restaurant',
    'Review',
    # Services  
    'RestaurantSearch',
    'RecommendationEngine',
    # Utils
    'DistanceCalculator',
    'get_district_info'
]

# 패키지 레벨 설정
DEFAULT_PRICE_RANGES = ['저렴', '보통', '비쌈']
SUPPORTED_CUISINES = ['한식', '중식', '일식', '양식', '아시안', '분식', '카페']
```

## 14.5 패키지 사용하기

### 기본 사용법

창고를 다 정리했으니 이제 써 볼 차례입니다. `restaurant_app.py`는 `seoul_restaurants` 폴더와 **같은 위치**에 둡니다. 파이썬은 실행하는 파일이 있는 폴더부터 모듈을 찾기 때문이에요(14.7절). 첫 줄 하나로 세 칸(`models`, `services`, `utils`)에 흩어진 도구를 한꺼번에 가져오는 것을 보세요. 메인 `__init__.py`에서 끌어올려 둔 덕분입니다.

```python
# restaurant_app.py
from seoul_restaurants import Restaurant, RestaurantSearch, get_district_info

# 샘플 맛집 데이터 생성
restaurants = [
    Restaurant("김수한무 한정식", "강남구", "한식", "비쌈", 4.5, 128),
    Restaurant("홍길동 짜장면", "종로구", "중식", "저렴", 4.2, 89),
    Restaurant("이순신 초밥", "서초구", "일식", "보통", 4.7, 156),
    Restaurant("장보고 파스타", "마포구", "양식", "보통", 4.1, 94),
    Restaurant("을지문덕 족발", "강남구", "한식", "보통", 4.3, 201)
]

# 검색 엔진 초기화
search_engine = RestaurantSearch(restaurants)

print("=== 서울 맛집 검색 시스템 ===")

# 지역별 검색
print("\n1. 강남구 맛집:")
gangnam_restaurants = search_engine.search_by_district("강남구")
for restaurant in gangnam_restaurants:
    print(f"  • {restaurant.display_name} - {restaurant.rating}점")

# 음식 종류별 검색  
print("\n2. 한식 맛집:")
korean_restaurants = search_engine.search_by_cuisine("한식")
for restaurant in korean_restaurants:
    print(f"  • {restaurant.display_name} - {restaurant.price_range}")

# 평점 기준 검색
print("\n3. 평점 4.5 이상 맛집:")
high_rated = search_engine.search_by_rating(4.5)
for restaurant in high_rated:
    print(f"  • {restaurant.display_name} - {restaurant.rating}점 ({restaurant.review_count}개 리뷰)")

# 복합 조건 검색
print("\n4. 강남구의 4.0점 이상 맛집:")
filtered = search_engine.advanced_search(
    district="강남구",
    min_rating=4.0
)
for restaurant in filtered:
    print(f"  • {restaurant.display_name} - {restaurant.rating}점")

# 지역 정보 조회
print("\n5. 지역 정보:")
district_info = get_district_info("강남구")
print(f"  강남구: {district_info['region']} 권역")
print(f"  좌표: ({district_info['latitude']}, {district_info['longitude']})")
```

강남구 검색에는 김수한무 한정식(4.5)과 을지문덕 족발(4.3)이, 평점 4.5 이상 검색에는 김수한무 한정식과 이순신 초밥(4.7)이 나옵니다. 마지막의 지역 정보는 `강남구: 강남 권역`과 좌표 `(37.5172, 127.0473)`이고요. 사용하는 쪽 코드에는 인덱스를 어떻게 만드는지, 거리를 어떻게 계산하는지가 하나도 없습니다. 내부가 어떻게 생겼는지 몰라도 메뉴판(공개 API)만 보고 쓸 수 있다는 것, 이것이 패키지로 나누는 진짜 이유입니다.

### 하위 모듈 직접 접근

메인 `__init__.py`가 끌어올려 주지 않은 것도 쓸 수 있습니다. 폴더 경로를 끝까지 적어 주면 돼요. 창고 입구에 없는 물건은 안쪽 칸까지 직접 걸어 들어가서 꺼내 오는 셈입니다.

```python
# advanced_usage.py
from seoul_restaurants.models.restaurant import Restaurant
from seoul_restaurants.services.search import RestaurantSearch
from seoul_restaurants.utils.location import DistanceCalculator

# 거리 계산 예제
distance = DistanceCalculator.distance_between_districts("강남구", "종로구")
print(f"강남구와 종로구 사이의 거리: {distance:.1f}km")

# 맛집 평점 업데이트
restaurant = Restaurant("새로운 맛집", "홍대", "한식", "보통", 4.0, 50)
print(f"업데이트 전: {restaurant.rating}점 ({restaurant.review_count}개 리뷰)")

restaurant.update_rating(5.0)  # 새 리뷰 추가
print(f"업데이트 후: {restaurant.rating}점 ({restaurant.review_count}개 리뷰)")
```

강남구와 종로구 사이 거리는 `8.7km`로 나옵니다. 평점 업데이트 결과는 조금 의외일 수 있어요. 리뷰 50개, 평점 4.0인 곳에 5점 리뷰가 하나 더해지면 `(4.0 × 50 + 5.0) ÷ 51 = 4.0196…`이라서, 소수 첫째 자리로 반올림하면 여전히 `4.0`점입니다. 리뷰 수만 `51개`로 늘어나죠. 리뷰가 많이 쌓인 곳일수록 리뷰 하나로는 평균이 잘 움직이지 않는다는 것을 숫자로 확인할 수 있습니다.

## 14.6 상대 import vs 절대 import

### 절대 import (권장)

패키지 안의 모듈이 다른 모듈을 부를 때는 주소를 두 가지 방식으로 적을 수 있습니다. 집 주소로 비유하면 "서울시 종로구 세종대로 1"처럼 처음부터 다 적는 **절대 주소**와, "우리 집에서 옆집"처럼 지금 위치를 기준으로 적는 **상대 주소**가 있죠.

절대 import는 패키지의 최상위부터 전체 경로를 명시하는 방법입니다. PEP 8도 읽기 쉽고, 에러가 났을 때 어느 패키지에서 문제가 생겼는지 메시지에 분명히 드러난다는 이유로 절대 import를 권합니다.

```python
# seoul_restaurants/services/recommendation.py
"""
맛집 추천 엔진 (절대 import 사용)
"""
from seoul_restaurants.models.restaurant import Restaurant
from seoul_restaurants.models.review import Review
from seoul_restaurants.utils.rating import RatingAnalyzer
from typing import List, Dict

class RecommendationEngine:
    """맛집 추천 엔진"""
    
    def __init__(self, restaurants: List[Restaurant]):
        self.restaurants = restaurants
        self.rating_analyzer = RatingAnalyzer()
    
    def recommend_by_preference(self, 
                              preferred_cuisines: List[str],
                              preferred_districts: List[str] = None,
                              min_rating: float = 4.0) -> List[Restaurant]:
        """사용자 선호도 기반 추천"""
        candidates = []
        
        for restaurant in self.restaurants:
            # 음식 종류 필터
            if restaurant.cuisine_type not in preferred_cuisines:
                continue
            
            # 지역 필터 (선택사항)
            if preferred_districts and restaurant.district not in preferred_districts:
                continue
            
            # 최소 평점 필터
            if restaurant.rating < min_rating:
                continue
                
            candidates.append(restaurant)
        
        # 평점과 리뷰 수를 종합한 점수로 정렬
        return sorted(candidates, 
                     key=lambda r: (r.rating * 0.7 + min(r.review_count/100, 1) * 0.3),
                     reverse=True)[:10]
    
    def recommend_similar(self, target_restaurant: Restaurant) -> List[Restaurant]:
        """비슷한 맛집 추천"""
        similar = []
        
        for restaurant in self.restaurants:
            if restaurant.name == target_restaurant.name:
                continue
            
            similarity_score = 0
            
            # 같은 음식 종류 (+3점)
            if restaurant.cuisine_type == target_restaurant.cuisine_type:
                similarity_score += 3
            
            # 같은 지역 (+2점)  
            if restaurant.district == target_restaurant.district:
                similarity_score += 2
            
            # 비슷한 가격대 (+1점)
            if restaurant.price_range == target_restaurant.price_range:
                similarity_score += 1
            
            # 비슷한 평점 (차이가 적을수록 높은 점수)
            rating_diff = abs(restaurant.rating - target_restaurant.rating)
            if rating_diff <= 0.5:
                similarity_score += 2
            elif rating_diff <= 1.0:
                similarity_score += 1
            
            if similarity_score >= 3:  # 임계점
                similar.append((restaurant, similarity_score))
        
        # 유사도 점수 순으로 정렬
        similar.sort(key=lambda x: x[1], reverse=True)
        return [restaurant for restaurant, score in similar[:5]]
```

`from seoul_restaurants.models.restaurant import Restaurant`만 봐도 `Restaurant`가 어디 있는지 바로 알 수 있죠. 추천 로직도 살펴보면, `recommend_by_preference`는 평점(70%)과 리뷰 수(30%, 100개 이상이면 만점)를 섞은 점수로 줄을 세우고, `recommend_similar`는 음식 종류(+3), 지역(+2), 가격대(+1), 평점 차이(+2 또는 +1)를 더해 3점 이상인 곳만 비슷한 맛집으로 고릅니다.

### 상대 import (패키지 내부에서만 사용)

상대 import는 현재 위치를 기준으로 다른 모듈을 참조하는 방법입니다. 점 하나(`.`)는 지금 모듈이 들어 있는 패키지, 점 두 개(`..`)는 그 한 칸 위 패키지예요. 터미널에서 `cd ..`로 상위 폴더에 가는 것과 비슷합니다.

```python
# seoul_restaurants/services/recommendation_relative.py
"""
맛집 추천 엔진 (상대 import 사용 예제)
"""
from typing import List

# 같은 레벨의 다른 모듈
from .search import RestaurantSearch

# 상위 패키지의 모듈
from ..models.restaurant import Restaurant
from ..models.review import Review

# 상위 패키지의 다른 하위 패키지
from ..utils.rating import RatingAnalyzer

class RecommendationEngineRelative:
    """상대 import를 사용한 추천 엔진"""
    
    def __init__(self, restaurants: List[Restaurant]):
        self.restaurants = restaurants
        self.search_engine = RestaurantSearch(restaurants)  # 같은 패키지
        self.rating_analyzer = RatingAnalyzer()  # 다른 패키지
```

상대 import에는 꼭 알아 둘 함정이 하나 있습니다. 상대 import가 들어 있는 파일을 `python seoul_restaurants/services/search.py`처럼 **직접 실행하면** 에러가 나요.

```
ImportError: attempted relative import with no known parent package
```

직접 실행된 파일은 이름표가 `__main__`이 되어서, 자기가 어느 패키지에 속해 있는지 모르기 때문입니다. "옆집"이라고 말하려면 우리 집이 어디인지부터 알아야 하는데 그걸 모르는 거죠. 이럴 때는 패키지 바깥 폴더에서 `python -m seoul_restaurants.services.search`처럼 `-m` 옵션과 점 경로로 실행하면 파이썬이 패키지 위치를 알고 실행합니다.

### import 방식 비교

두 방식의 장단점을 한곳에 모아 보면 다음과 같습니다. 정리하면, 기본은 절대 import로 쓰고, 패키지 안쪽 깊은 곳에서 경로가 너무 길어질 때만 상대 import를 쓰는 것이 무난합니다.

```python
# import_comparison.py
"""
절대 import vs 상대 import 비교
"""

# 1. 절대 import (권장)
from seoul_restaurants.models.restaurant import Restaurant
from seoul_restaurants.services.search import RestaurantSearch

# 장점:
# - 명확하고 이해하기 쉬움
# - IDE에서 자동완성 지원 좋음
# - 에러 메시지에 전체 경로가 드러나 원인을 찾기 쉬움
# - 어디서든 사용 가능

# 2. 상대 import (패키지 내부에서만)
# from .models.restaurant import Restaurant  # 같은 레벨
# from ..models.restaurant import Restaurant  # 상위 레벨

# 장점:
# - 패키지명이 바뀌어도 코드 수정 불필요
# - 타이핑이 적음

# 단점:
# - 복잡한 구조에서 헷갈리기 쉬움
# - 스크립트를 직접 실행할 때 문제 발생 가능
```

## 14.7 모듈 검색 경로

### sys.path 이해하기

파이썬은 모듈을 찾기 위해 `sys.path`에 정의된 경로들을 순서대로 검색합니다.

`import cafe_utils`라고 쓰면 파이썬은 `cafe_utils.py`를 어디서 찾을까요? 컴퓨터 전체를 뒤지지는 않습니다. `sys.path`라는 리스트에 적힌 폴더들을 **앞에서부터 차례로** 열어 보고, 처음 발견한 것을 가져옵니다. 보통 맨 앞은 실행한 스크립트가 있는 폴더이고, 그 뒤로 `PYTHONPATH` 환경변수에 적은 폴더, 표준 라이브러리 폴더, 외부 패키지가 설치되는 `site-packages` 폴더가 이어집니다. 앞에서 `random.py`라는 내 파일이 표준 `random`을 가린 것도, 내 폴더가 표준 라이브러리 폴더보다 앞에 있었기 때문이에요.

```python
# path_example.py
import sys
import os

print("=== 파이썬 모듈 검색 경로 ===")
for i, path in enumerate(sys.path):
    print(f"{i+1:2d}. {path}")

print(f"\n현재 작업 디렉토리: {os.getcwd()}")
print(f"현재 파일 위치: {__file__}")

# 경로 추가하기
custom_path = "/Users/me/my_modules"
if custom_path not in sys.path:
    sys.path.append(custom_path)
    print(f"\n사용자 정의 경로 추가: {custom_path}")

# 경로 우선순위 변경 (맨 앞에 추가)
priority_path = "/Users/me/priority_modules"  
sys.path.insert(0, priority_path)
print(f"우선순위 경로 추가: {priority_path}")

print("\n=== 업데이트된 검색 경로 ===")
for i, path in enumerate(sys.path[:5]):  # 상위 5개만 표시
    print(f"{i+1:2d}. {path}")
```

출력되는 경로는 컴퓨터와 파이썬 설치 방법마다 다르니 내 화면의 목록을 직접 읽어 보세요. `append`는 목록 맨 뒤에 붙이니 **가장 나중에** 찾고, `insert(0, ...)`은 맨 앞에 끼워 넣으니 **가장 먼저** 찾습니다. 그리고 이렇게 코드로 바꾼 `sys.path`는 그 프로그램이 실행되는 동안에만 유효합니다. 프로그램이 끝나면 원래대로 돌아가요.

### PYTHONPATH 환경변수

코드를 고치지 않고 검색 경로를 늘리고 싶다면 `PYTHONPATH` 환경변수를 씁니다. 여기에 적은 폴더는 `sys.path`에서 표준 라이브러리보다 앞에 들어갑니다. 첫 번째 방법은 터미널을 닫기 전까지 계속 적용되고, 두 번째 방법은 그 한 번의 실행에만 적용돼요.

```bash
# 터미널에서 PYTHONPATH 설정
export PYTHONPATH="/Users/me/my_packages:$PYTHONPATH"

# 또는 파이썬 실행 시 설정
PYTHONPATH=/Users/me/my_packages python restaurant_app.py
```

다만 매번 경로를 손으로 맞추는 것은 번거롭고 실수하기 쉽습니다. 실무에서는 다음 절의 uv 같은 도구로 프로젝트를 **설치 가능한 패키지**로 만들어서 이 문제를 해결합니다.

### 모듈 탐색 과정 시뮬레이션

파이썬이 `sys.path`를 어떻게 훑는지 눈으로 보기 위해, 그 과정을 흉내 내는 함수를 만들어 보겠습니다. 경로마다 `이름.py` 파일이 있는지, 아니면 `__init__.py`가 든 `이름` 폴더(패키지)가 있는지 차례로 확인해요.

```python
# module_finder.py
import sys
import os
from pathlib import Path

def find_module_path(module_name):
    """모듈 탐색 과정 시뮬레이션"""
    print(f"=== '{module_name}' 모듈 탐색 과정 ===")
    
    for i, search_path in enumerate(sys.path):
        print(f"\n{i+1}. 경로 확인: {search_path}")
        
        if not search_path or not os.path.exists(search_path):
            print("   → 경로가 존재하지 않음")
            continue
            
        # .py 파일 찾기
        py_file = Path(search_path) / f"{module_name}.py"
        if py_file.exists():
            print(f"   [O] 발견: {py_file}")
            return str(py_file)
        
        # 패키지 디렉토리 찾기
        pkg_dir = Path(search_path) / module_name
        if pkg_dir.is_dir():
            init_file = pkg_dir / "__init__.py"
            if init_file.exists():
                print(f"   [O] 패키지 발견: {pkg_dir}")
                return str(pkg_dir)
        
        print("   → 해당 경로에서 발견되지 않음")
    
    print(f"\n[X] '{module_name}' 모듈을 찾을 수 없습니다")
    return None

# 테스트
find_module_path("cafe_utils")
find_module_path("seoul_restaurants") 
find_module_path("json")  # 내장 모듈
find_module_path("nonexistent_module")
```

`json`은 표준 라이브러리 폴더에서 `json/` 패키지로 발견됩니다. `json`이 사실은 `__init__.py`가 든 폴더, 즉 패키지라는 것도 알 수 있죠. `cafe_utils`와 `seoul_restaurants`는 이 스크립트를 어디서 실행하느냐에 따라 찾기도 하고 못 찾기도 합니다. 스크립트를 실행하면 `sys.path`의 맨 앞에는 현재 작업 폴더가 아니라 **스크립트 파일이 있는 폴더**가 들어가거든요.

이 함수는 원리를 보여 주는 간단한 흉내일 뿐입니다. 실제 파이썬은 `sys`처럼 인터프리터 안에 아예 들어 있는 내장 모듈을 먼저 확인하고, 컴파일된 파일과 C로 만든 확장 모듈까지 함께 살핍니다. 그래서 이 함수로 `sys`를 찾으면 못 찾는다고 나오지만, 실제 `import sys`는 잘 됩니다.

## 14.8 uv를 활용한 현대적 패키지 관리

### uv 소개 및 설치

uv는 Rust로 작성된 빠른 파이썬 패키지 매니저입니다. pip보다 훨씬 빠르고 현대적인 기능들을 제공합니다.

지금까지는 내가 만든 모듈과 표준 라이브러리만 썼습니다. 그런데 `requests`, `pandas`처럼 남이 만들어 인터넷(PyPI, 파이썬 패키지 저장소)에 올려 둔 라이브러리를 쓰려면 내려받아 설치해야 하죠. 철물점에서 공구를 사 오는 일입니다. 여기서 문제가 생깁니다. 프로젝트 A는 `pandas` 1.x가, 프로젝트 B는 2.x가 필요하다면요? 한 컴퓨터에 둘 다 설치할 수는 없습니다.

그래서 프로젝트마다 따로 쓰는 공구 창고, **가상환경(virtual environment)** 을 만듭니다. 그리고 "이 프로젝트에는 어떤 공구가 어떤 버전으로 필요하다"는 목록을 `pyproject.toml` 파일에 적어 둡니다. uv는 이 두 가지, 즉 가상환경 만들기와 목록대로 설치하기를 한 번에 해 주는 도구예요. 이 책의 예제를 `uv run python ...`으로 실행하는 것도 그래서입니다.

```bash
# uv 설치 (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 Homebrew로 설치 (macOS)
brew install uv
```

### 프로젝트 초기화

```bash
# 새 패키지 프로젝트 생성 (src/ 구조)
uv init --package seoul-restaurant-finder
cd seoul-restaurant-finder

# 기존 디렉토리에서 초기화
mkdir my-project && cd my-project
uv init --package
```

`uv init`은 프로젝트 폴더에 `pyproject.toml`, `README.md`, 파이썬 버전을 적어 두는 `.python-version` 같은 기본 파일을 만들어 줍니다. 옵션 없이 `uv init`만 실행하면 바로 실행해 볼 수 있는 `main.py`가 하나 들어간 단순한 구조가 생겨요(uv 0.9에서 확인). 이 장처럼 남에게 배포할 패키지를 만들 때는 위처럼 `--package`를 붙이면 소스 코드를 `src/` 폴더 아래에 두는 아래 구조가 만들어집니다. 소스를 `src/` 안에 한 번 더 넣는 이유는, 프로젝트 폴더에서 테스트를 돌릴 때 설치된 패키지 대신 폴더 속 소스가 실수로 불려 오는 일을 막기 위해서예요.

`uv init --package`가 생성하는 구조:

```
seoul-restaurant-finder/
├── pyproject.toml
├── README.md
├── src/
│   └── seoul_restaurant_finder/
│       └── __init__.py
└── .python-version
```

### pyproject.toml 설정

`pyproject.toml`은 프로젝트의 **신분증이자 장보기 목록**입니다. TOML이라는 설정 파일 형식으로 쓰는데, `[제목]`으로 구역을 나누고 그 아래에 `이름 = 값`을 적는 단순한 구조예요. 구역별로 보면 이렇습니다.

- `[project]`: 이름, 버전, 설명, 필요한 파이썬 버전 같은 신분 정보와, 꼭 필요한 의존성 목록(`dependencies`)
- `[project.optional-dependencies]`: 원하는 사람만 설치하는 추가 묶음. `web`, `data`처럼 이름을 붙여 둡니다.
- `[project.scripts]`: 설치하면 터미널 명령으로 쓸 수 있게 할 함수. `restaurant-search`라고 치면 `cli.py`의 `main()`이 실행됩니다.
- `[tool.이름]`: black, ruff, pytest, mypy 같은 개발 도구들의 설정
- `[build-system]`: 이 프로젝트를 배포용 파일로 묶을 때 쓸 도구(여기서는 hatchling)

`"requests>=2.31.0"`의 `>=`는 "2.31.0 이상이면 된다"는 뜻입니다.

```toml
# pyproject.toml
[project]
name = "seoul-restaurant-finder"
version = "0.1.0"
description = "서울 맛집 검색 및 추천 시스템"
readme = "README.md"
requires-python = ">=3.10"
authors = [
    { name = "김개발", email = "dev@example.com" }
]
keywords = ["restaurant", "seoul", "recommendation", "food"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

# 의존성 정의
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "click>=8.0.0",
]

# 선택적 의존성
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]
web = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
]
data = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
]

# 명령행 진입점
[project.scripts]
restaurant-search = "seoul_restaurant_finder.cli:main"

# 개발 도구 설정
[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "W", "C90", "I", "N", "UP", "S"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.mypy]
python_version = "3.10"
strict = true
ignore_missing_imports = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 의존성 관리

`pyproject.toml`을 손으로 고쳐도 되지만, 보통은 `uv add`로 추가합니다. `uv add requests`를 실행하면 uv가 목록에 `requests`를 적고, 가상환경에 설치하고, 실제로 설치된 정확한 버전을 `uv.lock` 파일에 기록합니다. 이 잠금 파일 덕분에 다른 사람이 `uv sync`를 하면 **나와 똑같은 버전**이 설치됩니다. "제 컴퓨터에서는 되는데요?"를 막아 주는 장치죠. 그래서 `uv.lock`은 코드와 함께 git에 커밋합니다. `--dev`로 추가한 것은 테스트, 코드 검사처럼 개발할 때만 필요한 도구라서, 배포한 패키지를 설치하는 사람에게는 설치되지 않습니다.

```bash
# 의존성 추가
uv add requests
uv add pydantic
uv add "fastapi>=0.100.0"

# 개발 의존성 추가  
uv add --dev pytest
uv add --dev black
uv add --dev ruff

# 선택적 의존성 묶음 추가 ([project.optional-dependencies])
uv add --optional web fastapi uvicorn
uv add --optional data pandas numpy

# 의존성 제거
uv remove requests

# 의존성 업데이트 (잠금 파일을 최신 버전으로 갱신한 뒤 설치)
uv lock --upgrade
uv sync

# 전체 의존성 설치
uv sync

# 선택적 의존성 묶음까지 함께 설치
uv sync --extra web
uv sync --extra data
```

### 가상환경과 실행

uv는 가상환경을 프로젝트 폴더 안의 `.venv`에 만듭니다. 예전에는 가상환경을 쓰려면 "활성화(activate)" 명령을 먼저 실행해야 했는데, `uv run`을 앞에 붙이면 그 과정을 알아서 처리해 줍니다. 가상환경이 없으면 만들고, 목록과 다르게 설치된 것이 있으면 맞춘 다음 명령을 실행해요.

```bash
# 가상환경 자동 생성 및 명령 실행
uv run python -c "print('Hello, World!')"
uv run pytest
uv run black .
uv run ruff check

# 스크립트 실행
uv run restaurant-search --district 강남구   # pyproject.toml의 [project.scripts]에 등록한 명령

# 대화형 Python 실행
uv run python
```

### 실제 프로젝트 예제

앞에서 만든 맛집 검색 기능을 uv 프로젝트로 옮겨 보겠습니다. `__init__.py`는 앞의 메인 패키지 초기화와 같은 역할이고, `cli.py`는 터미널에서 옵션을 받아 검색하는 명령행 프로그램입니다. 외부 라이브러리 `click`의 데코레이터(`@click.command()`, `@click.option(...)`)가 `--district` 같은 옵션을 함수 인자로 바꿔 줘요. 데코레이터는 10장에서 배웠고 16장에서 더 깊이 다룹니다.

먼저 앞 절에서 만든 파일 두 가지를 새 프로젝트로 복사해 오세요. `seoul_restaurants/models/` 폴더는 `src/seoul_restaurant_finder/models/`로, `seoul_restaurants/services/search.py`는 `src/seoul_restaurant_finder/search.py`로 옮깁니다. 그리고 복사한 `search.py` 맨 위의 `from ..models import Restaurant`를 `from .models import Restaurant`로 한 줄 고칩니다. `search.py`가 폴더 한 단계 위로 올라왔으니 `models`도 "부모 폴더(`..`)"가 아니라 "같은 폴더(`.`)"에 있게 됐기 때문이에요. 14.6절에서 본 상대 import의 점 개수가 바로 이 폴더 깊이입니다.

```python
# src/seoul_restaurant_finder/__init__.py
"""서울 맛집 검색 시스템"""
__version__ = "0.1.0"

from .models import Restaurant, Review
from .search import RestaurantSearch

__all__ = ["Restaurant", "Review", "RestaurantSearch"]
```

```python
# src/seoul_restaurant_finder/cli.py
"""명령행 인터페이스"""
import click
from .search import RestaurantSearch
from .models import Restaurant

@click.command()
@click.option('--district', help='검색할 지역구')
@click.option('--cuisine', help='음식 종류')
@click.option('--min-rating', type=float, default=0.0, help='최소 평점')
def main(district, cuisine, min_rating):
    """서울 맛집 검색 CLI"""
    # 샘플 데이터
    restaurants = [
        Restaurant("김수한무 한정식", "강남구", "한식", "비쌈", 4.5, 128),
        Restaurant("홍길동 짜장면", "종로구", "중식", "저렴", 4.2, 89),
        Restaurant("이순신 초밥", "서초구", "일식", "보통", 4.7, 156),
    ]
    
    search = RestaurantSearch(restaurants)
    
    # 검색 조건 적용
    criteria = {}
    if district:
        criteria['district'] = district
    if cuisine:
        criteria['cuisine_type'] = cuisine
    if min_rating > 0:
        criteria['min_rating'] = min_rating
    
    results = search.advanced_search(**criteria)
    
    click.echo(f"검색 결과: {len(results)}개 맛집")
    for restaurant in results:
        click.echo(f"• {restaurant.display_name} - {restaurant.rating}점")

if __name__ == '__main__':
    main()
```

### 빌드 및 배포

**빌드**는 프로젝트를 남에게 건넬 수 있는 상자로 포장하는 일입니다. `uv build`를 실행하면 `dist/` 폴더에 두 가지 파일이 생깁니다. 바로 설치할 수 있게 포장한 `.whl`(휠) 파일과, 소스 코드를 묶은 `.tar.gz` 파일이에요. `pyproject.toml`의 `[project.scripts]`에 적어 둔 덕분에, 설치하고 나면 `restaurant-search`가 터미널 명령으로 생깁니다.

```bash
# 패키지 빌드
uv build

# 로컬 설치 (개발용)
uv pip install -e .

# 명령행 도구 사용
restaurant-search --district "강남구" --min-rating 4.0

# PyPI 배포 (실제로는 하지 마세요)
# uv publish
```

PyPI에 올리는 순간 전 세계 누구나 받을 수 있게 되고, 한 번 올린 버전 번호는 다시 쓸 수 없습니다. 그래서 위 예제에서도 `uv publish`는 주석으로 막아 두었어요. 연습할 때는 14.11절에 나오는 테스트용 저장소(TestPyPI)를 쓰세요.

### 프로젝트 구조 예제

완성된 프로젝트는 대략 이런 모양이 됩니다. 소스(`src/`), 테스트(`tests/`), 문서(`docs/`), 사용 예제(`examples/`)를 칸칸이 나눠 두면 처음 보는 사람도 어디에 무엇이 있는지 금방 찾습니다.

```bash
# 완성된 프로젝트 구조
seoul-restaurant-finder/
├── pyproject.toml
├── README.md
├── .gitignore
├── .python-version
├── src/
│   └── seoul_restaurant_finder/
│       ├── __init__.py
│       ├── cli.py
│       ├── models.py
│       ├── search.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_search.py
│   └── conftest.py
├── docs/
│   ├── index.md
│   └── api.md
└── examples/
    ├── basic_usage.py
    └── advanced_search.py
```

### uv 사용의 장점

"빠르다"는 말은 직접 재 보는 게 제일 확실합니다. 아래 스크립트는 `subprocess`로 터미널 명령을 실행하고 걸린 시간을 잽니다. 결과는 컴퓨터와 캐시 상태에 따라 달라지니, 숫자는 내 컴퓨터에서 직접 확인해 보세요. 실행하고 나면 `test-uv`, `test-venv` 폴더가 생기니 다 본 뒤에는 지워 주세요.

```python
# performance_comparison.py
"""uv vs pip 성능 비교"""
import time
import subprocess

def time_command(cmd):
    """명령 실행 시간 측정"""
    start = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    end = time.time()
    return end - start, result.returncode

# 가상환경 생성 속도 비교
print("=== 가상환경 생성 속도 비교 ===")

# uv (매우 빠름)
uv_time, _ = time_command("uv venv test-uv --python 3.11")
print(f"uv venv 생성: {uv_time:.2f}초")

# python -m venv (느림)
venv_time, _ = time_command("python -m venv test-venv")
print(f"python venv 생성: {venv_time:.2f}초")

if uv_time > 0:
    print(f"uv가 {venv_time/uv_time:.1f}배 빠름")

# 의존성 해결 속도도 uv가 훨씬 빠름
print("\n=== uv의 주요 장점 ===")
print("1. 속도: Rust로 작성되어 매우 빠름")
print("2. 호환성: pip와 호환되는 API")
print("3. 의존성 해결: 더 정확하고 빠른 해결")
print("4. 캐싱: 효율적인 캐시 시스템")
print("5. 프로젝트 관리: pyproject.toml 기반 현대적 관리")
print("6. 멀티플랫폼: Windows, macOS, Linux 모두 지원")
print("7. 메모리 효율성: 메모리 사용량 최적화")

# 실제 사용 예제
print("\n=== 실제 워크플로우 예제 ===")
workflow_commands = [
    "# 새 프로젝트 시작",
    "uv init seoul-restaurant-api",
    "cd seoul-restaurant-api",
    "",
    "# 의존성 추가",
    "uv add fastapi uvicorn pydantic",
    "uv add --dev pytest black ruff",
    "",
    "# 개발 서버 실행",
    "uv run uvicorn main:app --reload",
    "",
    "# 테스트 실행",
    "uv run pytest",
    "",
    "# 코드 품질 검사",
    "uv run black .",
    "uv run ruff check .",
]

for cmd in workflow_commands:
    print(cmd)
```

출력 뒷부분의 워크플로우가 uv로 하는 일의 전부입니다. `init`으로 시작하고, `add`로 공구를 들이고, `run`으로 실행하고 검사하는 것. 이 세 가지만 기억해도 대부분의 프로젝트를 꾸릴 수 있습니다.

이제 Part 2에서 내장 모듈, 외부 패키지, 실전 프로젝트 구조에 대해 다루겠습니다.

## Part 2: 내장 모듈과 실전 활용

## 14.9 파이썬 내장 모듈 활용

### 자주 사용하는 내장 모듈들

파이썬을 설치하면 따로 아무것도 설치하지 않아도 쓸 수 있는 모듈이 수백 개 딸려 옵니다. 이것을 **표준 라이브러리**라고 하고, "배터리 포함(batteries included)"이라는 별명이 붙을 만큼 종류가 많아요. 철물점에 가기 전에 집 공구함부터 열어 보는 습관을 들이면, 이미 있는 기능을 다시 만드는 수고를 덜 수 있습니다. 여기서는 자주 쓰는 여섯 개를 맛보고, 더 자세한 내용은 17장에서 다룹니다.

```python
# builtin_modules_demo.py
"""자주 사용하는 파이썬 내장 모듈들"""

import os
import sys
import json
import datetime
import random
import pathlib
import collections
from typing import Dict, List, Any

print("=== 파이썬 내장 모듈 활용 예제 ===")

# 1. os 모듈 - 운영체제 관련 기능
print("\n1. os 모듈:")
print(f"  현재 OS: {os.name}")
print(f"  환경변수 PATH 일부: {os.environ.get('PATH', '')[:50]}...")
print(f"  임시 디렉토리: {os.path.join(os.getcwd(), 'temp')}")

# 2. sys 모듈 - 파이썬 인터프리터 관련
print("\n2. sys 모듈:")
print(f"  파이썬 버전: {sys.version_info}")
print(f"  플랫폼: {sys.platform}")
print(f"  모듈 검색 경로 수: {len(sys.path)}")

# 3. datetime 모듈 - 날짜와 시간
print("\n3. datetime 모듈:")
now = datetime.datetime.now()
print(f"  현재 시간: {now.strftime('%Y년 %m월 %d일 %H시 %M분')}")
print(f"  한 주 후: {(now + datetime.timedelta(weeks=1)).strftime('%Y-%m-%d')}")

# 4. json 모듈 - JSON 처리
print("\n4. json 모듈:")
sample_data = {
    "맛집명": "김수한무 한정식",
    "평점": 4.5,
    "리뷰수": 128,
    "메뉴": ["불고기", "갈비찜", "된장찌개"]
}
json_str = json.dumps(sample_data, ensure_ascii=False, indent=2)
print(f"  JSON 변환:\n{json_str}")

# 5. random 모듈 - 난수 생성
print("\n5. random 모듈:")
korean_foods = ["김치찌개", "불고기", "비빔밥", "냉면", "삼겹살"]
print(f"  오늘의 추천 메뉴: {random.choice(korean_foods)}")
print(f"  평점 시뮬레이션: {random.uniform(3.5, 5.0):.1f}점")

# 6. collections 모듈 - 특수 컨테이너
print("\n6. collections 모듈:")
review_counts = collections.Counter(["긍정", "긍정", "부정", "긍정", "중립", "긍정"])
print(f"  리뷰 분석: {dict(review_counts)}")

# defaultdict 사용 예제
district_restaurants = collections.defaultdict(list)
district_restaurants["강남구"].append("김수한무 한정식")
district_restaurants["종로구"].append("홍길동 짜장면")
print(f"  지역별 맛집: {dict(district_restaurants)}")
```

몇 가지만 짚어 볼게요. `json.dumps`의 `ensure_ascii=False`가 없으면 한글이 `김`처럼 알아보기 힘든 코드로 바뀌어 저장됩니다. 한글 데이터를 다룬다면 꼭 붙여 주세요. `Counter`는 목록에서 각 값이 몇 번 나왔는지 세어 주고, `defaultdict(list)`는 처음 보는 키에 빈 리스트를 자동으로 만들어 줘서 `if 키 not in 사전:` 같은 확인을 생략하게 해 줍니다.

`random` 모듈의 결과는 실행할 때마다 달라지죠. 그런데 컴퓨터는 사실 진짜 무작위 수를 만들지 못합니다. 정해진 계산식으로 무작위처럼 **보이는** 수를 만들어 내는데, 이것을 **의사 난수(pseudo-random number)** 라고 해요. 계산의 출발점인 씨앗값을 `random.seed(42)`처럼 고정하면 매번 똑같은 순서로 수가 나옵니다. 게임 테스트나 실험을 똑같이 재현하고 싶을 때 쓰는 방법이에요. 반대로 같은 이유로 비밀번호나 인증 코드처럼 보안이 필요한 곳에는 `random` 대신 `secrets` 모듈을 씁니다.

### pathlib 모듈 활용 (권장)

파일 경로를 다룰 때는 `os.path`보다 `pathlib`를 권합니다. 경로를 문자열이 아니라 `Path` 객체로 다루기 때문에, 슬래시 연산자(`/`)로 `project_root / "config" / "settings.json"`처럼 경로를 이어 붙일 수 있어요. 윈도우는 `\`, macOS와 리눅스는 `/`로 경로를 구분하는데, `pathlib`가 운영체제에 맞게 알아서 바꿔 줍니다. 12.2절에서 기본 사용법을 봤으니 여기서는 프로젝트 폴더를 만들고 탐색하는 실전 예제를 살펴보겠습니다.

```python
# pathlib_example.py
"""pathlib를 사용한 현대적인 경로 처리"""

from pathlib import Path
import json
from datetime import datetime

# 프로젝트 구조 생성
def setup_restaurant_project():
    """맛집 프로젝트 디렉토리 구조 생성"""
    
    # 기본 디렉토리 구조
    project_root = Path("restaurant_project")
    directories = [
        project_root / "data",
        project_root / "logs",
        project_root / "config",
        project_root / "reports"
    ]
    
    # 디렉토리 생성
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"디렉토리 생성: {directory}")
    
    # 설정 파일 생성
    config_data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "seoul_restaurants"
        },
        "api": {
            "rate_limit": 1000,
            "timeout": 30
        },
        "search": {
            "max_results": 50,
            "default_radius": 2.0
        }
    }
    
    config_file = project_root / "config" / "settings.json"
    config_file.write_text(
        json.dumps(config_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"설정 파일 생성: {config_file}")
    
    # 로그 파일 생성
    log_file = project_root / "logs" / f"app_{datetime.now():%Y%m%d}.log"
    log_file.write_text(
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 애플리케이션 시작\n",
        encoding="utf-8"
    )
    print(f"로그 파일 생성: {log_file}")
    
    return project_root

# 파일 시스템 탐색
def explore_project(project_root: Path):
    """프로젝트 구조 탐색"""
    print(f"\n=== {project_root.name} 프로젝트 구조 ===")
    
    # 재귀적으로 모든 파일과 디렉토리 탐색
    for path in sorted(project_root.rglob("*")):
        level = len(path.relative_to(project_root).parts)
        indent = "  " * (level - 1)
        
        if path.is_dir():
            print(f"{indent}{path.name}/")
        else:
            size = path.stat().st_size
            print(f"{indent}{path.name} ({size} bytes)")

# 파일 조작 예제
def file_operations_example():
    """pathlib를 사용한 파일 조작"""
    
    # 임시 데이터 디렉토리
    data_dir = Path("temp_data")
    data_dir.mkdir(exist_ok=True)
    
    # 여러 파일 생성
    sample_files = [
        ("restaurants.json", {"count": 150, "last_updated": "2024-01-15"}),
        ("reviews.json", {"total_reviews": 2847, "avg_rating": 4.2}),
        ("districts.json", {"서울시": 25, "경기도": 31})
    ]
    
    created_files = []
    for filename, data in sample_files:
        file_path = data_dir / filename
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        created_files.append(file_path)
        print(f"파일 생성: {file_path}")
    
    print(f"\n총 {len(created_files)}개 파일 생성됨")
    
    # 파일 정보 조회
    for file_path in created_files:
        stat = file_path.stat()
        print(f"\n파일: {file_path.name}")
        print(f"  크기: {stat.st_size} bytes")
        print(f"  확장자: {file_path.suffix}")
        print(f"  부모 디렉토리: {file_path.parent.name}")
        print(f"  절대 경로: {file_path.resolve()}")
    
    # 패턴 매칭으로 파일 찾기
    json_files = list(data_dir.glob("*.json"))
    print(f"\nJSON 파일들: {[f.name for f in json_files]}")
    
    # 파일 내용 읽고 처리
    total_count = 0
    for file_path in json_files:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            print(f"\n{file_path.name} 내용:")
            for key, value in data.items():
                print(f"  {key}: {value}")
                if isinstance(value, int):
                    total_count += value
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
    
    print(f"\n모든 숫자값 합계: {total_count}")
    
    return data_dir

if __name__ == "__main__":
    # 프로젝트 구조 생성
    project = setup_restaurant_project()
    explore_project(project)
    
    # 파일 조작 예제
    temp_dir = file_operations_example()
    
    print(f"\n[O] 예제 실행 완료")
    print(f"생성된 디렉토리:")
    print(f"  - {project.resolve()}")
    print(f"  - {temp_dir.resolve()}")
```

실행하면 `restaurant_project` 아래에 네 개의 폴더와 설정 파일, 날짜가 붙은 로그 파일이 만들어지고, `rglob("*")`이 그 안을 전부 훑어 트리처럼 보여 줍니다. `mkdir(parents=True, exist_ok=True)`는 "중간 폴더가 없으면 같이 만들고, 이미 있으면 그냥 넘어가라"는 뜻이라 여러 번 실행해도 에러가 나지 않아요. 마지막의 `모든 숫자값 합계`는 `3053`입니다. 150 + 2847 + 25 + 31을 더한 값인데, `isinstance(value, int)`로 정수만 골랐기 때문에 실수인 평균 평점 4.2는 빠졌습니다.

## 14.10 실전 프로젝트 구조

### 대규모 프로젝트 구조

실무에서 사용하는 체계적인 프로젝트 구조를 만들어보겠습니다.

처음 보면 폴더가 너무 많아서 겁이 날 수 있어요. 하지만 원리는 앞에서 본 맛집 패키지와 같습니다. **함께 바뀌는 것끼리 한 칸에 모은다**는 것이죠. 설정은 `config`, 데이터 모양은 `models`, 업무 규칙은 `services`, 외부와 맞닿는 입구는 `api`와 `cli`로 나눕니다. 그리고 소스 바깥에 테스트, 문서, 스크립트, 배포 설정을 따로 둡니다. 처음부터 이 구조를 다 만들 필요는 없고, 프로젝트가 커지면서 칸이 하나씩 늘어난다고 생각하면 됩니다.

```bash
# 실전 프로젝트 구조
seoul_food_platform/
├── pyproject.toml                 # 프로젝트 설정
├── README.md                      # 프로젝트 문서
├── .gitignore                     # Git 제외 파일
├── .env.example                   # 환경변수 예제
├── docker-compose.yml             # Docker 설정
├── 
├── src/                          # 소스 코드
│   └── seoul_food_platform/
│       ├── __init__.py
│       ├── config/               # 설정 관리
│       │   ├── __init__.py
│       │   ├── settings.py
│       │   └── database.py
│       ├── models/               # 데이터 모델
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── restaurant.py
│       │   ├── user.py
│       │   └── review.py
│       ├── services/             # 비즈니스 로직
│       │   ├── __init__.py
│       │   ├── restaurant_service.py
│       │   ├── user_service.py
│       │   └── recommendation_service.py
│       ├── api/                  # API 엔드포인트
│       │   ├── __init__.py
│       │   ├── v1/
│       │   │   ├── __init__.py
│       │   │   ├── restaurants.py
│       │   │   └── users.py
│       │   └── middleware/
│       ├── utils/                # 유틸리티
│       │   ├── __init__.py
│       │   ├── validators.py
│       │   ├── formatters.py
│       │   └── exceptions.py
│       ├── database/             # 데이터베이스 관련
│       │   ├── __init__.py
│       │   ├── connection.py
│       │   └── migrations/
│       └── cli/                  # 명령행 도구
│           ├── __init__.py
│           ├── commands/
│           └── main.py
├──
├── tests/                        # 테스트 코드
│   ├── __init__.py
│   ├── conftest.py              # pytest 설정
│   ├── unit/                    # 단위 테스트
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/             # 통합 테스트
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── fixtures/                # 테스트 데이터
│       ├── restaurants.json
│       └── users.json
├──
├── docs/                        # 문서화
│   ├── README.md
│   ├── api/
│   │   └── openapi.yaml
│   ├── architecture/
│   │   └── overview.md
│   └── deployment/
│       └── docker.md
├──
├── scripts/                     # 유틸리티 스크립트
│   ├── setup.py
│   ├── migrate.py
│   └── seed_data.py
├──
└── deployments/                 # 배포 설정
    ├── docker/
    │   ├── Dockerfile
    │   └── docker-compose.prod.yml
    ├── kubernetes/
    └── terraform/
```

### 설정 관리 모듈

데이터베이스 주소, 비밀 키, 로그 수준 같은 설정은 코드에 박아 두지 않고 한 모듈에 모읍니다. 개발할 때와 실제 서비스할 때 값이 달라지기 때문이에요. 아래 `Settings` 클래스는 pydantic 2의 설정 전용 패키지인 `pydantic-settings`의 `BaseSettings`를 상속해서(설치는 `uv add pydantic-settings`), 같은 이름의 환경변수나 `.env` 파일에 값이 있으면 그 값으로 기본값을 덮어씁니다. 그리고 `get_settings()`는 설정 객체를 처음 한 번만 만들고 그다음부터는 만들어 둔 것을 돌려줘서, 프로그램 전체가 같은 설정을 보게 합니다.

`secret_key`의 기본값은 말 그대로 예시일 뿐입니다. 비밀 키나 비밀번호는 절대 코드에 적어 git에 올리지 말고, 환경변수나 `.env` 파일(이 파일은 git에 올리지 않습니다)로 넣으세요. 프로젝트 구조의 `.env.example`은 "이런 항목들을 채워야 한다"는 견본만 담아 둔 파일입니다.

```python
# src/seoul_food_platform/config/__init__.py
"""설정 관리 패키지"""
from .settings import Settings, get_settings
from .database import DatabaseConfig

__all__ = ['Settings', 'get_settings', 'DatabaseConfig']
```

```python
# src/seoul_food_platform/config/settings.py
"""애플리케이션 설정"""
import os
from pathlib import Path
from typing import Optional, List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 기본 설정
    app_name: str = "Seoul Food Platform"
    debug: bool = False
    version: str = "1.0.0"
    
    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # 데이터베이스 설정
    database_url: str = "postgresql://localhost:5432/seoul_food"
    redis_url: str = "redis://localhost:6379"
    
    # API 설정
    api_v1_prefix: str = "/api/v1"
    api_rate_limit: int = 1000
    api_timeout: int = 30
    
    # 보안 설정
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 외부 API 키들
    google_maps_api_key: Optional[str] = None
    naver_api_key: Optional[str] = None
    kakao_api_key: Optional[str] = None
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 파일 업로드 설정
    upload_directory: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png", ".gif"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        """데이터베이스 URL 검증"""
        if not v.startswith(('postgresql://', 'sqlite://')):
            raise ValueError('지원하지 않는 데이터베이스 형식')
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """로그 레벨 검증"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'로그 레벨은 {valid_levels} 중 하나여야 합니다')
        return v.upper()
    
    @property
    def upload_path(self) -> Path:
        """업로드 디렉토리 경로"""
        return Path(self.upload_directory)
    
    def create_upload_directory(self) -> None:
        """업로드 디렉토리 생성"""
        self.upload_path.mkdir(parents=True, exist_ok=True)

# 전역 설정 인스턴스
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """설정 인스턴스 반환 (싱글톤 패턴)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# 환경별 설정 클래스들
class DevelopmentSettings(Settings):
    """개발 환경 설정"""
    debug: bool = True
    log_level: str = "DEBUG"
    database_url: str = "sqlite:///./dev.db"

class ProductionSettings(Settings):
    """운영 환경 설정"""
    debug: bool = False
    log_level: str = "WARNING"
    workers: int = 8

class TestSettings(Settings):
    """테스트 환경 설정"""
    debug: bool = True
    database_url: str = "sqlite:///./test.db"
    redis_url: str = "redis://localhost:6379/1"  # 다른 DB 사용

def get_settings_by_env(env: str = None) -> Settings:
    """환경에 따른 설정 반환"""
    env = env or os.getenv("ENVIRONMENT", "development")
    
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestSettings
    }
    
    settings_class = settings_map.get(env, Settings)
    return settings_class()
```

`config/__init__.py`가 함께 내놓는 `DatabaseConfig`는 `config/database.py`에 둡니다. 설정 객체에서 데이터베이스에 관한 값만 골라 담는 작은 데이터 클래스예요. 주소가 `sqlite://`로 시작하는지 보고 어떤 데이터베이스인지도 알려 줍니다.

```python
# src/seoul_food_platform/config/database.py
"""데이터베이스 연결 설정"""
from dataclasses import dataclass

from .settings import Settings


@dataclass(frozen=True)
class DatabaseConfig:
    """데이터베이스 연결에 필요한 값만 모은 설정"""
    url: str
    echo: bool = False      # True면 실행하는 SQL을 로그로 출력
    pool_size: int = 5      # 동시에 열어 둘 연결 수

    @property
    def is_sqlite(self) -> bool:
        """SQLite 데이터베이스인지 여부"""
        return self.url.startswith("sqlite://")

    @classmethod
    def from_settings(cls, settings: Settings) -> "DatabaseConfig":
        """애플리케이션 설정에서 데이터베이스 설정을 만든다"""
        return cls(url=settings.database_url, echo=settings.debug)
```

`frozen=True`라서 한 번 만든 설정은 바꿀 수 없습니다. 실행 도중에 누군가 실수로 데이터베이스 주소를 바꿔 버리는 일을 막아 주죠.

### 기본 모델 클래스

모든 모델에 공통으로 필요한 것, 예를 들어 고유 번호(`id`), 만든 시각, 고친 시각은 `BaseModel`에 한 번만 정의하고 상속해서 씁니다. `field(default_factory=uuid4)`는 객체를 만들 때마다 `uuid4()`를 **새로 불러서** 기본값을 만든다는 뜻이에요. 그냥 `= uuid4()`라고 쓰면 클래스를 정의할 때 딱 한 번 만든 값을 모든 객체가 같이 쓰게 됩니다. 아래의 믹스인(mixin)은 "타임스탬프 기능", "삭제 표시 기능"처럼 작은 기능 하나만 담은 조각 클래스로, 필요한 모델에 섞어(mix) 넣어 씁니다. 상속은 13장에서 자세히 다룹니다.

```python
# src/seoul_food_platform/models/base.py
"""기본 모델 클래스"""
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4, UUID

@dataclass
class BaseModel:
    """모든 모델의 기본 클래스"""
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def __post_init__(self):
        """초기화 후 처리"""
        if isinstance(self.id, str):
            self.id = UUID(self.id)
    
    def update_timestamp(self):
        """수정 시간 업데이트"""
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, UUID):
                result[key] = str(value)
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """딕셔너리에서 객체 생성"""
        # datetime 필드 변환
        for field_name in ['created_at', 'updated_at']:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        # UUID 필드 변환
        if 'id' in data and isinstance(data['id'], str):
            data['id'] = UUID(data['id'])
        
        return cls(**data)

@dataclass
class TimestampMixin:
    """타임스탬프 믹스인"""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def touch(self):
        """수정 시간 업데이트"""
        self.updated_at = datetime.now()

@dataclass  
class SoftDeleteMixin:
    """소프트 삭제 믹스인"""
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    def delete(self):
        """소프트 삭제"""
        self.is_deleted = True
        self.deleted_at = datetime.now()
    
    def restore(self):
        """삭제 복원"""
        self.is_deleted = False
        self.deleted_at = None
```

### 향상된 레스토랑 모델

14.4절의 `Restaurant`보다 훨씬 자세한 모델입니다. 음식 종류나 가격대처럼 정해진 값 중 하나만 와야 하는 것은 `Enum`으로 만들어 오타가 들어올 틈을 막고, 평점은 `float` 대신 `Decimal`로 다뤄 소수 계산 오차를 피합니다(3장에서 본 `0.1 + 0.1 + 0.1` 문제죠). 위치, 연락처, 영업시간처럼 덩어리진 정보는 각각 작은 데이터 클래스로 떼어 냈어요. 맨 아래의 팩토리 함수들은 샘플 데이터나 딕셔너리로부터 객체를 손쉽게 만들어 주는 도우미입니다. `@dataclass(kw_only=True)`도 눈여겨보세요. 부모 `BaseModel`의 필드들은 모두 기본값이 있는데, dataclass는 기본값 있는 필드 뒤에 `name`처럼 기본값 없는 필드가 오면 클래스를 만드는 순간 `TypeError`를 냅니다. 모든 필드를 키워드 전용으로 만들면 이 순서 제약이 사라져요(파이썬 3.10부터). 대신 객체를 만들 때는 `Restaurant(name=..., ...)`처럼 항상 이름을 붙여 넘깁니다.

```python
# src/seoul_food_platform/models/restaurant.py
"""레스토랑 모델"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from decimal import Decimal

from .base import BaseModel, TimestampMixin, SoftDeleteMixin

class CuisineType(Enum):
    """음식 종류"""
    KOREAN = "한식"
    CHINESE = "중식"  
    JAPANESE = "일식"
    WESTERN = "양식"
    ASIAN = "아시안"
    FUSION = "퓨전"
    CAFE = "카페"
    BAKERY = "베이커리"
    FAST_FOOD = "패스트푸드"
    
class PriceRange(Enum):
    """가격대"""
    BUDGET = "저렴"      # ~15,000원
    MODERATE = "보통"    # 15,000~30,000원
    EXPENSIVE = "비쌈"   # 30,000원~
    FINE_DINING = "고급" # 50,000원~

class RestaurantStatus(Enum):
    """운영 상태"""
    OPEN = "영업중"
    CLOSED = "휴업"
    PERMANENTLY_CLOSED = "폐업"
    TEMPORARILY_CLOSED = "임시휴업"

@dataclass
class Location:
    """위치 정보"""
    address: str
    district: str  # 구
    neighborhood: str  # 동
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    postal_code: Optional[str] = None
    
    @property
    def full_address(self) -> str:
        """전체 주소"""
        return f"서울시 {self.district} {self.address}"

@dataclass
class ContactInfo:
    """연락처 정보"""
    phone: Optional[str] = None
    website: Optional[str] = None
    social_media: Dict[str, str] = field(default_factory=dict)

@dataclass
class BusinessHours:
    """영업시간"""
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None
    holiday: Optional[str] = None
    
    def get_today_hours(self) -> Optional[str]:
        """오늘의 영업시간 반환"""
        from datetime import datetime
        weekday = datetime.now().weekday()  # 0=월요일
        
        hours_map = [
            self.monday, self.tuesday, self.wednesday, self.thursday,
            self.friday, self.saturday, self.sunday
        ]
        
        return hours_map[weekday] if weekday < 7 else None

@dataclass(kw_only=True)  # 부모의 기본값 필드 뒤에 필수 필드를 두기 위해 키워드 전용으로
class Restaurant(BaseModel, TimestampMixin, SoftDeleteMixin):
    """레스토랑 정보 모델"""
    name: str
    cuisine_type: CuisineType
    price_range: PriceRange
    location: Location
    
    # 평점 정보
    average_rating: Decimal = Decimal('0.0')
    review_count: int = 0
    rating_distribution: Dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
    
    # 기본 정보
    description: Optional[str] = None
    specialty_dishes: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)  # ["주차가능", "와이파이", "단체석"]
    
    # 연락처 및 영업정보
    contact: ContactInfo = field(default_factory=ContactInfo)
    business_hours: BusinessHours = field(default_factory=BusinessHours)
    status: RestaurantStatus = RestaurantStatus.OPEN
    
    # 메타데이터
    photos: List[str] = field(default_factory=list)  # 사진 URL들
    tags: List[str] = field(default_factory=list)
    verified: bool = False  # 사업자 인증 여부
    
    def __post_init__(self):
        super().__post_init__()
        
        # Enum 값 처리
        if isinstance(self.cuisine_type, str):
            self.cuisine_type = CuisineType(self.cuisine_type)
        if isinstance(self.price_range, str):
            self.price_range = PriceRange(self.price_range)
        if isinstance(self.status, str):
            self.status = RestaurantStatus(self.status)
        
        # Decimal 처리
        if isinstance(self.average_rating, (int, float)):
            self.average_rating = Decimal(str(self.average_rating))
    
    @property
    def display_name(self) -> str:
        """화면 표시용 이름"""
        return f"{self.name} ({self.location.district})"
    
    @property
    def is_highly_rated(self) -> bool:
        """고평점 맛집 여부 (4.0 이상)"""
        return self.average_rating >= Decimal('4.0')
    
    @property
    def is_popular(self) -> bool:
        """인기 맛집 여부 (리뷰 100개 이상)"""
        return self.review_count >= 100
    
    def add_review(self, rating: int, update_distribution: bool = True) -> None:
        """리뷰 추가 및 평점 업데이트"""
        if not 1 <= rating <= 5:
            raise ValueError("평점은 1-5 사이여야 합니다")
        
        # 새 평균 계산
        total_score = self.average_rating * self.review_count + Decimal(str(rating))
        self.review_count += 1
        self.average_rating = (total_score / self.review_count).quantize(Decimal('0.1'))
        
        # 평점 분포 업데이트
        if update_distribution:
            self.rating_distribution[rating] += 1
        
        self.update_timestamp()
    
    def get_rating_percentage(self, rating: int) -> float:
        """특정 평점의 비율 반환"""
        if self.review_count == 0:
            return 0.0
        return (self.rating_distribution.get(rating, 0) / self.review_count) * 100
    
    def matches_criteria(self, **criteria) -> bool:
        """검색 조건 매칭 확인"""
        for key, value in criteria.items():
            match key:
                case 'cuisine_type':
                    if self.cuisine_type != CuisineType(value):
                        return False
                case 'district':
                    if self.location.district != value:
                        return False
                case 'min_rating':
                    if self.average_rating < Decimal(str(value)):
                        return False
                case 'price_range':
                    if self.price_range != PriceRange(value):
                        return False
                case 'features':
                    if not all(feature in self.features for feature in value):
                        return False
                case _:
                    continue
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환 (오버라이드)"""
        result = super().to_dict()
        
        # Enum 처리
        result['cuisine_type'] = self.cuisine_type.value
        result['price_range'] = self.price_range.value  
        result['status'] = self.status.value
        
        # Decimal 처리
        result['average_rating'] = float(self.average_rating)
        
        # 중첩 객체 처리
        result['location'] = {
            'address': self.location.address,
            'district': self.location.district,
            'neighborhood': self.location.neighborhood,
            'latitude': self.location.latitude,
            'longitude': self.location.longitude,
            'postal_code': self.location.postal_code,
            'full_address': self.location.full_address
        }
        
        return result

# 팩토리 함수들
def create_sample_restaurant(name: str, district: str) -> Restaurant:
    """샘플 레스토랑 생성"""
    location = Location(
        address=f"{district} 샘플로 123",
        district=district,
        neighborhood="샘플동"
    )
    
    return Restaurant(
        name=name,
        cuisine_type=CuisineType.KOREAN,
        price_range=PriceRange.MODERATE,
        location=location,
        description=f"{name}의 맛있는 한식 레스토랑",
        specialty_dishes=["불고기", "된장찌개"],
        features=["주차가능", "와이파이"]
    )

def create_restaurant_from_dict(data: Dict[str, Any]) -> Restaurant:
    """딕셔너리로부터 레스토랑 객체 생성"""
    location_data = data.pop('location', {})
    contact_data = data.pop('contact', {})
    hours_data = data.pop('business_hours', {})
    
    location = Location(**location_data)
    contact = ContactInfo(**contact_data)  
    hours = BusinessHours(**hours_data)
    
    return Restaurant(
        location=location,
        contact=contact, 
        business_hours=hours,
        **data
    )
```

### 서비스 레이어

서비스가 던질 예외들은 `utils/exceptions.py`에 모아 둡니다. 모두 `SeoulFoodPlatformError`라는 공통 기반 예외를 상속하게 해 두면, 부르는 쪽에서 `except SeoulFoodPlatformError:` 한 줄로 이 프로젝트의 예외를 한꺼번에 잡을 수도 있고, 필요할 때는 `RestaurantNotFoundError`만 콕 집어 잡을 수도 있어요. 사용자 정의 예외는 12장에서 다뤘습니다.

```python
# src/seoul_food_platform/utils/exceptions.py
"""서울 음식 플랫폼의 예외 모음"""


class SeoulFoodPlatformError(Exception):
    """이 프로젝트의 모든 예외의 기반 클래스"""


class RestaurantNotFoundError(SeoulFoodPlatformError):
    """찾는 레스토랑이 없거나 삭제되었을 때"""


class InvalidRatingError(SeoulFoodPlatformError):
    """평점이 허용 범위(1~5)를 벗어났을 때"""
```

서비스 레이어는 "등록한다, 조회한다, 리뷰를 단다" 같은 **업무 규칙**을 담는 곳입니다. 모델이 데이터의 모양을 책임진다면, 서비스는 그 데이터로 무엇을 할 수 있는지를 책임지죠. 찾는 맛집이 없으면 `RestaurantNotFoundError`처럼 상황에 딱 맞는 이름의 예외를 던져서, 부르는 쪽이 무엇이 잘못됐는지 바로 알 수 있게 합니다. 삭제도 데이터를 진짜로 지우지 않고 `is_deleted` 표시만 바꾸는 소프트 삭제라서, 실수로 지운 것을 되살릴 수 있어요.

```python
# src/seoul_food_platform/services/restaurant_service.py
"""레스토랑 서비스"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from uuid import UUID

from ..models.restaurant import Restaurant, CuisineType, PriceRange
from ..utils.exceptions import RestaurantNotFoundError, InvalidRatingError

class RestaurantService:
    """레스토랑 비즈니스 로직"""
    
    def __init__(self):
        self.restaurants: Dict[UUID, Restaurant] = {}
    
    def create_restaurant(self, **restaurant_data) -> Restaurant:
        """새 레스토랑 등록"""
        restaurant = Restaurant(**restaurant_data)
        self.restaurants[restaurant.id] = restaurant
        return restaurant
    
    def get_restaurant(self, restaurant_id: UUID) -> Restaurant:
        """레스토랑 조회"""
        restaurant = self.restaurants.get(restaurant_id)
        if not restaurant or restaurant.is_deleted:
            raise RestaurantNotFoundError(f"레스토랑을 찾을 수 없습니다: {restaurant_id}")
        return restaurant
    
    def update_restaurant(self, restaurant_id: UUID, **updates) -> Restaurant:
        """레스토랑 정보 수정"""
        restaurant = self.get_restaurant(restaurant_id)
        
        for key, value in updates.items():
            if hasattr(restaurant, key):
                setattr(restaurant, key, value)
        
        restaurant.update_timestamp()
        return restaurant
    
    def delete_restaurant(self, restaurant_id: UUID) -> None:
        """레스토랑 삭제 (소프트 삭제)"""
        restaurant = self.get_restaurant(restaurant_id)
        restaurant.delete()
    
    def add_review(self, restaurant_id: UUID, rating: int) -> Restaurant:
        """리뷰 추가"""
        if not 1 <= rating <= 5:
            raise InvalidRatingError("평점은 1-5 사이여야 합니다")
        
        restaurant = self.get_restaurant(restaurant_id)
        restaurant.add_review(rating)
        return restaurant
    
    def search_restaurants(self, **criteria) -> List[Restaurant]:
        """레스토랑 검색"""
        results = []
        
        for restaurant in self.restaurants.values():
            if restaurant.is_deleted:
                continue
                
            if restaurant.matches_criteria(**criteria):
                results.append(restaurant)
        
        # 평점 순으로 정렬
        return sorted(results, key=lambda r: r.average_rating, reverse=True)
    
    def get_restaurants_by_district(self, district: str) -> List[Restaurant]:
        """지역별 레스토랑 조회"""
        return self.search_restaurants(district=district)
    
    def get_highly_rated_restaurants(self, min_rating: float = 4.0) -> List[Restaurant]:
        """고평점 레스토랑 조회"""
        return self.search_restaurants(min_rating=min_rating)
    
    def get_popular_restaurants(self, min_reviews: int = 100) -> List[Restaurant]:
        """인기 레스토랑 조회 (리뷰 수 기준)"""
        results = []
        for restaurant in self.restaurants.values():
            if restaurant.is_deleted:
                continue
            if restaurant.review_count >= min_reviews:
                results.append(restaurant)
        
        return sorted(results, key=lambda r: r.review_count, reverse=True)
    
    def get_restaurant_statistics(self) -> Dict[str, Any]:
        """레스토랑 통계 정보"""
        active_restaurants = [r for r in self.restaurants.values() if not r.is_deleted]
        
        if not active_restaurants:
            return {
                'total_count': 0,
                'average_rating': 0.0,
                'cuisine_distribution': {},
                'district_distribution': {},
                'price_range_distribution': {}
            }
        
        # 음식 종류별 분포
        cuisine_dist = {}
        for restaurant in active_restaurants:
            cuisine = restaurant.cuisine_type.value
            cuisine_dist[cuisine] = cuisine_dist.get(cuisine, 0) + 1
        
        # 지역별 분포
        district_dist = {}
        for restaurant in active_restaurants:
            district = restaurant.location.district
            district_dist[district] = district_dist.get(district, 0) + 1
        
        # 가격대별 분포
        price_dist = {}
        for restaurant in active_restaurants:
            price = restaurant.price_range.value
            price_dist[price] = price_dist.get(price, 0) + 1
        
        # 평균 평점 계산
        total_rating = sum(r.average_rating for r in active_restaurants)
        avg_rating = float(total_rating / len(active_restaurants))
        
        return {
            'total_count': len(active_restaurants),
            'average_rating': round(avg_rating, 2),
            'cuisine_distribution': cuisine_dist,
            'district_distribution': district_dist,
            'price_range_distribution': price_dist
        }
```

## 14.11 패키지 배포하기

### setup.py를 사용한 전통적 방식 (참고용)

공들여 만든 패키지를 다른 사람도 `pip install`이나 `uv add`로 설치할 수 있게 하려면 PyPI에 올려야 합니다. 예전에는 이 정보를 `setup.py`라는 **파이썬 코드**로 적었어요. 오래된 프로젝트에서 자주 마주치니 읽을 줄은 알아 두면 좋습니다. 이름, 버전, 의존성처럼 앞의 `pyproject.toml`과 같은 정보가 함수 인자로 들어가 있는 것이 보이죠?

```python
# setup.py (레거시 방식)
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="seoul-food-platform",
    version="1.0.0",
    author="김개발",
    author_email="dev@example.com",
    description="서울 음식점 검색 및 추천 플랫폼",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/seoul-food-platform",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "ruff>=0.1.0"],
        "web": ["fastapi>=0.100.0", "uvicorn>=0.23.0"],
    },
    entry_points={
        "console_scripts": [
            "seoul-food=seoul_food_platform.cli.main:main",
        ],
    },
)
```

### 현대적인 pyproject.toml (권장)

이미 앞에서 다룬 pyproject.toml이 현대적인 표준입니다. 추가적인 고급 설정을 살펴보겠습니다.

`setup.py`는 실행해야 내용을 알 수 있는 코드라서, 도구들이 정보를 읽으려면 일단 실행해 봐야 했습니다. `pyproject.toml`은 그냥 읽기만 하면 되는 설정 파일이라 어떤 도구든 같은 정보를 안전하게 가져다 쓸 수 있어요. 아래 예제는 길지만 구역마다 하는 일은 앞에서 본 것과 같습니다. 의존성 묶음이 더 세분되고(`dev`, `web`, `database`, `monitoring`), 빌드 도구와 코드 검사 도구의 설정이 더해졌을 뿐이에요.

```toml
# pyproject.toml (고급 설정)
[build-system]
requires = ["hatchling>=1.8.0"]
build-backend = "hatchling.build"

[project]
name = "seoul-food-platform"
version = "1.0.0"
description = "서울 음식점 검색 및 추천 플랫폼"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
authors = [
    {name = "김개발", email = "dev@example.com"},
]
maintainers = [
    {name = "이관리", email = "maintainer@example.com"},
]
keywords = ["restaurant", "seoul", "food", "recommendation"]

# PyPI 분류
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

# 핵심 의존성
dependencies = [
    "pydantic>=2.0.0,<3.0.0",
    "click>=8.0.0",
    "requests>=2.31.0",
    "python-dateutil>=2.8.0",
]

# 선택적 의존성 그룹
[project.optional-dependencies]
# 개발 도구
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.7.0",
    "ruff>=0.0.280",
    "mypy>=1.5.0",
    "pre-commit>=3.3.0",
]

# 웹 API 기능
web = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "python-multipart>=0.0.6",
    "python-jose[cryptography]>=3.3.0",
]

# 데이터베이스 연결
database = [
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.28.0",  # PostgreSQL
    "redis>=4.6.0",
]

# 모니터링 및 로깅
monitoring = [
    "prometheus-client>=0.17.0",
    "structlog>=23.1.0",
    "sentry-sdk>=1.29.0",
]

# 전체 기능 (모든 옵션 포함)
all = [
    "seoul-food-platform[web,database,monitoring]"
]

# 명령행 진입점
[project.scripts]
seoul-food = "seoul_food_platform.cli.main:main"

# GUI 애플리케이션 진입점 (있다면)
[project.gui-scripts]
seoul-food-gui = "seoul_food_platform.gui.main:main"

# 프로젝트 URL들
[project.urls]
Homepage = "https://github.com/username/seoul-food-platform"
Documentation = "https://seoul-food-platform.readthedocs.io/"
Repository = "https://github.com/username/seoul-food-platform.git"
"Bug Tracker" = "https://github.com/username/seoul-food-platform/issues"
Changelog = "https://github.com/username/seoul-food-platform/blob/main/CHANGELOG.md"

# Hatch 빌드 설정
[tool.hatch.build.targets.wheel]
packages = ["src/seoul_food_platform"]

[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/tests",
    "/docs",
    "/README.md",
    "/LICENSE",
    "/CHANGELOG.md",
]
exclude = [
    "/.github",
    "/scripts",
    "*.pyc",
    "__pycache__",
]

# 개발 환경 설정
[tool.hatch.envs.default]
dependencies = [
    "coverage[toml]>=6.5",
    "pytest",
]

[tool.hatch.envs.default.scripts]
test = "pytest {args:tests}"
test-cov = "coverage run -m pytest {args:tests}"
cov-report = ["- coverage combine", "coverage report"]
cov-html = ["- coverage combine", "coverage html"]

# 린팅 환경
[tool.hatch.envs.lint]
detached = true
dependencies = ["black>=23.1.0", "mypy>=1.0.0", "ruff>=0.0.243"]

[tool.hatch.envs.lint.scripts]
typing = "mypy --install-types --non-interactive {args:src/seoul_food_platform tests}"
style = ["ruff {args:.}", "black --check --diff {args:.}"]
fmt = ["black {args:.}", "ruff --fix {args:.}", "style"]
all = ["style", "typing"]

# 도구별 설정
[tool.black]
target-version = ["py310"]
line-length = 100
skip-string-normalization = true

[tool.ruff]
target-version = "py310"
line-length = 100
select = [
    "A",   # flake8-builtins
    "ARG", # flake8-unused-arguments  
    "B",   # flake8-bugbear
    "C",   # mccabe
    "DTZ", # flake8-datetimez
    "E",   # pycodestyle (Error)
    "EM",  # flake8-errmsg
    "F",   # pyflakes
    "FBT", # flake8-boolean-trap
    "I",   # isort
    "ICN", # flake8-import-conventions
    "N",   # pep8-naming
    "PLC", # pylint Convention
    "PLE", # pylint Error
    "PLR", # pylint Refactor
    "PLW", # pylint Warning
    "Q",   # flake8-quotes
    "RUF", # Ruff-specific rules
    "S",   # flake8-bandit
    "T",   # flake8-print
    "TID", # flake8-tidy-imports
    "UP",  # pyupgrade
    "W",   # pycodestyle (Warning)
    "YTT", # flake8-2020
]
ignore = [
    "FBT001", # Boolean positional arg in function definition
    "FBT002", # Boolean default value in function definition  
    "FBT003", # Boolean positional value in function call
]

[tool.ruff.per-file-ignores]
"tests/**/*" = ["PLR2004", "S101", "TID252"]

[tool.pytest.ini_options]
minversion = "6.0"
addopts = ["-ra", "--strict-markers", "--strict-config"]
xfail_strict = true
filterwarnings = ["error"]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.coverage.run]
source_pkgs = ["seoul_food_platform", "tests"]
branch = true
parallel = true
omit = ["src/seoul_food_platform/__about__.py"]

[tool.coverage.paths]
seoul_food_platform = ["src/seoul_food_platform", "*/seoul-food-platform/src/seoul_food_platform"]
tests = ["tests", "*/seoul-food-platform/tests"]

[tool.coverage.report]
exclude_lines = [
    "no cov",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

### 배포 프로세스

배포는 "검사 → 테스트 → 버전 올리기 → 빌드 → 연습 배포 → 진짜 배포" 순서로 진행합니다. 8번의 TestPyPI는 진짜 PyPI와 똑같이 생긴 **연습용 저장소**예요. 여기에 먼저 올려서 설치까지 잘 되는지 확인한 다음 진짜로 올립니다. 앞에서 말했듯 PyPI에 한 번 올린 버전 번호는 되돌릴 수 없으니까요.

```bash
# 1. 개발 환경 설정
uv sync --extra dev

# 2. 코드 품질 검사
uv run ruff check src tests
uv run black --check src tests
uv run mypy src

# 3. 테스트 실행
uv run pytest --cov=seoul_food_platform

# 4. 버전 업데이트 (수동 또는 자동화)
# pyproject.toml의 version을 업데이트

# 5. 패키지 빌드
uv build

# 6. 빌드 결과 확인
ls -la dist/
# seoul_food_platform-1.0.0-py3-none-any.whl
# seoul_food_platform-1.0.0.tar.gz

# 7. 로컬 테스트 설치
uv pip install dist/seoul_food_platform-1.0.0-py3-none-any.whl

# 8. TestPyPI에 업로드 (테스트용)
uv publish --publish-url https://test.pypi.org/legacy/

# 9. TestPyPI에서 설치 테스트
pip install --index-url https://test.pypi.org/simple/ seoul-food-platform

# 10. 실제 PyPI에 배포
uv publish
```

### GitHub Actions를 통한 자동화

이 순서를 매번 손으로 하다 보면 언젠가 한 단계를 빼먹습니다. GitHub Actions는 저장소에 어떤 일이 생겼을 때 정해 둔 명령을 GitHub 서버가 대신 실행해 주는 서비스예요. 아래 설정은 `v1.0.0`처럼 `v`로 시작하는 태그를 올리면, 먼저 파이썬 3.10, 3.11, 3.12 세 버전에서 검사와 테스트를 돌리고(`test`), 모두 통과했을 때만(`needs: test`) 빌드해서 PyPI에 올립니다. PyPI 토큰은 파일에 적지 않고 `secrets.PYPI_TOKEN`으로 GitHub의 비밀 저장소에서 꺼내 쓰는 것도 눈여겨보세요.

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v10
      with:
        version: "latest"
    
    - name: Set up Python
      run: uv python install ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: uv sync --all-extras
    
    - name: Run tests
      run: |
        uv run ruff check src tests
        uv run black --check src tests  
        uv run mypy src
        uv run pytest --cov=seoul_food_platform

  build-and-publish:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v10
    
    - name: Build package
      run: uv build
    
    - name: Publish to PyPI
      env:
        UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
      run: uv publish
```

## 정리 및 베스트 프랙티스

### 모듈과 패키지 사용 가이드라인

이 장에서 본 규칙들을 모듈 하나에 모아 보면 아래와 같은 모양이 됩니다. 위에서부터 읽으면 모듈 파일의 표준 순서이기도 해요. docstring으로 시작해서, `import`를 PEP 8 순서(표준 라이브러리 → 외부 라이브러리 → 내 프로젝트, 묶음 사이는 한 줄 띄우기)로 적고, 공개 목록 `__all__`, 상수, 함수와 클래스를 차례로 두고, 맨 끝에 직접 실행할 때만 도는 `if __name__ == '__main__':`을 둡니다. 이 파일은 패키지 안에 두는 것을 전제로 상대 import(`from .models ...`)를 쓰고 있어서, 14.6절에서 본 것처럼 파일만 따로 실행하면 에러가 납니다.

```python
# src/seoul_food_platform/best_practices_demo.py
# 패키지 안 모듈이라 실행은: uv run python -m seoul_food_platform.best_practices_demo
"""모듈과 패키지 베스트 프랙티스"""

# 1. Import 순서 (PEP 8)
# 표준 라이브러리
import os
import sys
from pathlib import Path
from typing import List, Dict

# 외부 라이브러리 (이 파일은 쓰지 않아 비워 둠 — 쓰지 않는 import는 넣지 않는다)

# 로컬 애플리케이션 (같은 패키지 안의 모듈)
from .services.restaurant_service import RestaurantService

# 2. __all__ 사용하여 public API 명시
__all__ = ['RestaurantManager', 'setup_logging']

# 3. 모듈 레벨 상수
DEFAULT_CONFIG_FILE = Path.home() / '.seoul-food' / 'config.json'
MAX_RETRY_ATTEMPTS = 3

# 4. 모듈 초기화 함수
def setup_logging(level: str = 'INFO'):
    """로깅 설정"""
    import logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# 5. 메인 클래스
class RestaurantManager:
    """레스토랑 관리자 - 모듈의 메인 인터페이스"""
    
    def __init__(self, config_file: Path = DEFAULT_CONFIG_FILE):
        self.config_file = config_file
        self.service = RestaurantService()
        self._load_config()
    
    def _load_config(self):
        """설정 로드 (private 메서드)"""
        if self.config_file.exists():
            # 설정 로드 로직
            pass

# 6. 모듈이 직접 실행될 때의 동작
if __name__ == '__main__':
    # 간단한 테스트나 유틸리티 실행
    setup_logging('DEBUG')
    manager = RestaurantManager()
    print("레스토랑 관리자가 초기화되었습니다.")
```

### PEP 8 검사기로 스타일 점검하기

이름 규칙, 띄어쓰기, `import` 순서까지 사람이 매번 눈으로 확인하기는 어렵습니다. 그래서 PEP 8을 지켰는지 자동으로 검사해 주는 도구를 씁니다. 대표적인 것이 `pycodestyle`이에요(예전 이름은 `pep8`이었습니다). 일부러 규칙을 어긴 파일을 하나 만들어 검사해 보겠습니다.

```python
# messy.py
import os, sys
def 합계( a,b ):
    return a+b
class cafe:
    pass
```

```bash
uv run --with pycodestyle pycodestyle messy.py
```

`uv run --with 패키지`는 프로젝트에 설치하지 않고 그 실행에만 잠깐 패키지를 빌려 쓰는 방법입니다. 결과는 `파일:줄:칸: 코드 설명` 형식으로 나옵니다(pycodestyle 2.15.0).

```
messy.py:2:10: E401 multiple imports on one line
messy.py:3:1: E302 expected 2 blank lines, found 0
messy.py:3:8: E201 whitespace after '('
messy.py:3:10: E231 missing whitespace after ','
messy.py:3:12: E202 whitespace before ')'
messy.py:5:1: E302 expected 2 blank lines, found 0
```

한 줄에 `import`를 두 개 했다(E401), 함수와 클래스 앞에 빈 줄 두 개가 없다(E302), 괄호 안쪽에 쓸데없는 공백이 있다(E201, E202), 쉼표 뒤에 공백이 없다(E231)는 지적입니다. 그런데 `class cafe`처럼 클래스 이름을 소문자로 지은 것은 지적하지 않았죠? `pycodestyle`은 공백과 배치 같은 **모양**을 보는 도구라서 이름 규칙은 검사하지 않습니다. 이름까지 검사하고 싶다면 14.8절의 `pyproject.toml`에 설정해 둔 `ruff`를 쓰세요. `ruff`는 이름 규칙(`N`으로 시작하는 규칙)까지 함께 검사해서, 같은 파일에서 ``N801 Class name `cafe` should use CapWords convention``을 찾아냅니다. 고칠 수 있는 것은 자동으로 고쳐 주기도 해요.

### 실전 팁들

마지막으로 알아 두면 쓸모 있는 도구 다섯 가지입니다. 모두 표준 라이브러리만으로 만들었어요.

- `importlib.import_module`: 모듈 이름을 **문자열로** 받아 불러옵니다. 실행 중에 어떤 플러그인을 쓸지 정할 때 유용합니다.
- `importlib.reload`: 이미 불러온 모듈을 다시 읽어 들입니다. 앞의 Q&A에서 본 것처럼 `import`는 한 번만 실행되니까요.
- `inspect`: 모듈 안의 함수와 클래스를 살펴보고 함수의 매개변수 모양(시그니처)까지 보여 줍니다.
- 패키지 구조 출력: `__init__.py`가 있는 폴더를 따라 내려가며 트리를 그립니다.
- 순환 import 감지: A가 B를 부르고 B가 다시 A를 부르는 **순환 import**는 앞에서 본 "partially initialized module" 에러의 흔한 원인입니다. `ast` 모듈로 소스 코드를 읽어 서로 부르는 쌍을 찾아요. 주석에도 적혀 있듯 두 모듈이 서로 직접 부르는 경우만 잡는 간단한 버전입니다.

```python
# practical_tips.py
"""실전에서 유용한 팁들"""

import sys
import importlib
import inspect
from pathlib import Path

# 1. 동적 모듈 로딩
def load_plugin(plugin_name: str, plugin_dir: Path):
    """플러그인 동적 로딩"""
    sys.path.insert(0, str(plugin_dir))
    try:
        module = importlib.import_module(plugin_name)
        return module
    except ImportError as e:
        print(f"플러그인 로딩 실패: {e}")
        return None
    finally:
        if str(plugin_dir) in sys.path:
            sys.path.remove(str(plugin_dir))

# 2. 모듈 리로딩 (개발 시 유용)
def reload_module(module):
    """모듈 리로딩"""
    return importlib.reload(module)

# 3. 모듈 정보 탐색
def inspect_module(module):
    """모듈 내용 탐색"""
    print(f"=== {module.__name__} 모듈 정보 ===")
    
    # 모든 속성 나열
    for name in dir(module):
        if not name.startswith('_'):
            obj = getattr(module, name)
            obj_type = type(obj).__name__
            
            # 함수인 경우 시그니처도 표시
            if inspect.isfunction(obj):
                sig = inspect.signature(obj)
                print(f"함수: {name}{sig}")
            elif inspect.isclass(obj):
                print(f"클래스: {name}")
                # 클래스 메서드들도 표시
                for method_name in dir(obj):
                    if not method_name.startswith('_'):
                        method = getattr(obj, method_name)
                        if inspect.ismethod(method) or inspect.isfunction(method):
                            print(f"  메서드: {method_name}")
            else:
                print(f"{obj_type}: {name}")

# 4. 패키지 구조 시각화
def print_package_structure(package_path: Path, prefix: str = ""):
    """패키지 구조를 트리 형태로 출력"""
    if not package_path.is_dir():
        return
    
    items = sorted(package_path.iterdir())
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        
        if item.is_dir() and (item / "__init__.py").exists():
            print(f"{prefix}{current_prefix}{item.name}/")
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_package_structure(item, next_prefix)
        elif item.suffix == '.py':
            print(f"{prefix}{current_prefix}{item.name}")
        elif item.is_dir():
            print(f"{prefix}{current_prefix}{item.name}/")

# 5. 순환 import 감지 (간단한 버전)
def find_circular_imports(package_path: Path):
    """순환 import 감지"""
    import ast
    
    imports = {}  # 파일별 import 목록
    
    for py_file in package_path.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            file_imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        file_imports.append(node.module)
            
            imports[py_file.stem] = file_imports
            
        except Exception as e:
            print(f"파일 파싱 오류 {py_file}: {e}")
    
    # 간단한 순환 감지 (실제로는 더 복잡한 알고리즘 필요)
    for module, module_imports in imports.items():
        for imported in module_imports:
            if imported in imports:
                imported_imports = imports[imported]
                if module in [imp.split('.')[-1] for imp in imported_imports]:
                    print(f"[!] 순환 import 감지: {module} ↔ {imported}")

if __name__ == "__main__":
    # 예제 실행
    print("=== 패키지 구조 출력 ===")
    seoul_pkg = Path("seoul_restaurants")
    if seoul_pkg.exists():
        print_package_structure(seoul_pkg)
    
    print("\n=== 순환 import 검사 ===") 
    find_circular_imports(Path("seoul_restaurants"))
```

`seoul_restaurants` 폴더 옆에서 실행하면 앞에서 그렸던 것과 같은 트리가 출력됩니다. 한 번이라도 패키지를 불러온 적이 있다면 폴더마다 `__pycache__/`도 보일 텐데, 파이썬이 모듈을 다음에 더 빨리 불러오려고 컴파일해 둔 파일을 보관하는 곳이에요. 지워도 다시 만들어지니 걱정하지 않아도 되고, 보통 git에는 올리지 않습니다. 우리 패키지에는 순환 import가 없으니 검사 결과 아래에는 아무것도 찍히지 않습니다.

이제 Chapter 14: 모듈과 패키지가 완성되었습니다. 이 챕터에서는 다음 내용들을 다뤘습니다:

1. **모듈 기초** - 모듈 생성과 기본 개념
2. **Import 방법들** - import, from import, as 사용법
3. **패키지 구조** - 실전 프로젝트 구조 설계
4. **고급 기능** - 상대/절대 import, 모듈 검색 경로
5. **uv 활용** - 현대적인 패키지 관리 방법
6. **내장 모듈** - 자주 사용하는 표준 라이브러리들
7. **배포** - pyproject.toml을 통한 패키지 배포
8. **베스트 프랙티스** - 실무에서 유용한 팁들

모든 예제는 한국어 컨텍스트(서울 맛집, 한국 지명 등)를 사용하여 실생활과 연관된 이해하기 쉬운 내용으로 구성했습니다.
