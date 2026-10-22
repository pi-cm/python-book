# Chapter 12: 파일과 예외 처리

> **학습 목표**  
> - 파일 입출력의 기본 개념과 다양한 방법 습득
> - pathlib을 활용한 현대적 파일 경로 관리
> - 예외 처리를 통한 안정적인 프로그램 작성
> - 컨텍스트 매니저로 리소스 안전 관리
> - CSV, JSON 등 다양한 파일 형식 처리
> - 한국어 인코딩 문제 해결

---

## 들어가며: 프로그램이 끝나도 남는 것

지금까지 만든 변수와 객체는 프로그램이 끝나는 순간 모두 사라집니다. 변수는 컴퓨터의 메모리에 잠깐 놓여 있다가, 프로그램이 끝나면 그 자리를 비워 주거든요. 칠판에 적은 글씨를 수업이 끝나면 지우는 것과 같습니다. 오늘 계산한 성적을 내일도 보고 싶다면 칠판이 아니라 공책에 옮겨 적어야 하죠. 컴퓨터의 공책이 바로 **파일**입니다.

파일은 디스크에 저장되고, 컴퓨터는 그 많은 파일을 폴더 안의 폴더 안의 폴더로 정리해 둡니다. 이 정리 체계를 **파일 시스템**이라고 해요. 그래서 파일을 다루려면 두 가지를 알아야 합니다. 파일에 **무엇을 어떻게** 적고 읽는지(12.1), 그리고 그 파일이 **어디에** 있는지(12.2)죠.

파일을 다루기 시작하면 예상하지 못한 일도 함께 찾아옵니다. 열려는 파일이 없거나, 다른 프로그램이 쓰고 있거나, 숫자가 있어야 할 자리에 글자가 들어 있거나요. 이런 상황에서 프로그램이 그냥 멈춰 버리지 않고 침착하게 대처하게 만드는 기술이 **예외 처리**입니다. 이 장의 후반부(12.3~12.4)에서 다루고, 마지막으로 표 형태의 CSV와 구조가 있는 JSON 파일을 읽고 쓰며 둘을 함께 써 봅니다.

## 12.1 파일 입출력 기본

### 기본 파일 읽기/쓰기

파일을 다루는 순서는 공책을 쓰는 순서와 같습니다. 공책을 **펴고**(`open`), **쓰거나 읽고**(`write`, `read`), 다 쓰면 **덮습니다**(`close`). `open()`의 두 번째 인자는 무엇을 할지 정하는 모드예요. `"w"`는 쓰기, `"r"`은 읽기입니다.

덮는 걸 깜빡하면 어떻게 될까요? 쓴 내용이 디스크에 다 옮겨지지 않았을 수도 있고, 열린 파일이 계속 자원을 붙잡고 있게 됩니다. 중간에 에러가 나서 `close()`까지 가지 못하는 경우도 있고요. 그래서 요즘은 아래 두 번째 함수처럼 `with open(...) as file:`로 씁니다. 11장에서 본 컨텍스트 매니저라서 `with` 블록을 빠져나오는 순간 무슨 일이 있었든 파일이 자동으로 닫혀요.

`encoding="utf-8"`도 매번 적어 주는 습관을 들이세요. 이걸 빼면 파이썬은 운영체제에 설정된 기본 인코딩을 쓰는데, 그 값이 컴퓨터마다 다를 수 있습니다. 내 컴퓨터에서 잘 읽히던 한글 파일이 다른 컴퓨터에서 깨지는 일을 막는 가장 쉬운 방법이에요.

```python
# 전통적인 파일 처리 방식
def traditional_file_handling():
    """전통적인 파일 처리"""
    # 파일 쓰기
    file = open("korean_greeting.txt", "w", encoding="utf-8")
    file.write("안녕하세요!\n")
    file.write("파이썬 파일 처리를 배우고 있습니다.\n")
    file.close()
    
    # 파일 읽기
    file = open("korean_greeting.txt", "r", encoding="utf-8")
    content = file.read()
    file.close()
    
    print("파일 내용:")
    print(content)

# 현대적인 파일 처리 방식 (권장)
def modern_file_handling():
    """컨텍스트 매니저를 사용한 현대적 파일 처리"""
    
    # 파일 쓰기
    with open("korean_modern.txt", "w", encoding="utf-8") as file:
        file.write("파이썬으로 한글 파일 처리하기\n")
        file.write("=" * 30 + "\n")
        
        korean_data = [
            "이름: 김철수",
            "나이: 25세", 
            "직업: 소프트웨어 개발자",
            "관심사: 파이썬, 데이터 분석, 웹 개발"
        ]
        
        for line in korean_data:
            file.write(f"{line}\n")
    
    # 파일 읽기 (전체)
    with open("korean_modern.txt", "r", encoding="utf-8") as file:
        content = file.read()
        print("전체 파일 내용:")
        print(content)
    
    # 파일 읽기 (줄별)
    print("\n줄별 읽기:")
    with open("korean_modern.txt", "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
            print(f"줄 {line_number}: {line.strip()}")

# 다양한 파일 읽기 방법
def various_reading_methods():
    """다양한 파일 읽기 방법 시연"""
    
    # 테스트 파일 생성
    test_content = """첫 번째 줄입니다.
두 번째 줄에는 한글이 있습니다.
세 번째 줄: 숫자 12345
네 번째 줄: 특수문자 !@#$%
다섯 번째 줄입니다."""
    
    with open("test_reading.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("1. read() - 전체 내용:")
    with open("test_reading.txt", "r", encoding="utf-8") as f:
        content = f.read()
        print(repr(content))
    
    print("\n2. readline() - 한 줄씩:")
    with open("test_reading.txt", "r", encoding="utf-8") as f:
        line_count = 0
        while True:
            line = f.readline()
            if not line:  # 파일 끝
                break
            line_count += 1
            print(f"줄 {line_count}: {repr(line)}")
    
    print("\n3. readlines() - 모든 줄을 리스트로:")
    with open("test_reading.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            print(f"줄 {i}: {repr(line)}")
    
    print("\n4. 이터레이터 방식 (권장):")
    with open("test_reading.txt", "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            print(f"줄 {i}: {line.strip()}")

# 한글 인코딩 처리
def korean_encoding_demo():
    """한글 인코딩 처리 시연"""
    
    korean_text = """안녕하세요! 
한글 인코딩 테스트입니다.
UTF-8: 유니코드 표준 인코딩
CP949: 윈도우 한글 인코딩
EUC-KR: 구 한글 인코딩"""
    
    # UTF-8로 저장 (권장)
    with open("korean_utf8.txt", "w", encoding="utf-8") as f:
        f.write(korean_text)
    
    # CP949로 저장 (윈도우 호환용)
    with open("korean_cp949.txt", "w", encoding="cp949") as f:
        f.write(korean_text)
    
    print("인코딩별 파일 크기:")
    import os
    utf8_size = os.path.getsize("korean_utf8.txt")
    cp949_size = os.path.getsize("korean_cp949.txt")
    
    print(f"UTF-8: {utf8_size} bytes")
    print(f"CP949: {cp949_size} bytes")
    
    # 잘못된 인코딩으로 읽기 시도
    print("\n인코딩 오류 시연:")
    try:
        with open("korean_utf8.txt", "r", encoding="ascii") as f:
            content = f.read()
    except UnicodeDecodeError as e:
        print(f"[X] ASCII로 UTF-8 파일 읽기 실패: {e}")
    
    # 올바른 인코딩으로 읽기
    with open("korean_utf8.txt", "r", encoding="utf-8") as f:
        content = f.read()
        print(f"[O] UTF-8로 올바르게 읽음:\n{content}")

# 실행
print("=== 전통적인 파일 처리 ===")
traditional_file_handling()

print("\n=== 현대적인 파일 처리 ===")
modern_file_handling()

print("\n=== 다양한 읽기 방법 ===")
various_reading_methods()

print("\n=== 한글 인코딩 처리 ===")
korean_encoding_demo()
```

**읽는 방법 네 가지**의 출력을 비교해 보세요. `read()`는 파일 전체를 문자열 하나로, `readlines()`는 줄마다 끊은 리스트로 한 번에 가져옵니다. `readline()`은 부를 때마다 한 줄씩 가져오다가 파일 끝에 닿으면 빈 문자열 `''`을 돌려줘서 `if not line: break`로 멈출 수 있어요. 각 줄 끝에 `'\n'`이 붙어 있고 마지막 줄에만 없는 것도 보이죠? 파일에 적힌 줄바꿈 문자까지 그대로 읽기 때문입니다. 화면에 찍을 때 `strip()`으로 떼어 낸 이유예요.

네 번째인 `for line in f:`가 권장 방식인 이유는 메모리입니다. `read()`나 `readlines()`는 파일 전체를 메모리에 올리지만, 파일 객체를 `for`로 돌면 한 줄씩 읽어 오거든요. 몇 GB짜리 로그 파일도 이 방식이면 문제없습니다.

**인코딩** 부분에서는 같은 글을 저장했는데 UTF-8 파일이 154바이트, CP949 파일이 115바이트로 크기가 다릅니다. 글자 하나를 몇 바이트로 적느냐가 인코딩마다 다르기 때문이에요.

```python
for text in ["A", "가", "漢"]:
    print(text, len(text.encode("utf-8")), len(text.encode("cp949")))
# A 1 1
# 가 3 2
# 漢 3 2
```

UTF-8은 영문·숫자를 1바이트로, 한글과 한자를 3바이트로 적습니다. 자주 쓰는 영문에 짧은 자리를, 나머지에 긴 자리를 주는 가변 길이 방식이라 전 세계 모든 글자를 한 파일에 담을 수 있고, 영문만 있는 파일은 옛날 ASCII 파일과 완전히 똑같아요. 윈도우에서 오래 쓰인 CP949는 한글을 2바이트로 적는 대신 한국어 밖의 많은 글자를 담지 못합니다. 프랑스어의 `é`만 해도 CP949로 저장하려 하면 `UnicodeEncodeError`가 나요. 그래서 새로 만드는 파일은 UTF-8이 기본입니다.

마지막으로 UTF-8 파일을 `encoding="ascii"`로 읽으려 하자 `UnicodeDecodeError`가 났습니다. 메시지의 `byte 0xec in position 0`은 첫 글자 "안"을 UTF-8로 적은 첫 바이트가 `0xEC`인데, ASCII는 128(`0x80`) 이상의 바이트를 모른다는 뜻이에요. 한글이 깨져 보이거나 이 에러가 나면 **저장할 때와 읽을 때의 인코딩이 같은지**부터 확인하세요.

### 파일 모드와 옵션

`open()`의 모드는 생각보다 많습니다. 특히 `"w"`는 파일이 이미 있으면 **내용을 싹 비우고** 시작한다는 점을 꼭 기억하세요. 실수로 소중한 파일을 날리는 가장 흔한 원인입니다.

| 모드 | 뜻 | 파일이 없으면 | 파일이 있으면 |
|---|---|---|---|
| `"r"` | 읽기 (기본값) | `FileNotFoundError` | 처음부터 읽음 |
| `"w"` | 쓰기 | 새로 만듦 | **내용을 비우고** 씀 |
| `"a"` | 이어 쓰기 | 새로 만듦 | 끝에 덧붙임 |
| `"x"` | 새로 만들어 쓰기 | 새로 만듦 | `FileExistsError` |
| `"r+"` | 읽기와 쓰기 | `FileNotFoundError` | 내용 유지 |
| `"w+"` | 쓰기와 읽기 | 새로 만듦 | **내용을 비움** |

여기에 `"b"`를 붙이면(`"rb"`, `"wb"`) 글자가 아니라 **바이트** 그대로 읽고 씁니다. 이미지, 음악, 압축 파일처럼 글자가 아닌 파일을 다룰 때 쓰고, 이때는 `encoding`을 주지 않아요.

```python
import os
from pathlib import Path

def file_modes_demo():
    """파일 모드 시연"""
    
    test_file = "mode_test.txt"
    
    # 1. 'w' 모드: 쓰기 (기존 파일 덮어쓰기)
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("첫 번째 내용\n")
    
    # 2. 'a' 모드: 추가 (기존 파일 끝에 추가)
    with open(test_file, "a", encoding="utf-8") as f:
        f.write("두 번째 내용 (추가)\n")
        f.write("세 번째 내용 (추가)\n")
    
    # 3. 'r' 모드: 읽기 (기본값)
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
        print(f"'a' 모드 후 파일 내용:\n{content}")
    
    # 4. 'x' 모드: 배타적 생성 (파일이 이미 있으면 오류)
    exclusive_file = "exclusive_test.txt"
    
    try:
        with open(exclusive_file, "x", encoding="utf-8") as f:
            f.write("배타적 생성 모드 테스트\n")
        print("[O] 'x' 모드로 새 파일 생성 성공")
    except FileExistsError:
        print("[X] 'x' 모드: 파일이 이미 존재함")
    
    # 같은 파일을 다시 'x' 모드로 열려고 시도
    try:
        with open(exclusive_file, "x", encoding="utf-8") as f:
            f.write("이 내용은 쓰여지지 않음\n")
    except FileExistsError:
        print("[X] 'x' 모드: 기존 파일이 있어서 실패")
    
    # 5. 'r+' 모드: 읽기/쓰기
    with open(test_file, "r+", encoding="utf-8") as f:
        # 파일 시작 부분에서 읽기
        original_content = f.read()
        print(f"'r+' 모드 - 원본 내용:\n{original_content}")
        
        # 파일 끝에 추가
        f.write("네 번째 내용 (r+ 모드)\n")
    
    # 6. 'w+' 모드: 읽기/쓰기 (기존 파일 덮어쓰기)
    with open("rw_test.txt", "w+", encoding="utf-8") as f:
        f.write("w+ 모드 테스트\n")
        f.write("읽기와 쓰기 모두 가능\n")
        
        # 파일 포인터를 시작으로 이동
        f.seek(0)
        content = f.read()
        print(f"'w+' 모드로 쓴 후 읽기:\n{content}")
    
    # 정리
    for file in [test_file, exclusive_file, "rw_test.txt"]:
        if os.path.exists(file):
            os.remove(file)

def binary_file_demo():
    """바이너리 파일 처리 시연"""
    
    # 바이너리 데이터 생성 (간단한 이미지 데이터 시뮬레이션)
    binary_data = bytes([0xFF, 0xD8, 0xFF, 0xE0] + list(range(100)))
    
    # 바이너리 쓰기
    with open("test_binary.dat", "wb") as f:
        f.write(binary_data)
        f.write(b"\x00\x01\x02\x03")  # 추가 바이너리 데이터
    
    # 바이너리 읽기
    with open("test_binary.dat", "rb") as f:
        read_data = f.read()
        print(f"바이너리 파일 크기: {len(read_data)} bytes")
        print(f"첫 10바이트: {read_data[:10]}")
        print(f"마지막 4바이트: {read_data[-4:]}")
    
    # 바이너리와 텍스트 혼합 처리
    mixed_data = {
        "header": "한글 헤더 정보",
        "binary_data": binary_data,
        "footer": "푸터 정보"
    }
    
    # 텍스트 부분은 UTF-8, 바이너리는 그대로
    with open("mixed_data.bin", "wb") as f:
        # 헤더 쓰기 (UTF-8 인코딩)
        header_bytes = mixed_data["header"].encode("utf-8")
        f.write(len(header_bytes).to_bytes(4, byteorder='big'))  # 헤더 길이 (4바이트)
        f.write(header_bytes)
        
        # 바이너리 데이터 쓰기
        f.write(len(mixed_data["binary_data"]).to_bytes(4, byteorder='big'))  # 데이터 길이
        f.write(mixed_data["binary_data"])
        
        # 푸터 쓰기
        footer_bytes = mixed_data["footer"].encode("utf-8")
        f.write(len(footer_bytes).to_bytes(4, byteorder='big'))  # 푸터 길이
        f.write(footer_bytes)
    
    # 혼합 데이터 읽기
    with open("mixed_data.bin", "rb") as f:
        # 헤더 읽기
        header_length = int.from_bytes(f.read(4), byteorder='big')
        header = f.read(header_length).decode("utf-8")
        
        # 바이너리 데이터 읽기  
        data_length = int.from_bytes(f.read(4), byteorder='big')
        binary_data = f.read(data_length)
        
        # 푸터 읽기
        footer_length = int.from_bytes(f.read(4), byteorder='big')
        footer = f.read(footer_length).decode("utf-8")
        
        print(f"\n혼합 파일 읽기 결과:")
        print(f"헤더: {header}")
        print(f"바이너리 데이터 크기: {len(binary_data)} bytes")
        print(f"푸터: {footer}")
    
    # 정리
    for file in ["test_binary.dat", "mixed_data.bin"]:
        if os.path.exists(file):
            os.remove(file)

# 실행
print("=== 파일 모드 시연 ===")
file_modes_demo()

print("\n=== 바이너리 파일 처리 ===")
binary_file_demo()
```

`"x"` 모드는 같은 파일을 두 번째로 열 때 `FileExistsError`를 내며 실패했습니다. "없을 때만 새로 만든다"가 보장되니, 남의 파일을 덮어쓰면 안 되는 곳에서 `"w"` 대신 쓰면 안전해요. `"r+"`로 연 파일은 `read()`로 끝까지 읽고 나면 **읽은 위치**가 파일 끝에 가 있어서, 이어서 `write()`한 내용이 끝에 붙습니다. 파일 객체는 지금 어디를 읽고 쓰는지 가리키는 위치를 하나 갖고 있고, `"w+"` 예제의 `f.seek(0)`은 그 위치를 맨 앞으로 되돌려 방금 쓴 내용을 다시 읽게 한 거예요.

바이너리 예제의 첫 파일은 108바이트입니다. 앞의 4바이트(`0xFF 0xD8 0xFF 0xE0`)에 0~99의 100바이트, 마지막에 4바이트를 더 썼으니까요. 두 번째 파일은 한글 헤더, 바이트 데이터, 푸터를 한 파일에 섞어 담는데, 바이트만 늘어놓으면 어디까지가 헤더인지 알 수가 없죠. 그래서 각 덩어리 앞에 **길이를 4바이트로 먼저 적어 두고**(`to_bytes(4, byteorder='big')`), 읽을 때는 길이부터 읽은 다음 그만큼만 읽습니다. 많은 파일 형식과 통신 규약이 이런 "길이 먼저, 내용 다음" 방식을 씁니다.

## 12.2 pathlib을 활용한 현대적 파일 관리

### pathlib 기본 사용법

파일을 열려면 그 파일이 어디 있는지 알려 줘야 합니다. 주소를 알려 주는 방법은 두 가지예요.

- **절대 경로**: 맨 꼭대기(루트)부터 전부 적은 주소입니다. `/Users/username/Documents/report.txt`나 `C:\Users\username\Documents\report.txt`처럼요. "대한민국 서울시 ○○구 ○○로 12"처럼 어디서 출발하든 같은 곳을 가리킵니다.
- **상대 경로**: 지금 있는 폴더(현재 작업 디렉터리)를 기준으로 한 주소입니다. `data/report.txt`는 "여기 안의 data 폴더 안", `../report.txt`는 "한 단계 위 폴더"예요. "여기서 두 블록 가서 왼쪽"처럼 출발점이 바뀌면 가리키는 곳도 바뀝니다.

예전에는 경로를 문자열로 이어 붙이고 `os.path` 함수들로 다뤘지만, 지금은 경로를 **객체**로 다루는 `pathlib.Path`를 씁니다. 가장 눈에 띄는 건 `/` 연산자로 경로를 잇는다는 점이에요. `Path.cwd() / "data" / "korean_files"`처럼요. 11장에서 본 매직 메서드 기억나죠? `Path`가 나눗셈 연산자 `__truediv__`를 "경로 잇기"라는 뜻으로 다시 정의해 둔 겁니다. 윈도우는 `\`, 맥과 리눅스는 `/`로 폴더를 구분하는데, `Path`가 운영체제에 맞게 알아서 바꿔 주니 같은 코드가 어디서나 동작해요.

```python
from pathlib import Path
import os
import shutil
from datetime import datetime

def pathlib_basics():
    """pathlib 기본 사용법"""
    
    # 경로 생성 (운영체제 독립적)
    current_dir = Path.cwd()  # 현재 작업 디렉터리
    home_dir = Path.home()   # 홈 디렉터리
    
    print(f"현재 디렉터리: {current_dir}")
    print(f"홈 디렉터리: {home_dir}")
    
    # 경로 조합 (/ 연산자 사용)
    data_dir = current_dir / "data" / "korean_files"
    config_file = current_dir / "config" / "settings.json"
    
    print(f"데이터 디렉터리: {data_dir}")
    print(f"설정 파일: {config_file}")
    
    # 경로 정보 추출
    sample_path = Path("/Users/username/Documents/projects/python_book/chapter01.md")
    
    print(f"\n경로 정보 추출:")
    print(f"전체 경로: {sample_path}")
    print(f"파일명: {sample_path.name}")
    print(f"확장자: {sample_path.suffix}")
    print(f"확장자 제외 이름: {sample_path.stem}")
    print(f"부모 디렉터리: {sample_path.parent}")
    print(f"모든 부모: {list(sample_path.parents)}")
    print(f"루트: {sample_path.anchor}")
    print(f"경로 부분들: {sample_path.parts}")
    
    # 절대경로와 상대경로
    relative_path = Path("docs/korean/tutorial.md")
    absolute_path = relative_path.resolve()
    
    print(f"\n경로 변환:")
    print(f"상대 경로: {relative_path}")
    print(f"절대 경로: {absolute_path}")
    print(f"상대 경로 여부: {relative_path.is_absolute()}")
    print(f"절대 경로 여부: {absolute_path.is_absolute()}")

def pathlib_file_operations():
    """pathlib을 이용한 파일 작업"""
    
    # 작업 디렉터리 생성
    work_dir = Path("pathlib_demo")
    work_dir.mkdir(exist_ok=True)
    
    # 중첩 디렉터리 생성
    korean_dir = work_dir / "korean_docs" / "tutorials" 
    korean_dir.mkdir(parents=True, exist_ok=True)
    
    # 파일 생성 및 쓰기
    tutorial_file = korean_dir / "파이썬_기초.md"
    tutorial_content = """# 파이썬 기초 튜토리얼

## 1. 소개
파이썬은 배우기 쉽고 강력한 프로그래밍 언어입니다.

## 2. 변수와 데이터 타입
- 정수형: int
- 실수형: float  
- 문자열: str
- 불린형: bool

## 3. 한글 처리
파이썬은 유니코드를 지원하므로 한글 처리가 용이합니다.
"""
    
    tutorial_file.write_text(tutorial_content, encoding="utf-8")
    
    # 파일 정보 확인
    print(f"파일 생성: {tutorial_file}")
    print(f"파일 존재: {tutorial_file.exists()}")
    print(f"파일 여부: {tutorial_file.is_file()}")
    print(f"디렉터리 여부: {tutorial_file.is_dir()}")
    print(f"파일 크기: {tutorial_file.stat().st_size} bytes")
    
    # 파일 시간 정보
    stat = tutorial_file.stat()
    changed_time = datetime.fromtimestamp(stat.st_ctime)  # 맥·리눅스: 상태 변경 시각, 윈도우: 생성 시각
    modified_time = datetime.fromtimestamp(stat.st_mtime)
    
    print(f"상태 변경 시간(st_ctime): {changed_time}")
    print(f"수정 시간: {modified_time}")
    
    # 파일 읽기
    content = tutorial_file.read_text(encoding="utf-8")
    print(f"\n파일 내용 (첫 100자):")
    print(content[:100] + "...")
    
    # 파일 복사
    backup_file = korean_dir / "파이썬_기초_백업.md"
    backup_file.write_text(content, encoding="utf-8")
    
    # 파일명 변경
    new_name = korean_dir / "Python_기초_한글.md"
    tutorial_file.rename(new_name)
    
    print(f"파일명 변경: {tutorial_file} → {new_name}")
    
    # 디렉터리 내용 탐색
    print(f"\n{korean_dir} 디렉터리 내용:")
    for item in korean_dir.iterdir():
        if item.is_file():
            print(f"{item.name} ({item.stat().st_size} bytes)")
        elif item.is_dir():
            print(f"{item.name}/")
    
    # 패턴 매칭으로 파일 찾기
    print(f"\n마크다운 파일 찾기:")
    for md_file in korean_dir.glob("*.md"):
        print(f"  {md_file.name}")
    
    # 재귀적 검색
    print(f"\n모든 마크다운 파일 (재귀 검색):")
    for md_file in work_dir.rglob("*.md"):
        relative_path = md_file.relative_to(work_dir)
        print(f"  {relative_path}")
    
    # 정리
    shutil.rmtree(work_dir)
    print(f"\n정리: {work_dir} 디렉터리 삭제")

def advanced_pathlib():
    """pathlib 고급 활용"""
    
    # 프로젝트 구조 생성
    project_root = Path("korean_project")
    
    # 전형적인 파이썬 프로젝트 구조
    directories = [
        "src/korean_app",
        "tests/unit", 
        "tests/integration",
        "docs/api",
        "docs/tutorials",
        "data/raw",
        "data/processed",
        "config",
        "logs"
    ]
    
    for dir_path in directories:
        (project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    # 파일 생성
    files_to_create = {
        "README.md": "# 한국어 프로젝트\n\n파이썬으로 만든 한국어 처리 애플리케이션",
        "requirements.txt": "requests>=2.28.0\npandas>=1.5.0\nfastapi>=0.85.0",
        "src/korean_app/__init__.py": "# 한국어 앱 패키지",
        "src/korean_app/main.py": 'def main():\n    print("안녕하세요, 한국어 앱입니다!")',
        "config/settings.json": '{\n  "language": "ko",\n  "debug": true\n}',
        "data/raw/sample.txt": "안녕하세요\n한글 데이터 샘플입니다"
    }
    
    for file_path, content in files_to_create.items():
        full_path = project_root / file_path
        full_path.write_text(content, encoding="utf-8")
    
    print(f"프로젝트 구조 생성 완료: {project_root}")
    
    # 프로젝트 분석
    def analyze_project(root_path: Path):
        """프로젝트 구조 분석"""
        total_files = 0
        total_size = 0
        file_types = {}
        
        for file_path in root_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                file_size = file_path.stat().st_size
                total_size += file_size
                
                extension = file_path.suffix.lower() or "확장자없음"
                if extension not in file_types:
                    file_types[extension] = {"count": 0, "size": 0}
                
                file_types[extension]["count"] += 1
                file_types[extension]["size"] += file_size
        
        return {
            "총파일수": total_files,
            "총크기": total_size,
            "파일타입별": file_types
        }
    
    analysis = analyze_project(project_root)
    
    print(f"\n프로젝트 분석 결과:")
    print(f"총 파일 수: {analysis['총파일수']}")
    print(f"총 크기: {analysis['총크기']} bytes")
    print(f"파일 타입별 통계:")
    
    for ext, info in analysis["파일타입별"].items():
        print(f"  {ext}: {info['count']}개 파일, {info['size']} bytes")
    
    # 특정 파일 찾기
    print(f"\n파이썬 파일 찾기:")
    python_files = list(project_root.rglob("*.py"))
    for py_file in python_files:
        rel_path = py_file.relative_to(project_root)
        size = py_file.stat().st_size
        print(f"  {rel_path} ({size} bytes)")
    
    # 빈 디렉터리 찾기
    print(f"\n빈 디렉터리:")
    for dir_path in project_root.rglob("*"):
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            rel_path = dir_path.relative_to(project_root)
            print(f"  {rel_path}/")
    
    # 정리
    shutil.rmtree(project_root)
    print(f"\n정리: {project_root} 프로젝트 삭제")

# 실행
print("=== pathlib 기본 사용법 ===")
pathlib_basics()

print("\n=== pathlib 파일 작업 ===")
pathlib_file_operations()

print("\n=== pathlib 고급 활용 ===")
advanced_pathlib()
```

`pathlib_basics()`의 앞부분 출력은 실행하는 컴퓨터와 위치에 따라 다르게 나옵니다. `Path.cwd()`는 지금 작업 중인 폴더, `Path.home()`은 사용자의 홈 폴더니까요. 반면 `sample_path`에서 꺼낸 `name`(`chapter01.md`), `suffix`(`.md`), `stem`(`chapter01`), `parent`는 문자열을 쪼개는 일이라 어디서나 같습니다. `resolve()`는 상대 경로 앞에 현재 폴더를 붙여 절대 경로로 바꿔 주는데, 파일이 실제로 없어도 주소 계산은 해 줘요.

`pathlib_file_operations()`에서 기억할 것들입니다.

- `mkdir(parents=True, exist_ok=True)`: 중간 폴더가 없으면 함께 만들고, 이미 있어도 에러를 내지 않습니다. 이 두 옵션을 빼면 각각 `FileNotFoundError`, `FileExistsError`가 날 수 있어요.
- `write_text()`와 `read_text()`: `open`과 `with`를 한 줄로 줄인 지름길입니다. 짧은 파일을 통째로 쓰고 읽을 때 편해요.
- `glob("*.md")`는 그 폴더 바로 안에서만, `rglob("*.md")`는 하위 폴더까지 모두 뒤져 찾습니다. `*`는 "아무 글자나 몇 개든"이라는 뜻이에요.
- `stat().st_ctime`은 운영체제마다 뜻이 다릅니다. 윈도우에서는 파일을 만든 시각이지만, 맥과 리눅스에서는 파일 정보(권한 등)가 마지막으로 바뀐 시각이에요. 그래서 예제는 이 값을 "생성 시간"이 아니라 "상태 변경 시간"이라고 출력합니다.
- `shutil.rmtree()`는 폴더를 안의 내용까지 통째로 지웁니다. 휴지통을 거치지 않으니 경로를 잘못 주면 되돌릴 수 없어요. 예제처럼 방금 만든 연습용 폴더에만 쓰세요.

`advanced_pathlib()`은 이 도구들을 모아 실제 프로젝트 폴더 구조를 만들고, `rglob("*")`로 모든 파일을 돌며 확장자별 개수와 크기를 셉니다. `file_path.suffix`가 빈 문자열이면 `"확장자없음"`으로 묶은 것도 눈여겨보세요.

## 12.3 예외 처리 기초

### 기본 예외 처리

프로그램을 짜다 보면 빨간 에러 메시지를 수없이 만납니다. 파이썬에서는 실행 중에 일어난 이런 문제를 **예외(exception)** 라고 불러요. 예외가 나면 프로그램은 그 자리에서 멈춥니다. 사용자가 나이 칸에 "abc"를 입력했다고 프로그램 전체가 꺼지면 곤란하겠죠. `try` 문은 "일단 해 보고, 문제가 생기면 이렇게 대처하겠다"는 약속입니다.

```
try:
    실행할 코드
except 예외종류:
    그 예외가 났을 때 처리하는 코드
else:
    예외가 나지 않았을 때 실행할 코드
finally:
    예외가 났든 안 났든 항상 실행할 코드
```

`try` 안의 코드를 실행하다 문제가 생기면 그 즉시 남은 줄을 건너뛰고 맞는 `except`로 갑니다. 아무 문제 없이 끝나면 `except`는 모두 무시하고 `else`를 실행하죠. `finally`는 어느 쪽이든 마지막에 꼭 실행됩니다. 짧은 예로 확인해 봅시다.

```python
for text in ["5", "0", "abc"]:
    try:
        y = 10 / int(text)
    except ZeroDivisionError:      # 0으로 나눴을 때
        print("0으로 나눌 수 없습니다.")
    except ValueError:             # 숫자가 아닌 글자가 들어왔을 때
        print("숫자를 입력하세요.")
    else:                          # 예외가 없었을 때만
        print("결과:", y)
    finally:                       # 무슨 일이 있어도
        print("--- 끝 ---")
```

`"5"`는 `결과: 2.0`, `"0"`은 0으로 나눌 수 없다는 안내, `"abc"`는 숫자를 입력하라는 안내가 나오고, 세 번 모두 `--- 끝 ---`이 찍힙니다. 예외의 **종류**에 따라 다른 `except`가 골라졌다는 점이 핵심이에요.

`try`가 이렇게 편하다 보니 아무 데나 감싸고 싶어지는데, 마구잡이로 쓴 `try`는 큰 화를 부릅니다. 특히 `except:`처럼 종류를 적지 않으면 오타로 생긴 `NameError`까지 조용히 삼켜서, 버그가 있는데도 프로그램이 멀쩡한 척 돌아가요. 처리할 줄 아는 예외만 구체적으로 적고, 구체적인 예외를 먼저, 넓은 `Exception`을 나중에 두세요. 위에서부터 순서대로 맞춰 보다가 처음 맞는 하나만 실행하기 때문입니다. 그리고 `try`도 만능은 아닙니다. 괄호를 닫지 않은 것 같은 **문법 오류(SyntaxError)** 는 실행하기 전에 코드를 읽는 단계에서 걸리기 때문에, `try`로 감싸도 잡을 수 없어요.

> **Q. 에러의 종류는 누가 정하나요?**
> 기본 종류는 파이썬이 미리 정해 두었습니다. 그리고 이 예외들은 사실 모두 **클래스**이고, 족보처럼 상속 관계로 이어져 있어요. `ZeroDivisionError.__mro__`를 출력해 보면 `ZeroDivisionError → ArithmeticError → Exception → BaseException`으로 올라가는 계보가 나옵니다. 그래서 `except ArithmeticError:`라고 쓰면 그 자식인 `ZeroDivisionError`도 함께 잡히고, `except Exception:`은 거의 모든 예외를 잡죠. 클래스라는 건 우리가 새 종류를 직접 만들 수도 있다는 뜻입니다. 그건 12.4에서 해 봅니다.

```python
import traceback
from typing import Optional, List
import random

def basic_exception_handling():
    """기본 예외 처리 패턴"""
    
    print("1. 기본 try-except 구문:")
    
    # 숫자 입력받기 (시뮬레이션)
    user_inputs = ["25", "abc", "0", "-5", "100"]
    
    for user_input in user_inputs:
        try:
            age = int(user_input)
            print(f"[O] 입력값 '{user_input}' → 나이: {age}세")
            
            # 나이 유효성 검사
            if age < 0:
                raise ValueError("나이는 0보다 작을 수 없습니다")
            elif age > 150:
                raise ValueError("나이는 150을 초과할 수 없습니다")
            
            # 연령대 분류
            if age < 20:
                category = "청소년"
            elif age < 65:
                category = "성인"
            else:
                category = "노인"
            
            print(f"   연령대: {category}")
            
        except ValueError as e:
            print(f"[X] 입력값 '{user_input}' 오류: {e}")
        except Exception as e:
            print(f"[X] 예상치 못한 오류: {e}")

def multiple_exception_handling():
    """다중 예외 처리"""
    
    print("\n2. 다중 예외 처리:")
    
    # 다양한 오류 상황 시뮬레이션
    test_cases = [
        {"operation": "divide", "a": 10, "b": 2},
        {"operation": "divide", "a": 10, "b": 0},  # ZeroDivisionError
        {"operation": "access_list", "lst": [1, 2, 3], "index": 1},
        {"operation": "access_list", "lst": [1, 2, 3], "index": 5},  # IndexError
        {"operation": "access_dict", "d": {"name": "김철수"}, "key": "name"},
        {"operation": "access_dict", "d": {"name": "김철수"}, "key": "age"},  # KeyError
    ]
    
    for case in test_cases:
        try:
            if case["operation"] == "divide":
                result = case["a"] / case["b"]
                print(f"[O] {case['a']} ÷ {case['b']} = {result}")
            
            elif case["operation"] == "access_list":
                value = case["lst"][case["index"]]
                print(f"[O] 리스트[{case['index']}] = {value}")
            
            elif case["operation"] == "access_dict":
                value = case["d"][case["key"]]
                print(f"[O] 딕셔너리['{case['key']}'] = {value}")
                
        except ZeroDivisionError:
            print(f"[X] 0으로 나눌 수 없습니다: {case['a']} ÷ {case['b']}")
        
        except IndexError:
            print(f"[X] 리스트 인덱스 범위 초과: {case['lst']}[{case['index']}]")
        
        except KeyError as e:
            print(f"[X] 딕셔너리에 키가 없습니다: {e}")
        
        except Exception as e:
            print(f"[X] 예상치 못한 오류: {type(e).__name__}: {e}")

def try_except_else_finally():
    """try-except-else-finally 구문"""
    
    print("\n3. try-except-else-finally 구문:")
    
    def process_file(filename: str, create_if_missing: bool = False):
        """파일 처리 함수"""
        file_handle = None
        
        try:
            print(f"파일 열기 시도: {filename}")
            
            file_handle = open(filename, "r", encoding="utf-8")
            
            print(f"[O] 파일 열기 성공: {filename}")
            
        except FileNotFoundError:
            print(f"[X] 파일을 찾을 수 없습니다: {filename}")
            if create_if_missing:
                try:
                    file_handle = open(filename, "w", encoding="utf-8")
                    file_handle.write(f"# {filename}\n생성 시간: {datetime.now()}\n")
                    print(f"[O] 새 파일 생성: {filename}")
                except Exception as create_error:
                    print(f"[X] 파일 생성 실패: {create_error}")
        
        except PermissionError:
            print(f"[X] 파일 접근 권한이 없습니다: {filename}")
        
        except Exception as e:
            print(f"[X] 예상치 못한 오류: {e}")
        
        else:
            # 예외가 발생하지 않았을 때만 실행
            print("[O] 파일 처리가 정상적으로 완료되었습니다")
            
            if file_handle and not file_handle.closed:
                if 'r' in file_handle.mode:
                    content = file_handle.read()
                    print(f"파일 내용 (첫 50자): {content[:50]}...")
        
        finally:
            # 항상 실행되는 블록
            if file_handle and not file_handle.closed:
                file_handle.close()
                print(f"파일 핸들 정리 완료: {filename}")
            print("--- 파일 처리 종료 ---\n")
    
    # 테스트 케이스들
    from datetime import datetime
    
    # 존재하지 않는 파일 (생성하지 않음)
    process_file("nonexistent.txt", create_if_missing=False)
    
    # 존재하지 않는 파일 (생성함)
    process_file("created_file.txt", create_if_missing=True)
    
    # 생성된 파일 읽기
    process_file("created_file.txt", create_if_missing=False)
    
    # 정리
    import os
    if os.path.exists("created_file.txt"):
        os.remove("created_file.txt")

def exception_information():
    """예외 정보 상세 확인"""
    
    print("\n4. 예외 정보 상세 확인:")
    
    def problematic_function():
        """의도적으로 오류를 발생시키는 함수"""
        data = {"한글": "Korean", "영어": "English"}
        
        # 여러 단계의 함수 호출
        def level1():
            return level2()
        
        def level2():
            return level3()
        
        def level3():
            # 의도적 오류 발생
            return data["중국어"]  # KeyError 발생
        
        return level1()
    
    try:
        result = problematic_function()
        print(f"결과: {result}")
        
    except KeyError as e:
        print(f"[X] KeyError 발생: {e}")
        print(f"예외 타입: {type(e)}")
        print(f"예외 메시지: {str(e)}")
        
        # 상세한 트레이스백 정보
        print("\n상세 트레이스백:")
        traceback.print_exc()
        
        # 트레이스백을 문자열로 저장
        trace_str = traceback.format_exc()
        print(f"\n트레이스백 문자열 길이: {len(trace_str)} 문자")
        
        # 스택 정보 분석
        import sys
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        print(f"\n예외 분석:")
        print(f"예외 타입: {exc_type.__name__}")
        print(f"예외 값: {exc_value}")
        
        # 스택 프레임 정보
        frames = traceback.extract_tb(exc_traceback)
        print(f"스택 프레임 수: {len(frames)}")
        
        for i, frame in enumerate(frames):
            print(f"  프레임 {i+1}: {frame.filename}:{frame.lineno} in {frame.name}")
            print(f"    코드: {frame.line}")

# 실행
print("=== 예외 처리 기본 ===")
basic_exception_handling()
multiple_exception_handling()
try_except_else_finally()
exception_information()
```

1번 출력에서 `'-5'`를 보세요. `[O] 입력값 '-5' → 나이: -5세`가 먼저 찍히고 바로 다음 줄에 오류가 나옵니다. `int("-5")`는 문제없이 성공했으니 출력까지 갔고, 그다음 줄의 검사에서 우리가 직접 `raise ValueError(...)`로 예외를 **일으킨** 거예요. `raise`는 파이썬이 아니라 우리가 "이건 문제다"라고 판단할 때 쓰는 문장입니다. 그 뒤의 연령대 분류는 건너뛰고 곧장 `except ValueError`로 갔죠.

2번은 예외 종류마다 `except`를 따로 두었습니다. 0으로 나누기, 없는 인덱스, 없는 키가 각자 맞는 안내문으로 처리되고, `KeyError`의 `e`를 출력하면 없던 키 `'age'`가 나와요. 3번의 `finally`는 파일이 열렸든 못 열렸든 "--- 파일 처리 종료 ---"를 찍고, 열린 파일이 있으면 닫습니다. 정리 코드를 `finally`에 두면 빠뜨릴 일이 없어요.

4번은 에러 메시지, 즉 **트레이스백(traceback)** 을 읽는 법과 이어집니다. 트레이스백은 예외가 생긴 곳까지 함수가 어떤 순서로 불렸는지 보여 주는 기록이에요. `level1 → level2 → level3`처럼 위에서 아래로 호출 순서가 나오고, **맨 아래 줄**에 예외의 종류와 메시지(`KeyError: '중국어'`)가 있습니다. 에러를 만나면 맨 아래 줄부터 읽고, 바로 위에서 내가 쓴 파일의 줄 번호를 찾으세요. `traceback.print_exc()`는 이 기록을 출력하고, `format_exc()`는 문자열로 돌려줘서 로그 파일에 남길 때 씁니다.

> **허락보다 용서가 쉽다**
> 파이썬 커뮤니티에는 EAFP(Easier to Ask Forgiveness than Permission)라는 말이 있습니다. "허락을 구하는 것보다 용서를 구하는 게 쉽다", 즉 일단 해 보고(`try`) 안 되면 그때 처리하는(`except`) 방식이에요. 반대는 LBYL(Look Before You Leap), "누울 자리를 보고 다리를 뻗어라"입니다. 실행하기 전에 `if`로 조건을 미리 따져 보는 방식이죠. 예를 들어 딕셔너리에서 값을 꺼낼 때 `if key in d:`로 먼저 확인하면 LBYL, `try: d[key]` 후 `except KeyError:`로 처리하면 EAFP입니다. 파이썬 공식 용어집은 EAFP를 파이썬에서 흔한 스타일로 소개해요. 확인과 실행 사이에 상황이 바뀌는(그 사이에 다른 프로그램이 파일을 지우는 등) 문제를 피할 수 있기 때문입니다.

## 12.4 사용자 정의 예외와 고급 예외 처리

### 사용자 정의 예외 클래스

전화번호 형식이 틀렸을 때 `ValueError`를 내도 되긴 합니다. 그런데 `ValueError`는 `int("abc")`에서도, 수많은 다른 곳에서도 나는 아주 흔한 예외예요. 받는 쪽에서 "이게 전화번호 문제인지 다른 문제인지" 구별하려면 메시지 문자열을 뒤져야 하죠. 예외 종류의 **이름** 자체가 무슨 문제인지 말해 주면 훨씬 낫습니다.

앞에서 예외는 모두 클래스라고 했죠. 그러니 새 예외는 `Exception`을 상속한 클래스를 만들면 끝입니다. 내용이 없어도 돼요. `class KoreanError(Exception): pass` 한 줄이면 `raise KoreanError("메시지")`로 쓸 수 있습니다. 아래 예제는 여기서 한 걸음 더 나가 오류 코드, 발생 시각, 상황 정보까지 담고, 예외들 사이에 족보를 만들었어요.

```
Exception
└── KoreanError                 모든 한국 데이터 오류의 조상
    └── KoreanValidationError   검증 실패
        ├── KoreanPhoneNumberError
        ├── KoreanBusinessNumberError
        └── KoreanNameError
```

이렇게 족보를 만들어 두면 받는 쪽이 원하는 만큼 넓게 또는 좁게 잡을 수 있습니다. 전화번호 오류만 따로 처리하고 싶으면 `except KoreanPhoneNumberError:`, 검증 오류 전부라면 `except KoreanValidationError:`, 이 프로그램이 낸 오류 전부라면 `except KoreanError:`로요. 부모로 잡으면 자식도 함께 잡히는 건 13장에서 배울 상속 덕분입니다.

```python
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# 한국어 예외 클래스 정의
class KoreanError(Exception):
    """한국어 관련 기본 예외 클래스"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self):
        return f"[{self.error_code}] {self.message}"
    
    def to_dict(self):
        """예외 정보를 딕셔너리로 반환"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }

class KoreanValidationError(KoreanError):
    """한국어 데이터 검증 오류"""
    
    def __init__(self, field_name: str, value: Any, message: str):
        context = {"field": field_name, "value": str(value)}
        super().__init__(message, "VALIDATION_ERROR", context)
        self.field_name = field_name
        self.value = value

class KoreanPhoneNumberError(KoreanValidationError):
    """한국 전화번호 형식 오류"""
    
    def __init__(self, phone_number: str):
        message = f"올바르지 않은 한국 전화번호 형식: {phone_number} (예: 010-1234-5678)"
        super().__init__("phone_number", phone_number, message)

class KoreanBusinessNumberError(KoreanValidationError):
    """한국 사업자등록번호 형식 오류"""
    
    def __init__(self, business_number: str):
        message = f"올바르지 않은 사업자등록번호 형식: {business_number} (예: 123-45-67891)"
        super().__init__("business_number", business_number, message)

class KoreanNameError(KoreanValidationError):
    """한국 이름 형식 오류"""
    
    def __init__(self, name: str, reason: str = "한글 2-5글자여야 합니다"):
        message = f"올바르지 않은 한국 이름: {name} ({reason})"
        super().__init__("korean_name", name, message)

# 한국 데이터 검증 클래스
class KoreanDataValidator:
    """한국 데이터 검증기"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """한국 전화번호 검증"""
        import re
        
        # 하이픈 제거 후 검증
        cleaned_phone = re.sub(r'[-\s]', '', phone)
        
        # 010으로 시작하는 11자리 숫자
        if not re.match(r'^010\d{8}$', cleaned_phone):
            raise KoreanPhoneNumberError(phone)
        
        # 표준 형식으로 반환
        return f"{cleaned_phone[:3]}-{cleaned_phone[3:7]}-{cleaned_phone[7:]}"
    
    @staticmethod  
    def validate_business_number(business_num: str) -> str:
        """사업자등록번호 검증"""
        import re
        
        # 하이픈 제거
        cleaned_num = re.sub(r'[-\s]', '', business_num)
        
        # 10자리 숫자 검증
        if not re.match(r'^\d{10}$', cleaned_num):
            raise KoreanBusinessNumberError(business_num)
        
        # 체크섬 검증 (사업자등록번호 검증 규칙)
        check_digits = [1, 3, 7, 1, 3, 7, 1, 3, 5]
        total = sum(int(cleaned_num[i]) * check_digits[i] for i in range(9))
        total += int(cleaned_num[8]) * 5 // 10  # 9번째 자리 × 5의 십의 자리를 한 번 더 더함
        check_digit = (10 - (total % 10)) % 10
        
        if int(cleaned_num[9]) != check_digit:
            raise KoreanBusinessNumberError(business_num)
        
        # 표준 형식으로 반환
        return f"{cleaned_num[:3]}-{cleaned_num[3:5]}-{cleaned_num[5:]}"
    
    @staticmethod
    def validate_korean_name(name: str) -> str:
        """한국 이름 검증"""
        import re
        
        # 한글만 허용, 2-5글자
        if not re.match(r'^[가-힣]{2,5}$', name):
            if not re.match(r'^[가-힣]+$', name):
                reason = "한글만 입력 가능합니다"
            elif len(name) < 2:
                reason = "최소 2글자 이상이어야 합니다" 
            elif len(name) > 5:
                reason = "최대 5글자까지 가능합니다"
            else:
                reason = "올바르지 않은 형식입니다"
            
            raise KoreanNameError(name, reason)
        
        return name

def demonstrate_custom_exceptions():
    """사용자 정의 예외 시연"""
    
    print("=== 사용자 정의 예외 시연 ===")
    
    # 테스트 데이터
    test_data = [
        {"type": "phone", "value": "010-1234-5678", "valid": True},
        {"type": "phone", "value": "010-1234-567", "valid": False},   # 숫자가 10자리
        {"type": "phone", "value": "011-1234-5678", "valid": False},
        {"type": "business", "value": "123-45-67890", "valid": False},  # 체크섬 오류
        {"type": "business", "value": "123-45-67891", "valid": True},   # 체크섬이 맞는 번호
        {"type": "name", "value": "김철수", "valid": True},
        {"type": "name", "value": "김", "valid": False},
        {"type": "name", "value": "Kim철수", "valid": False},
    ]
    
    validator = KoreanDataValidator()
    
    for data in test_data:
        try:
            if data["type"] == "phone":
                result = validator.validate_phone_number(data["value"])
                print(f"[O] 전화번호 검증 성공: {data['value']} → {result}")
            
            elif data["type"] == "business":
                result = validator.validate_business_number(data["value"])
                print(f"[O] 사업자번호 검증 성공: {data['value']} → {result}")
            
            elif data["type"] == "name":
                result = validator.validate_korean_name(data["value"])
                print(f"[O] 이름 검증 성공: {data['value']}")
                
        except KoreanError as e:
            expected = "[X]" if not data["valid"] else "[!]"
            print(f"{expected} {e}")
            
            # 예외 상세 정보
            if not data["valid"]:  # 예상된 오류인 경우 상세 정보 표시
                error_dict = e.to_dict()
                print(f"   오류 정보: {error_dict}")

# 예외 체이닝과 재발생
def exception_chaining_demo():
    """예외 체이닝 시연"""
    
    print("\n=== 예외 체이닝 시연 ===")
    
    def process_korean_user_data(user_data: dict):
        """한국 사용자 데이터 처리"""
        try:
            # 이름 검증
            name = KoreanDataValidator.validate_korean_name(user_data.get("name", ""))
            
            # 전화번호 검증
            phone = KoreanDataValidator.validate_phone_number(user_data.get("phone", ""))
            
            # 사업자번호 검증 (있는 경우)
            business_num = user_data.get("business_number")
            if business_num:
                business_num = KoreanDataValidator.validate_business_number(business_num)
            
            return {
                "name": name,
                "phone": phone,
                "business_number": business_num,
                "status": "validated"
            }
            
        except KoreanValidationError as validation_error:
            # 원본 예외를 체인으로 연결하여 새 예외 발생
            raise KoreanError(
                f"사용자 데이터 검증 실패: {user_data.get('name', 'Unknown')}",
                "USER_DATA_VALIDATION_FAILED",
                {"user_data": user_data}
            ) from validation_error
    
    # 테스트 데이터
    test_users = [
        {"name": "김철수", "phone": "010-1234-5678"},  # 정상
        {"name": "이", "phone": "010-1234-5678"},      # 이름 오류
        {"name": "박민수", "phone": "010-1234-567"},    # 전화번호 오류
    ]
    
    for user in test_users:
        try:
            result = process_korean_user_data(user)
            print(f"[O] 사용자 데이터 처리 성공: {result['name']}")
        
        except KoreanError as e:
            print(f"[X] 사용자 데이터 처리 실패: {e}")
            
            # 원본 예외 확인 (__cause__ 속성)
            if e.__cause__:
                print(f"   원인: {e.__cause__}")
                print(f"   원인 타입: {type(e.__cause__).__name__}")

# 로깅과 함께하는 예외 처리
def logging_with_exceptions():
    """로깅과 함께하는 예외 처리"""
    
    print("\n=== 로깅과 예외 처리 ===")
    
    # 로거 설정
    logger = logging.getLogger("korean_app")
    logger.setLevel(logging.DEBUG)
    
    # 콘솔 핸들러
    if not logger.handlers:  # 중복 핸들러 방지
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    def secure_korean_data_processor(data: dict):
        """보안이 중요한 한국 데이터 처리기"""
        
        logger.info(f"데이터 처리 시작: {data.get('name', 'Unknown')}")
        
        try:
            # 민감한 개인정보 처리 시뮬레이션
            if "ssn" in data:  # 주민등록번호
                logger.warning("주민등록번호 처리 - 보안 검사 필요")
                # 실제로는 암호화 등의 보안 처리
            
            # 데이터 검증
            validated_data = {}
            validated_data["name"] = KoreanDataValidator.validate_korean_name(data["name"])
            validated_data["phone"] = KoreanDataValidator.validate_phone_number(data["phone"])
            
            logger.info(f"데이터 검증 완료: {validated_data['name']}")
            return validated_data
            
        except KoreanValidationError as e:
            # 검증 오류는 WARNING 레벨
            logger.warning(f"데이터 검증 실패: {e}", exc_info=True)
            raise
            
        except Exception as e:
            # 예상치 못한 오류는 ERROR 레벨
            logger.error(f"예상치 못한 오류 발생", exc_info=True)
            
            # 민감한 정보가 포함된 데이터는 로그에서 제외
            safe_data = {k: v for k, v in data.items() if k not in ["ssn", "password"]}
            logger.error(f"처리 중이던 안전한 데이터: {safe_data}")
            
            raise KoreanError(
                "시스템 오류가 발생했습니다. 관리자에게 문의하세요.",
                "SYSTEM_ERROR",
                {"timestamp": datetime.now().isoformat()}
            ) from e
    
    # 테스트
    test_cases = [
        {"name": "김철수", "phone": "010-1234-5678"},
        {"name": "이영희", "phone": "010-1234-5678", "ssn": "123456-1234567"},
        {"name": "박", "phone": "010-1234-5678"},  # 이름 오류
    ]
    
    for case in test_cases:
        try:
            result = secure_korean_data_processor(case)
            print(f"[O] 처리 완료: {result}")
        except KoreanError as e:
            print(f"[X] 처리 실패: {e}")

# 실행
demonstrate_custom_exceptions()
exception_chaining_demo()
logging_with_exceptions()
```

`demonstrate_custom_exceptions()`는 전화번호, 사업자번호, 이름을 모두 `except KoreanError` **하나**로 받았습니다. 세 예외가 모두 `KoreanError`의 자손이기 때문이에요. 그런데도 출력에는 `KoreanPhoneNumberError`, `KoreanNameError`처럼 실제 종류가 정확히 남습니다. `to_dict()`가 `self.__class__.__name__`으로 자기 클래스 이름을 꺼내 기록하거든요. `__str__`을 다시 정의해 두었기 때문에 `print(e)`가 `[VALIDATION_ERROR] 메시지` 모양으로 찍히는 것도 11장의 매직 메서드 그대로입니다.

`exception_chaining_demo()`의 `raise KoreanError(...) from validation_error`는 **예외 연결**입니다. 낮은 단계의 오류(이름이 한 글자)를 높은 단계의 오류(사용자 데이터 처리 실패)로 바꿔 올리면서, 원래 원인을 `__cause__`에 붙여 두는 거예요. 출력의 "원인: ... (최소 2글자 이상이어야 합니다)"가 거기서 나왔습니다. 이 예외를 아무도 잡지 않아 트레이스백이 찍힌다면, 원래 예외와 새 예외 사이에 `The above exception was the direct cause of the following exception:`이라는 줄이 들어가 두 예외가 함께 보여요. 원인을 잃어버리지 않고 포장만 바꾸는 방법입니다.

`logging_with_exceptions()`는 화면에 `print`하는 대신 **로그**를 남깁니다. 로그에는 시각과 심각도(INFO, WARNING, ERROR)가 함께 찍히고, `exc_info=True`를 주면 트레이스백까지 기록돼요. 실행해 보면 로그는 표준 에러로 나가기 때문에 일반 출력과 섞여 보일 수 있습니다. 그리고 `except` 블록 끝의 맨 `raise`는 방금 잡은 예외를 기록만 하고 **그대로 다시 던지는** 문장이에요. 여기서 처리할 수 없는 문제라면 이렇게 위로 넘겨야지 삼켜 버리면 안 됩니다. 주민등록번호나 비밀번호 같은 개인정보를 로그에서 빼는(`safe_data`) 부분도 실무에서 꼭 지켜야 하는 습관입니다.

예외를 일으키는 방법이 하나 더 있습니다. `assert 조건, "메시지"`는 조건이 거짓이면 `AssertionError`를 냅니다. "여기서는 절대 이럴 리 없다"는 개발자의 가정을 확인할 때 쓰는데, 파이썬을 `-O` 옵션으로 최적화해 실행하면 `assert` 문이 통째로 빠져 버립니다. 그래서 사용자 입력 검증처럼 꼭 실행돼야 하는 검사는 `assert`가 아니라 `if`와 `raise`로 써야 해요.

## 12.5 CSV와 JSON 파일 처리

### CSV 파일 처리

파일에 아무렇게나 적어 두면 나중에 읽을 때 어디까지가 이름이고 어디부터가 나이인지 알 수 없습니다. 그래서 사람들이 약속한 저장 형식을 씁니다. 그중 가장 많이 쓰는 두 가지가 CSV와 JSON이에요.

**CSV(Comma-Separated Values)** 는 표를 글자로 적는 방법입니다. 한 줄이 표의 한 행이고, 칸은 쉼표로 나눠요. 첫 줄에는 보통 열 이름을 적습니다.

```
이름,나이,전공,평점,입학년도
김철수,20,컴퓨터과학과,3.8,2022
```

메모장으로도 열리고 엑셀로도 열리니 사람과 프로그램이 함께 보기 좋죠. 그런데 값 안에 쉼표가 들어 있으면 어떻게 할까요? `"글로벌, 반도체 1위"`처럼 큰따옴표로 감싸는 규칙이 있는데, 이런 규칙을 직접 처리하기는 번거로우니 표준 라이브러리의 `csv` 모듈에 맡깁니다. `DictWriter`와 `DictReader`를 쓰면 행을 딕셔너리로 주고받을 수 있어요.

CSV 파일을 열 때는 `newline=""`을 꼭 붙이세요. `csv` 모듈이 줄바꿈을 직접 관리하기 때문에, 이걸 빼면 따옴표 안의 줄바꿈이 제대로 읽히지 않거나 윈도우에서 행 사이에 빈 줄이 끼어들 수 있습니다. 파이썬 공식 문서가 권하는 방법이에요.

```python
import csv
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime, date
from decimal import Decimal

def korean_csv_processing():
    """한국어 CSV 파일 처리"""
    
    print("=== 한국어 CSV 파일 처리 ===")
    
    # 한국 학생 데이터 생성
    korean_students = [
        {"이름": "김철수", "나이": 20, "전공": "컴퓨터과학과", "평점": 3.8, "입학년도": 2022},
        {"이름": "이영희", "나이": 21, "전공": "경영학과", "평점": 3.9, "입학년도": 2021},
        {"이름": "박민수", "나이": 19, "전공": "기계공학과", "평점": 3.6, "입학년도": 2023},
        {"이름": "최지영", "나이": 22, "전공": "화학과", "평점": 4.0, "입학년도": 2020},
        {"이름": "정수진", "나이": 20, "전공": "수학과", "평점": 3.7, "입학년도": 2022}
    ]
    
    csv_file = Path("korean_students.csv")
    
    # CSV 파일 쓰기
    try:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            if korean_students:
                fieldnames = korean_students[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # 헤더 쓰기
                writer.writeheader()
                
                # 데이터 쓰기
                writer.writerows(korean_students)
        
        print(f"[O] CSV 파일 생성 완료: {csv_file}")
        
    except Exception as e:
        print(f"[X] CSV 파일 생성 실패: {e}")
        return
    
    # CSV 파일 읽기
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            print(f"\nCSV 파일 내용:")
            print(f"컬럼: {reader.fieldnames}")
            
            loaded_students = []
            for row_num, row in enumerate(reader, 1):
                print(f"  {row_num}: {dict(row)}")
                loaded_students.append(row)
        
        print(f"총 {len(loaded_students)}명의 학생 데이터 로드")
        
    except Exception as e:
        print(f"[X] CSV 파일 읽기 실패: {e}")
    
    # 데이터 분석
    try:
        # 전공별 통계
        major_stats = {}
        for student in loaded_students:
            major = student["전공"]
            if major not in major_stats:
                major_stats[major] = {"count": 0, "total_gpa": 0}
            
            major_stats[major]["count"] += 1
            major_stats[major]["total_gpa"] += float(student["평점"])
        
        print(f"\n전공별 통계:")
        for major, stats in major_stats.items():
            avg_gpa = stats["total_gpa"] / stats["count"]
            print(f"  {major}: {stats['count']}명, 평균 평점: {avg_gpa:.2f}")
        
    except Exception as e:
        print(f"[X] 데이터 분석 실패: {e}")
    
    # 정리
    if csv_file.exists():
        csv_file.unlink()

def advanced_csv_processing():
    """고급 CSV 처리 기법"""
    
    print("\n=== 고급 CSV 처리 ===")
    
    # 복잡한 한국 회사 데이터
    company_data = [
        {
            "회사명": "삼성전자",
            "업종": "전자제품",
            "설립일": "1969-01-13",
            "직원수": 267800,
            "매출액": 2796890,  # 억원
            "주소": "경기도 수원시 영통구 삼성로 129",
            "상장여부": True,
            "특이사항": "글로벌, 반도체 1위"
        },
        {
            "회사명": "LG전자", 
            "업종": "전자제품",
            "설립일": "1958-02-01",
            "직원수": 75000,
            "매출액": 748632,
            "주소": "서울특별시 영등포구 여의대로 128",
            "상장여부": True,
            "특이사항": "가전제품, 인공지능"
        }
    ]
    
    # 복잡한 데이터를 CSV로 저장
    complex_csv = Path("korean_companies.csv")
    
    try:
        with open(complex_csv, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["회사명", "업종", "설립일", "직원수", "매출액", "주소", "상장여부", "특이사항"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
            
            writer.writeheader()
            writer.writerows(company_data)
        
        print(f"[O] 복잡한 CSV 파일 생성: {complex_csv}")
        
    except Exception as e:
        print(f"[X] CSV 생성 실패: {e}")
        return
    
    # CSV 파일을 다양한 방식으로 읽기
    try:
        print(f"\n다양한 CSV 읽기 방식:")
        
        # 1. DictReader 사용
        with open(complex_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            print("1. DictReader로 읽기:")
            for row in reader:
                # 데이터 타입 변환
                company_info = {
                    "회사명": row["회사명"],
                    "업종": row["업종"],
                    "설립일": datetime.strptime(row["설립일"], "%Y-%m-%d").date(),
                    "직원수": int(row["직원수"]),
                    "매출액": int(row["매출액"]),
                    "상장여부": row["상장여부"].lower() == "true"
                }
                print(f"  {company_info}")
        
        # 2. 일반 reader 사용
        with open(complex_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)  # 첫 번째 행은 헤더
            
            print(f"\n2. 일반 reader로 읽기:")
            print(f"헤더: {headers}")
            
            for row_num, row in enumerate(reader, 1):
                print(f"  행 {row_num}: {row}")
        
    except Exception as e:
        print(f"[X] CSV 읽기 실패: {e}")
    
    # 정리
    if complex_csv.exists():
        complex_csv.unlink()

def json_file_processing():
    """JSON 파일 처리"""
    
    print("\n=== JSON 파일 처리 ===")
    
    # 복잡한 한국 도시 데이터
    korean_cities_data = {
        "metadata": {
            "title": "한국 주요 도시 정보",
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "source": "통계청"
        },
        "cities": [
            {
                "name": "서울특별시",
                "english_name": "Seoul",
                "population": 9720846,
                "area_km2": 605.21,
                "districts": ["강남구", "강동구", "강북구", "강서구", "관악구"],
                "coordinates": {"latitude": 37.5665, "longitude": 126.9780},
                "established": "1394-07-01",
                "is_capital": True,
                "famous_for": ["한강", "경복궁", "남산타워", "홍대", "강남"]
            },
            {
                "name": "부산광역시",
                "english_name": "Busan", 
                "population": 3448737,
                "area_km2": 770.06,
                "districts": ["해운대구", "부산진구", "동래구", "남구", "중구"],
                "coordinates": {"latitude": 35.1796, "longitude": 129.0756},
                "established": "1963-01-01",
                "is_capital": False,
                "famous_for": ["해운대해수욕장", "자갈치시장", "태종대", "광안대교"]
            }
        ],
        "statistics": {
            "total_cities": 2,
            "total_population": 13169583,
            "average_area": 687.635
        }
    }
    
    json_file = Path("korean_cities.json")
    
    # JSON 파일 쓰기
    try:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(korean_cities_data, f, 
                     ensure_ascii=False,  # 한글 그대로 저장
                     indent=2,           # 예쁘게 포맷팅
                     separators=(',', ': '))  # 구분자 설정
        
        print(f"[O] JSON 파일 생성 완료: {json_file}")
        
    except Exception as e:
        print(f"[X] JSON 파일 생성 실패: {e}")
        return
    
    # JSON 파일 읽기
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        
        print(f"\nJSON 파일 내용:")
        print(f"제목: {loaded_data['metadata']['title']}")
        print(f"버전: {loaded_data['metadata']['version']}")
        print(f"도시 수: {loaded_data['statistics']['total_cities']}")
        
        # 도시별 정보 출력
        for city in loaded_data["cities"]:
            print(f"\n{city['name']} ({city['english_name']})")
            print(f"  인구: {city['population']:,}명")
            print(f"  면적: {city['area_km2']} km²")
            print(f"  인구밀도: {city['population']/city['area_km2']:,.1f}명/km²")
            print(f"  주요 관광지: {', '.join(city['famous_for'])}")
            print(f"  좌표: ({city['coordinates']['latitude']}, {city['coordinates']['longitude']})")
        
    except Exception as e:
        print(f"[X] JSON 파일 읽기 실패: {e}")
    
    # JSON 데이터 조작 및 저장
    try:
        # 새로운 도시 추가
        new_city = {
            "name": "대구광역시",
            "english_name": "Daegu",
            "population": 2438031,
            "area_km2": 883.56,
            "districts": ["중구", "동구", "서구", "남구", "북구"],
            "coordinates": {"latitude": 35.8714, "longitude": 128.6014},
            "established": "1949-08-15",
            "is_capital": False,
            "famous_for": ["83타워", "서문시장", "동화사", "수성못"]
        }
        
        loaded_data["cities"].append(new_city)
        loaded_data["statistics"]["total_cities"] = len(loaded_data["cities"])
        loaded_data["statistics"]["total_population"] += new_city["population"]
        
        # 수정된 데이터 저장
        updated_file = Path("korean_cities_updated.json")
        with open(updated_file, "w", encoding="utf-8") as f:
            json.dump(loaded_data, f, ensure_ascii=False, indent=2)
        
        print(f"[O] 업데이트된 JSON 파일 저장: {updated_file}")
        
        # JSON Lines 형식으로도 저장 (스트리밍에 유용)
        jsonl_file = Path("korean_cities.jsonl")
        with open(jsonl_file, "w", encoding="utf-8") as f:
            for city in loaded_data["cities"]:
                json.dump(city, f, ensure_ascii=False)
                f.write('\n')
        
        print(f"[O] JSON Lines 파일 저장: {jsonl_file}")
        
    except Exception as e:
        print(f"[X] JSON 데이터 조작 실패: {e}")
    
    # 정리
    for file in [json_file, Path("korean_cities_updated.json"), Path("korean_cities.jsonl")]:
        if file.exists():
            file.unlink()

# 실행
korean_csv_processing()
advanced_csv_processing()
json_file_processing()
```

CSV를 다시 읽어 온 출력을 보면 `'나이': '20'`, `'평점': '3.8'`처럼 숫자에도 따옴표가 붙어 있습니다. CSV는 글자만 적는 형식이라 읽어 오면 **모든 값이 문자열**이에요. 그래서 평균을 낼 때 `float(student["평점"])`으로 바꿨고, `advanced_csv_processing()`에서도 `int()`, `datetime.strptime()`, `.lower() == "true"` 비교로 하나하나 원래 타입으로 되돌렸습니다. `quoting=csv.QUOTE_NONNUMERIC`은 쓸 때 숫자가 아닌 값을 모두 큰따옴표로 감싸라는 옵션이라, 저장된 파일에서 문자열과 숫자를 눈으로 구별할 수 있어요. "일반 reader로 읽기" 출력에서 `"글로벌, 반도체 1위"`가 쉼표에서 쪼개지지 않고 한 칸으로 읽힌 것도 확인해 보세요.

**JSON(JavaScript Object Notation)** 은 표보다 복잡한 구조, 즉 딕셔너리 안의 리스트 안의 딕셔너리 같은 데이터를 담는 형식입니다. 웹에서 데이터를 주고받을 때 거의 표준처럼 쓰이고, 생김새도 파이썬의 딕셔너리·리스트와 비슷해요. 파이썬 값은 이렇게 바뀝니다.

| 파이썬 | JSON | 다시 읽으면 |
|---|---|---|
| `dict` | 객체 `{}` | `dict` |
| `list`, `tuple` | 배열 `[]` | `list` (튜플도 리스트로 돌아옴) |
| `str` | 문자열 | `str` |
| `int`, `float` | 숫자 | `int`, `float` |
| `True`, `False`, `None` | `true`, `false`, `null` | `True`, `False`, `None` |

이 표에 없는 타입은 저장할 수 없습니다. `datetime` 객체를 그대로 `json.dump()`에 넣으면 `Object of type datetime is not JSON serializable` 에러가 나요. 예제가 `datetime.now().isoformat()`으로 문자열을 만들어 넣은 이유입니다.

`ensure_ascii=False`도 중요합니다. 기본값(`True`)으로 두면 `json.dumps({"도시": "서울"})`이 `{"도시": "서울"}`처럼 한글을 유니코드 번호로 바꿔 적어요. 프로그램은 똑같이 읽지만 사람이 파일을 열면 알아볼 수가 없죠. `indent=2`는 들여쓰기로 보기 좋게 정리해 줍니다. 마지막의 **JSON Lines**(`.jsonl`)는 JSON 객체 하나를 한 줄에 하나씩 적는 방식이라, 파일 전체를 한 번에 읽지 않고 한 줄씩 처리하거나 끝에 계속 덧붙이기 좋습니다.

### 작업 중인 변수 통째로 저장하기: pickle

CSV와 JSON은 다른 프로그램과 데이터를 주고받기 좋은 대신, 담을 수 있는 타입이 정해져 있습니다. 그냥 **지금 작업하던 파이썬 변수들을 그대로 저장했다가 나중에 다시 꺼내고** 싶을 때는 표준 라이브러리의 `pickle`을 씁니다. 오이를 소금물에 절여 두었다가 나중에 꺼내 먹는 피클처럼, 파이썬 객체를 바이트로 절여 파일에 보관하는 거예요. 변수 여러 개를 저장할 때는 딕셔너리 하나로 묶어서 한 번에 넣으면 꺼낼 때도 이름으로 찾기 쉽습니다.

```python
import pickle
from pathlib import Path

scores = {"김철수": 85, "이영희": 92}
names = ["김철수", "이영희"]
round_no = 3

# 여러 변수를 딕셔너리 하나로 묶어서 한 번에 저장
with open("work.pkl", "wb") as f:
    pickle.dump({"scores": scores, "names": names, "round_no": round_no}, f)

with open("work.pkl", "rb") as f:
    saved = pickle.load(f)

print(saved["scores"], saved["names"], saved["round_no"])
# {'김철수': 85, '이영희': 92} ['김철수', '이영희'] 3
Path("work.pkl").unlink()
```

바이트로 저장하니 `"wb"`, `"rb"` 모드를 썼고, 꺼낸 리스트는 JSON과 달리 리스트 그대로, 딕셔너리는 딕셔너리 그대로 돌아옵니다. 다만 두 가지는 꼭 기억하세요. 첫째, **믿을 수 없는 곳에서 받은 pickle 파일은 절대 열지 마세요.** 파이썬 공식 문서도 경고하듯, 악의적으로 만든 pickle 파일은 여는 순간(`pickle.load`) 임의의 코드를 실행할 수 있습니다. 둘째, pickle은 파이썬 전용 형식이라 다른 언어와 데이터를 주고받을 때는 JSON이 맞습니다. 나 혼자 쓰는 중간 결과 보관용이라고 생각하면 됩니다.

## 12.6 실습 문제

### 기본 문제 (1-5번)

각 문제는 빈 함수와 `# 문제:` 설명이 먼저 나오고, `# 답:` 아래에 풀이가 이어집니다. 풀이 함수들은 실행이 끝나면 만든 파일과 폴더를 스스로 지우도록 되어 있으니, 결과 파일을 직접 열어 보고 싶다면 정리하는 줄을 잠시 지우고 실행해 보세요. 3번에서는 어떤 입력이 어떤 `except`로 가는지 먼저 예상해 보고 출력과 맞춰 보는 것도 좋은 연습입니다.

```python
# 1번: 파일 읽기/쓰기 기본
def create_korean_diary():
    """한국어 일기 파일 생성"""
    pass

# 문제: 한국어 일기를 파일로 저장하고 읽어오는 함수를 만드세요
# 답:
def create_korean_diary():
    diary_content = """2024년 3월 15일 일기

오늘은 파이썬 파일 처리를 공부했다.
한글 인코딩도 배웠고, pathlib도 사용해봤다.
내일은 예외 처리를 더 자세히 공부해야겠다.

기분: 좋음
날씨: 맑음"""
    
    with open("my_diary.txt", "w", encoding="utf-8") as f:
        f.write(diary_content)
    
    with open("my_diary.txt", "r", encoding="utf-8") as f:
        content = f.read()
        print(content)
    
    import os
    os.remove("my_diary.txt")

create_korean_diary()

# 2번: pathlib 활용
from pathlib import Path

# 문제: 한국어 프로젝트 구조를 pathlib로 만드세요
# 답:
def create_project_structure():
    project = Path("한국어_프로젝트")
    
    # 디렉터리 구조 생성
    dirs = ["소스코드", "데이터", "문서", "테스트"]
    for dir_name in dirs:
        (project / dir_name).mkdir(parents=True, exist_ok=True)
    
    # 파일 생성
    (project / "README.md").write_text("# 한국어 프로젝트", encoding="utf-8")
    (project / "소스코드" / "main.py").write_text('print("안녕하세요!")', encoding="utf-8")
    
    print(f"프로젝트 구조 생성: {project}")
    
    # 정리
    import shutil
    shutil.rmtree(project)

create_project_structure()

# 3번: 예외 처리 기본
def safe_division(a, b):
    # 문제: 안전한 나눗셈 함수를 만드세요
    pass

# 답:
def safe_division(a, b):
    try:
        result = a / b
        return {"success": True, "result": result}
    except ZeroDivisionError:
        return {"success": False, "error": "0으로 나눌 수 없습니다"}
    except TypeError:
        return {"success": False, "error": "숫자만 입력 가능합니다"}

print(safe_division(10, 2))
print(safe_division(10, 0))
print(safe_division("10", 2))

# 4번: CSV 처리
import csv

# 문제: 한국 학생 성적을 CSV로 관리하는 함수를 만드세요
# 답:
def manage_student_grades():
    students = [
        {"이름": "김철수", "국어": 85, "영어": 90, "수학": 88},
        {"이름": "이영희", "국어": 92, "영어": 87, "수학": 95},
        {"이름": "박민수", "국어": 78, "영어": 82, "수학": 90}
    ]
    
    # CSV 저장
    with open("성적.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["이름", "국어", "영어", "수학"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(students)
    
    # CSV 읽기 및 평균 계산
    with open("성적.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scores = [int(row["국어"]), int(row["영어"]), int(row["수학"])]
            avg = sum(scores) / len(scores)
            print(f"{row['이름']}: 평균 {avg:.1f}점")
    
    import os
    os.remove("성적.csv")

manage_student_grades()

# 5번: JSON 처리
import json

# 문제: 한국 음식 정보를 JSON으로 저장하고 검색하는 함수를 만드세요
# 답:
def korean_food_database():
    foods = {
        "한식": [
            {"이름": "김치찌개", "재료": ["김치", "돼지고기", "두부"], "매운맛": 3},
            {"이름": "비빔밥", "재료": ["밥", "나물", "고추장"], "매운맛": 2},
            {"이름": "불고기", "재료": ["소고기", "양파", "배"], "매운맛": 1}
        ]
    }
    
    # JSON 저장
    with open("음식.json", "w", encoding="utf-8") as f:
        json.dump(foods, f, ensure_ascii=False, indent=2)
    
    # JSON 읽기 및 검색
    with open("음식.json", "r", encoding="utf-8") as f:
        loaded_foods = json.load(f)
    
    # 매운맛 2 이상인 음식 찾기
    spicy_foods = [food for food in loaded_foods["한식"] if food["매운맛"] >= 2]
    print("매운 음식:")
    for food in spicy_foods:
        print(f"- {food['이름']} (매운맛: {food['매운맛']})")
    
    import os
    os.remove("음식.json")

korean_food_database()
```

## 12.7 다음 장 미리보기

다음 Chapter 13에서는 **상속과 다형성**을 학습합니다:

### 주요 내용 미리보기
- **상속 기초**: 부모 클래스 확장과 `super()` 활용
- **다중 상속과 MRO**: 메서드 탐색 순서 이해
- **추상 클래스와 인터페이스**: `abc` 모듈과 Protocol
- **다형성과 덕 타이핑**: 같은 인터페이스, 다른 동작
- **실전 프로젝트**: 한국 기업 HR 관리 시스템

### 연결 포인트
- 객체 지향 기초 → 클래스 계층 설계
- 사용자 정의 예외 → 예외 클래스 상속 구조
- 컨텍스트 매니저 → 프로토콜 기반 다형성

파일 처리와 예외 처리를 완전히 마스터했다면, 이제 클래스를 계층적으로 설계하고 확장하는 객체 지향의 핵심 기법을 배울 준비가 되었습니다!

---

> **학습 팁**: 파일 처리 시에는 항상 `with` 문을 사용하고, 예외 처리는 구체적인 예외부터 일반적인 예외 순으로 작성하세요. 한글 처리 시에는 UTF-8 인코딩을 기본으로 사용합니다.

**다음 장에서 만나요!** 
