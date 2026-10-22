# 레퍼런스 E. 표준 라이브러리 지도

파이썬을 설치하면 따라오는 모듈이 200개가 넘습니다. 17장에서 자주 쓰는 것들을 골라 써 봤다면, 이 지도는 "이런 일을 하는 모듈이 표준에 있었나?" 싶을 때 펼쳐 보는 자료예요. 외부 패키지를 설치하기 전에 여기서 먼저 찾아보세요. 용도별로 묶었고, 본문에서 그 모듈을 실제로 쓴 장을 함께 적었습니다.

표에 실은 모듈은 모두 Python 3.12에서 `import`가 되는 것을 확인했고, 대표 함수·클래스 이름도 실제 모듈에 있는지 하나하나 확인했습니다. 전체 목록은 `sys.stdlib_module_names`로 직접 볼 수 있어요.

```python
import sys

names = sorted(m for m in sys.stdlib_module_names if not m.startswith("_"))
print(len(names))   # 212
print(names[:6])    # ['abc', 'aifc', 'antigravity', 'argparse', 'array', 'ast']
```

밑줄로 시작하는 내부용 모듈까지 세면 301개, 빼면 212개입니다(3.12 기준). 이 목록에는 운영체제에 따라 없는 모듈(윈도우 전용 `winreg`, `msvcrt` 등)과 3.13에서 사라질 모듈도 들어 있어요. 아래 표에는 그중 실무에서 손이 자주 가는 101개만 실었습니다. 이름이 `a.b`처럼 점으로 이어진 것은 패키지 안의 하위 모듈입니다.

## 텍스트 처리

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `string` | 문자 상수 모음과 간단한 템플릿 | `ascii_letters`, `digits`, `punctuation`, `Template` | 17 |
| `re` | 정규 표현식으로 찾기·바꾸기·나누기 | `compile`, `search`, `match`, `fullmatch`, `findall`, `sub`, `split` | 10, 17 |
| `textwrap` | 긴 문장을 정해진 폭으로 줄바꿈·들여쓰기 | `wrap`, `fill`, `shorten`, `dedent`, `indent` | 17 |
| `unicodedata` | 유니코드 문자 정보와 정규화(NFC·NFD) | `normalize`, `name`, `category`, `east_asian_width` | 17 |
| `difflib` | 두 텍스트의 차이 비교, 비슷한 문자열 찾기 | `SequenceMatcher`, `unified_diff`, `get_close_matches` |  |
| `codecs` | 문자 인코딩 변환기 등록·조회 | `open`, `lookup`, `encode`, `decode`, `BOM_UTF8` |  |

## 이진 데이터

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `struct` | 파이썬 값과 C 구조체 바이트를 서로 변환 | `pack`, `unpack`, `calcsize`, `Struct` |  |
| `array` | 한 가지 숫자 타입만 담는 빽빽한 배열 | `array`, `typecodes` |  |
| `base64` | 바이트를 Base64·Base32·Base16 글자로 변환 | `b64encode`, `b64decode`, `urlsafe_b64encode` |  |

## 날짜와 시간

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `datetime` | 날짜·시각·기간 계산과 서식 | `date`, `time`, `datetime`, `timedelta`, `timezone` | 17 |
| `zoneinfo` | IANA 시간대 정보(Asia/Seoul 등) | `ZoneInfo`, `available_timezones` | 17 |
| `time` | 유닉스 시간, 잠시 멈추기, 성능 측정용 시계 | `time`, `sleep`, `perf_counter`, `monotonic`, `strftime` | 17 |
| `calendar` | 달력 출력, 윤년·요일 계산 | `monthrange`, `isleap`, `weekday`, `TextCalendar` | 17 |

## 자료구조

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `collections` | 특수 컨테이너 자료형 | `Counter`, `defaultdict`, `deque`, `namedtuple`, `OrderedDict`, `ChainMap` | 07, 08, 17 |
| `collections.abc` | 컨테이너 추상 기반 클래스(무엇을 구현해야 하나) | `Iterable`, `Iterator`, `Sequence`, `Mapping`, `Callable` | 15 |
| `heapq` | 리스트를 최소 힙으로 쓰기(우선순위 큐) | `heappush`, `heappop`, `nlargest`, `nsmallest` |  |
| `bisect` | 정렬된 리스트에서 이진 탐색·삽입 | `bisect_left`, `bisect_right`, `insort` |  |
| `enum` | 이름 붙은 상수 집합 | `Enum`, `IntEnum`, `StrEnum`, `Flag`, `auto` | 08 |
| `dataclasses` | 데이터 담는 클래스 자동 생성 | `dataclass`, `field`, `asdict`, `replace`, `fields` | 08 |
| `copy` | 얕은 복사와 깊은 복사 | `copy`, `deepcopy` |  |
| `weakref` | 객체를 붙잡지 않는 약한 참조 | `ref`, `WeakValueDictionary`, `WeakKeyDictionary`, `finalize` | 17 |
| `pprint` | 중첩 자료구조를 보기 좋게 출력 | `pprint`, `pformat`, `PrettyPrinter` |  |
| `graphlib` | 의존 관계 그래프의 위상 정렬 | `TopologicalSorter` |  |

## 수학과 통계

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `math` | 실수 수학 함수와 상수 | `sqrt`, `floor`, `ceil`, `isclose`, `gcd`, `comb`, `pi`, `inf` | 03 |
| `decimal` | 오차 없는 10진 소수 계산(돈 계산) | `Decimal`, `getcontext`, `localcontext`, `ROUND_HALF_UP` | 03, 17 |
| `fractions` | 분수(유리수) 계산 | `Fraction` |  |
| `random` | 의사 난수(게임·시뮬레이션용) | `random`, `randint`, `choice`, `choices`, `sample`, `shuffle`, `seed` | 08, 15 |
| `statistics` | 평균·중앙값·표준편차 같은 기초 통계 | `mean`, `median`, `mode`, `stdev`, `quantiles`, `correlation` | 08, 17 |

## 함수형 도구

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `itertools` | 반복자를 잇고 자르고 조합하는 도구 | `chain`, `islice`, `groupby`, `product`, `permutations`, `combinations`, `batched` | 10, 17 |
| `functools` | 함수를 감싸고 고치는 도구 | `reduce`, `partial`, `lru_cache`, `cache`, `wraps`, `total_ordering`, `singledispatch` | 10, 17 |
| `operator` | 연산자를 함수로 꺼내 쓰기 | `add`, `itemgetter`, `attrgetter`, `methodcaller` | 10 |

## 파일과 경로

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `pathlib` | 경로를 객체로 다루기 | `Path`, `PurePath` | 12, 17 |
| `os.path` | 경로를 문자열로 다루던 예전 방식 | `join`, `exists`, `basename`, `splitext`, `abspath` | 12 |
| `io` | 파일 객체의 기반 클래스, 메모리 속 파일 | `StringIO`, `BytesIO`, `TextIOWrapper`, `open` | 17 |
| `glob` | 와일드카드 패턴으로 파일 찾기 | `glob`, `iglob`, `escape` |  |
| `shutil` | 파일·폴더 복사, 이동, 삭제, 압축 | `copy2`, `copytree`, `move`, `rmtree`, `make_archive`, `which` | 12, 17 |
| `tempfile` | 임시 파일·폴더 만들기 | `TemporaryDirectory`, `NamedTemporaryFile`, `mkstemp` |  |

## 직렬화와 압축

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `json` | JSON 읽고 쓰기 | `dump`, `dumps`, `load`, `loads`, `JSONDecodeError` | 12, 17 |
| `csv` | CSV 읽고 쓰기 | `reader`, `writer`, `DictReader`, `DictWriter` | 12, 17 |
| `pickle` | 파이썬 객체를 바이트로 저장(믿을 수 있는 데이터만) | `dump`, `dumps`, `load`, `loads` | 12, 17 |
| `sqlite3` | 파일 하나짜리 SQL 데이터베이스 | `connect`, `Connection`, `Cursor`, `Row` | 18 |
| `tomllib` | TOML 읽기 전용(pyproject.toml 등) | `load`, `loads` |  |
| `configparser` | INI 형식 설정 파일 | `ConfigParser` | 17 |
| `gzip` | .gz 파일 압축·해제 | `open`, `compress`, `decompress` |  |
| `lzma` | .xz 파일 압축·해제 | `open`, `compress`, `decompress` |  |
| `zipfile` | .zip 파일 만들고 풀기 | `ZipFile`, `is_zipfile` |  |
| `tarfile` | .tar(.gz) 파일 만들고 풀기 | `open`, `TarFile` |  |

## 암호와 해시

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `hashlib` | SHA-256 같은 해시, 비밀번호용 키 유도 | `sha256`, `md5`, `blake2b`, `pbkdf2_hmac`, `scrypt` | 19 |
| `hmac` | 비밀 키를 섞은 메시지 인증 코드 | `new`, `digest`, `compare_digest` | 19 |
| `secrets` | 보안용 난수(토큰, 임시 비밀번호) | `token_hex`, `token_urlsafe`, `choice`, `compare_digest` | 19 |

## 운영체제

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `os` | 환경 변수, 프로세스, 파일 시스템 등 운영체제 기능 | `environ`, `getenv`, `listdir`, `makedirs`, `walk`, `getcwd` | 12, 17 |
| `platform` | 운영체제·파이썬 버전 정보 | `system`, `platform`, `python_version`, `machine` | 17 |
| `argparse` | 명령줄 인자 해석 | `ArgumentParser` |  |
| `shlex` | 셸 명령줄을 나누고 안전하게 따옴표 치기 | `split`, `quote`, `join` |  |
| `signal` | Ctrl+C 같은 운영체제 신호 처리 | `signal`, `SIGINT`, `SIGTERM` |  |
| `ctypes` | C 공유 라이브러리 함수 부르기 | `CDLL`, `c_int`, `c_char_p`, `Structure` |  |

## 동시성

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `threading` | 스레드로 동시에 일하기 | `Thread`, `Lock`, `RLock`, `Event`, `Semaphore` | 17 |
| `multiprocessing` | 프로세스 여러 개로 CPU 코어 함께 쓰기 | `Process`, `Pool`, `Queue`, `cpu_count` | 15 |
| `concurrent.futures` | 스레드·프로세스 풀의 간단한 공통 인터페이스 | `ThreadPoolExecutor`, `ProcessPoolExecutor`, `as_completed` | 17 |
| `asyncio` | async/await 기반 비동기 실행 | `run`, `gather`, `create_task`, `sleep`, `Queue`, `Lock`, `TaskGroup` | 15, 17 |
| `subprocess` | 외부 프로그램 실행 | `run`, `Popen`, `PIPE`, `CalledProcessError` | 14, 17 |
| `queue` | 스레드 사이에 안전하게 주고받는 큐 | `Queue`, `LifoQueue`, `PriorityQueue`, `Empty` | 17 |
| `contextvars` | 비동기 작업마다 따로 갖는 변수 | `ContextVar`, `copy_context` |  |

## 네트워크와 인터넷

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `socket` | 저수준 네트워크 통신 | `socket`, `create_connection`, `gethostname`, `AF_INET` |  |
| `ssl` | TLS 암호화 연결 | `create_default_context`, `SSLContext` |  |
| `urllib.request` | URL 열기(HTTP 요청) | `urlopen`, `Request` | 17 |
| `urllib.parse` | URL 나누고 조립하기, 쿼리 문자열 인코딩 | `urlparse`, `urlencode`, `quote`, `parse_qs`, `urljoin` | 17 |
| `http.server` | 간단한 HTTP 서버(개발·테스트용) | `HTTPServer`, `SimpleHTTPRequestHandler` | 17 |
| `http` | HTTP 상태 코드와 메서드 상수 | `HTTPStatus`, `HTTPMethod` |  |
| `smtplib` | SMTP로 메일 보내기 | `SMTP`, `SMTP_SSL` |  |
| `ipaddress` | IPv4·IPv6 주소와 네트워크 계산 | `ip_address`, `ip_network`, `IPv4Address` |  |
| `uuid` | 겹치지 않는 고유 식별자 | `uuid4`, `uuid1`, `UUID` | 14 |

## 인터넷 데이터 처리

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `email` | 메일 메시지 만들고 해석하기 | `message.EmailMessage`, `parser`, `policy` |  |
| `mimetypes` | 파일 확장자와 MIME 형식 대응 | `guess_type`, `guess_extension` |  |
| `html` | HTML 특수 문자 이스케이프 | `escape`, `unescape` |  |
| `xml.etree.ElementTree` | XML 읽고 쓰기 | `parse`, `fromstring`, `Element`, `SubElement` |  |

## 개발 도구

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `logging` | 레벨별 로그 기록 | `getLogger`, `basicConfig`, `Logger`, `Handler`, `Formatter` | 12, 17 |
| `unittest` | 클래스 기반 단위 테스트 | `TestCase`, `main`, `skip` |  |
| `unittest.mock` | 테스트용 가짜 객체 | `Mock`, `MagicMock`, `patch` |  |
| `doctest` | docstring 속 예시를 테스트로 실행 | `testmod`, `testfile` |  |
| `pdb` | 대화형 디버거 | `set_trace`, `run`, `post_mortem` |  |
| `traceback` | 예외 추적 정보 출력·문자열화 | `print_exc`, `format_exc`, `extract_tb` | 12, 17 |
| `warnings` | 경고 내기와 경고 거르기 | `warn`, `filterwarnings`, `catch_warnings` |  |
| `timeit` | 짧은 코드의 실행 시간 측정 | `timeit`, `repeat`, `Timer` | 07 |
| `cProfile` | 함수별 실행 시간 프로파일링 | `run`, `Profile` | 17 |
| `pstats` | cProfile 결과 정렬·출력 | `Stats`, `SortKey` | 17 |
| `tracemalloc` | 메모리 할당 추적 | `start`, `take_snapshot`, `get_traced_memory` | 16 |

## 타입

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `typing` | 타입 힌트용 이름들 | `Any`, `Optional`, `Union`, `Callable`, `TypeVar`, `Protocol`, `Literal`, `TypedDict` | 08, 13 |
| `types` | 내장 타입 이름과 동적 타입 생성 | `SimpleNamespace`, `ModuleType`, `FunctionType`, `MappingProxyType` |  |
| `abc` | 추상 기반 클래스 만들기 | `ABC`, `ABCMeta`, `abstractmethod` | 13 |

## 실행 환경

| 모듈 | 무엇을 하나 | 대표 함수·클래스 | 관련 장 |
|---|---|---|---|
| `sys` | 인터프리터 정보와 설정 | `argv`, `path`, `version_info`, `exit`, `modules`, `stdin`, `stdout` | 14, 17 |
| `builtins` | 내장 함수·예외가 들어 있는 모듈 | `print`, `len`, `open` | 14 |
| `importlib` | 모듈을 이름으로 불러오기, 다시 불러오기 | `import_module`, `reload` | 14 |
| `importlib.metadata` | 설치된 패키지의 버전·메타데이터 | `version`, `distributions`, `entry_points` |  |
| `importlib.resources` | 패키지 안에 든 데이터 파일 읽기 | `files`, `as_file` |  |
| `inspect` | 실행 중인 객체 들여다보기 | `signature`, `getsource`, `getmembers`, `isfunction` | 13, 14 |
| `contextlib` | with 문 도구 | `contextmanager`, `asynccontextmanager`, `suppress`, `ExitStack`, `closing` | 16, 17 |
| `gc` | 가비지 컬렉터 제어 | `collect`, `disable`, `get_count` |  |
| `ast` | 파이썬 코드를 문법 트리로 해석 | `parse`, `literal_eval`, `dump`, `NodeVisitor` | 14 |
| `keyword` | 예약어 목록 | `kwlist`, `softkwlist`, `iskeyword` | 02, 14 |
| `venv` | 가상 환경 만들기(python -m venv) | `create`, `EnvBuilder` | 14 |

## 사라진 모듈과 사라질 모듈

오래된 책이나 블로그 글의 코드가 `ModuleNotFoundError`를 낸다면 아래 표부터 확인하세요. 오래 관리되지 않은 모듈을 정리하자는 제안(PEP 594, 별명 "dead batteries", 다 닳은 건전지)과 `distutils` 폐지 제안(PEP 632)에 따라 3.12와 3.13에서 차례로 빠졌습니다. 대체 수단은 공식 문서 "What's New in Python 3.12/3.13"에 적힌 것만 옮겼어요.

### 3.12에서 제거된 모듈

| 모듈 | 하던 일 | 대신 쓸 것 |
|---|---|---|
| `distutils` | 패키지 빌드·설치 | `setuptools`(외부 패키지, `distutils`도 계속 제공), 14장의 uv |
| `imp` | 모듈 찾기·불러오기 | `importlib`(`import_module`, `reload`, `util.find_spec`), `types.ModuleType` |
| `asynchat` | 비동기 소켓 채팅 도우미 | `asyncio` |
| `asyncore` | 비동기 소켓 처리 | `asyncio` |
| `smtpd` | SMTP 서버 | `aiosmtpd`(외부 패키지) 같은 asyncio 기반 서버 |

### 3.13에서 제거된 모듈

3.12에서는 아직 `import`가 되지만, 대부분 불러오는 순간 `DeprecationWarning: 'telnetlib' is deprecated and slated for removal in Python 3.13` 같은 경고가 나옵니다. 아래 21개는 `uv run --python 3.13`으로 하나씩 불러 보아 모두 `ModuleNotFoundError`가 나는 것을 확인했습니다. 대부분 PyPI에 `standard-이름` 꼴의 복원 패키지가 있지만, 새 코드라면 오른쪽 열의 대체 수단을 쓰세요.

| 모듈 | 하던 일 | 대신 쓸 것 |
|---|---|---|
| `aifc` | AIFF 오디오 파일 | `standard-aifc` |
| `audioop` | 오디오 샘플 연산 | `audioop-lts` |
| `cgi` | CGI 요청 해석 | `urllib.parse.parse_qsl()`·`parse_qs()`, `email.message`, `multipart` |
| `cgitb` | CGI 오류 보고 | `standard-cgitb` |
| `chunk` | IFF 청크 읽기 | `standard-chunk` |
| `crypt` | 유닉스 비밀번호 해시 | `hashlib`, `bcrypt`, `argon2-cffi` |
| `imghdr` | 이미지 형식 알아내기 | `filetype`, `puremagic`, `python-magic` |
| `mailcap` | mailcap 파일 처리 | `mimetypes` |
| `msilib` | 윈도우 설치 파일(MSI) | (공식 안내 없음) |
| `nis` | 썬 NIS 조회 | (공식 안내 없음) |
| `nntplib` | 뉴스그룹(NNTP) | `pynntp` |
| `ossaudiodev` | OSS 오디오 장치 | `pygame` |
| `pipes` | 셸 파이프라인 | `subprocess`, `shlex.quote()` |
| `sndhdr` | 소리 파일 형식 알아내기 | `filetype`, `puremagic`, `python-magic` |
| `spwd` | 유닉스 섀도 비밀번호 | `python-pam` |
| `sunau` | Sun AU 오디오 파일 | `standard-sunau` |
| `telnetlib` | 텔넷 클라이언트 | `telnetlib3`, `Exscript` |
| `uu` | uuencode 인코딩 | `base64` |
| `xdrlib` | XDR 데이터 | `standard-xdrlib` |
| `lib2to3` | 2to3 변환 도구의 기반 | (2to3 도구와 함께 제거) |
| `tkinter.tix` | Tk 확장 위젯 | (공식 안내 없음, 3.6부터 폐지 예고) |

> **Q. `msilib`, `nis`, `spwd`, `ossaudiodev`는 3.12에서도 import가 안 되던데요?**
> 이 넷은 특정 운영체제에서만 만들어지는 모듈이에요. `msilib`은 윈도우, 나머지는 리눅스 같은 유닉스 계열에서만 빌드됩니다. 그래서 macOS의 3.12에서는 `sys.stdlib_module_names`에는 이름이 있지만 불러오면 `ModuleNotFoundError`가 납니다. 이름이 표준 목록에 있다고 해서 모든 컴퓨터에서 쓸 수 있는 것은 아니라는 점을 기억해 두세요.
