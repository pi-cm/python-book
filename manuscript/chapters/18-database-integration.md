# Chapter 18: 데이터베이스 연동

> **학습 목표**  
> - SQLite로 테이블을 만들고 SQL로 데이터 다루기
> - 트랜잭션과 예외 처리로 데이터를 안전하게 지키기
> - ORM과 SQLAlchemy의 개념 이해하기
> - Alembic으로 스키마 변경을 관리하고 인덱스로 성능 높이기
> - SQL 인젝션을 막는 매개변수화된 쿼리 쓰기

---

## 들어가며: 엑셀 파일로는 왜 부족할까요?

작은 가게의 손님 명단이라면 엑셀 파일 하나로 충분합니다. 그런데 가게가 커져서 직원 열 명이 동시에 주문을 입력하고, 손님이 만 명으로 늘고, "지난달 강남구 손님이 산 상품 중 재고가 50개 미만인 것"을 찾아야 한다면 어떨까요? 누군가 파일을 열어 둔 사이에 다른 사람이 저장하면 한쪽 내용이 사라지고, 원하는 조건으로 찾으려면 필터를 몇 번이나 걸어야 합니다.

이럴 때 쓰는 것이 **데이터베이스(database)** 입니다. 도서관을 떠올려 보세요. 책(데이터)은 서가에 규칙대로 꽂혀 있고, 우리는 서가를 직접 뒤지는 대신 사서에게 "파이썬 책 중에 2020년 이후에 나온 것 주세요"라고 **부탁**합니다. 사서는 색인 카드를 보고 빠르게 찾아 주고, 여러 사람이 동시에 빌리고 반납해도 장부가 꼬이지 않게 관리하죠.

데이터베이스에서 이 사서 역할을 하는 프로그램을 **DBMS**(데이터베이스 관리 시스템)라 하고, 사서에게 부탁하는 말이 **SQL**입니다. 이 장에서는 파이썬에서 SQL로 데이터베이스에 부탁하는 방법을 배우고, 이어서 SQL 대신 파이썬 객체로 부탁하는 방법(ORM)까지 살펴봅니다. 이 장의 예제는 처음부터 끝까지 이어지는 하나의 프로그램이에요. 앞에서 만든 `get_connection()`과 테이블을 뒤에서 계속 씁니다.

## 18.1 SQLite 기초와 Python 연동

### SQLite 소개

데이터베이스라고 하면 MySQL, PostgreSQL처럼 서버를 따로 설치하고 띄워 둬야 하는 프로그램을 떠올리기 쉽습니다. **SQLite**는 다릅니다. 데이터베이스 전체가 **파일 하나**예요. 서버를 설치할 필요도, 계정을 만들 필요도 없습니다. 그래서 공부하거나, 작은 프로그램을 만들거나, 큰 서비스를 만들기 전에 시험해 볼 때 딱 좋습니다. 스마트폰 앱들도 기기 안에 데이터를 저장할 때 SQLite를 많이 써요.

무엇보다 파이썬에는 `sqlite3` 모듈이 표준 라이브러리로 들어 있어서, 아무것도 설치하지 않고 바로 쓸 수 있습니다.

### 첫 번째 데이터베이스 연결

데이터베이스와 대화하는 순서는 늘 같습니다.

1. **연결(connect)**: `sqlite3.connect("파일이름")`으로 데이터베이스 파일을 엽니다. 파일이 없으면 새로 만들어요.
2. **실행(execute)**: SQL 문장을 문자열로 건넵니다.
3. **확정(commit)**: 바꾼 내용을 파일에 확정합니다. 확정하기 전까지는 임시 상태예요.

첫 SQL은 `CREATE TABLE`, 표(테이블)를 만드는 문장입니다. 괄호 안에 열 이름과 자료형, 그리고 지켜야 할 규칙을 적어요. `PRIMARY KEY`는 행마다 하나뿐인 번호(주민등록번호 같은 것), `AUTOINCREMENT`는 그 번호를 1, 2, 3… 자동으로 매기라는 뜻이고, `NOT NULL`은 비워 두면 안 되는 칸, `UNIQUE`는 다른 행과 겹치면 안 되는 칸입니다. `IF NOT EXISTS`를 붙였으니 이미 테이블이 있으면 조용히 넘어가요. 그래서 이 코드는 여러 번 실행해도 안전합니다.

```python
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime

# 데이터베이스 파일 경로 설정
db_path = Path("korea_company.db")

# 데이터베이스 연결
def get_connection():
    """데이터베이스 연결을 반환합니다. with 블록이 끝나면 연결을 닫습니다."""
    return closing(sqlite3.connect(db_path))

# 첫 번째 테이블 생성
def create_employees_table():
    """직원 테이블을 생성합니다."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                position TEXT NOT NULL,
                salary INTEGER NOT NULL,
                hire_date DATE NOT NULL,
                email TEXT UNIQUE
            )
        """)
        conn.commit()

# 테이블 생성 실행
create_employees_table()
print("직원 테이블이 생성되었습니다.")
```

실행하고 나면 폴더에 `korea_company.db` 파일이 생깁니다. 이 파일 하나가 데이터베이스 전체예요. 복사하면 백업이 되고, 다른 컴퓨터로 옮기면 데이터가 통째로 따라갑니다.

> **Q. `with get_connection() as conn:`을 쓰면 블록이 끝날 때 연결도 닫히나요?**
> 닫힙니다. 그런데 그건 `get_connection()`이 연결을 `contextlib.closing()`으로 감싸 두었기 때문이에요. 12장에서 `with open(...)`이 블록 끝에서 파일을 닫아 준 것과 헷갈리기 쉬운데, `sqlite3.connect()`가 돌려준 연결을 그대로 `with`에 쓰면 **확정(commit)과 취소(rollback)만** 맡습니다. 블록이 무사히 끝나면 commit, 예외가 나면 rollback을 하고, 연결 자체는 열어 둔 채로 남겨요. 그러면 함수를 부를 때마다 열린 연결이 쌓이고, 경고를 켜고(`python -W default`) 실행했을 때 `ResourceWarning: unclosed database`가 찍힙니다. `closing(연결)`은 반대로 **닫기만** 해 주는 감싸개입니다. 그래서 이 장의 함수들은 데이터를 바꾼 뒤 `conn.commit()`을 직접 부르고, 블록이 끝나면 `closing`이 연결을 닫습니다.

### 데이터 삽입과 조회

이제 표에 줄을 채워 넣을 차례입니다. `INSERT INTO 테이블 (열들) VALUES (값들)`이 한 줄을 넣는 SQL이에요.

여기서 가장 중요한 것은 값 자리에 쓴 **물음표(`?`)** 입니다. 값을 SQL 문자열에 직접 끼워 넣지 않고, 자리만 표시해 둔 다음 실제 값은 튜플로 따로 건네요. 이렇게 하면 값에 따옴표 같은 특수 문자가 섞여 있어도 sqlite3가 알아서 안전하게 처리해 줍니다. 왜 이게 그렇게 중요한지는 18.10절에서 직접 확인합니다.

같은 이메일로 두 번 넣으려고 하면 `UNIQUE` 규칙에 걸려 `sqlite3.IntegrityError`가 납니다. 아래 함수는 이 예외를 잡아서 메시지만 출력해요. 그래서 이 예제를 두 번째 실행하면 다섯 명 모두 `오류 발생: UNIQUE constraint failed: employees.email`이 찍힙니다. 이미 들어 있는 사람이니까요.

```python
def add_employee(name: str, department: str, position: str, 
                salary: int, email: str):
    """새 직원을 추가합니다."""
    with get_connection() as conn:
        try:
            conn.execute("""
                INSERT INTO employees (name, department, position, salary, hire_date, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, department, position, salary, datetime.now().date().isoformat(), email))
            conn.commit()
            print(f"{name} 직원이 추가되었습니다.")
        except sqlite3.IntegrityError as e:
            print(f"오류 발생: {e}")

# 샘플 데이터 추가
employees_data = [
    ("김철수", "개발팀", "시니어 개발자", 7000000, "kim.cs@company.co.kr"),
    ("박영희", "마케팅팀", "마케팅 매니저", 6000000, "park.yh@company.co.kr"),
    ("이민수", "인사팀", "인사 담당자", 5500000, "lee.ms@company.co.kr"),
    ("정수진", "개발팀", "주니어 개발자", 4500000, "jung.sj@company.co.kr"),
    ("최동욱", "영업팀", "영업 대표", 6500000, "choi.dw@company.co.kr")
]

for employee in employees_data:
    add_employee(*employee)
```

`add_employee(*employee)`의 `*`는 튜플을 풀어서 인자 다섯 개로 나눠 넘긴다는 뜻입니다. 입사일은 `datetime.now().date().isoformat()`으로 `'2024-01-15'` 같은 문자열로 바꿔 넘겼어요. SQLite에는 날짜 전용 자료형이 따로 없어서 어차피 문자열로 저장되거든요. 날짜 객체를 그대로 넘겨도 저장은 되지만, 파이썬 3.12부터는 "기본 날짜 변환기는 앞으로 없어진다"는 `DeprecationWarning`이 나옵니다(경고를 켜야 보입니다). 처음부터 문자열로 바꿔 넘기는 습관을 들이면 좋습니다. 그리고 `salary` 열에는 **월급**을 원 단위로 저장합니다.

### 데이터 조회와 표시

넣었으면 꺼내 봐야죠. 꺼내는 SQL은 `SELECT 열들 FROM 테이블`이고, `ORDER BY`로 정렬 순서를 정합니다. `conn.execute()`는 **커서(cursor)** 를 돌려주는데, 커서는 결과 묶음을 가리키는 손가락이라고 생각하면 됩니다. `fetchall()`은 남은 결과를 모두 튜플의 리스트로, `fetchone()`은 한 줄만 꺼내요.

```python
def get_all_employees():
    """모든 직원 정보를 조회합니다."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, name, department, position, salary, hire_date, email
            FROM employees
            ORDER BY department, position
        """)
        return cursor.fetchall()

def display_employees():
    """직원 목록을 보기 좋게 출력합니다."""
    employees = get_all_employees()
    
    print("\n=== 직원 목록 ===")
    print(f"{'ID':<3} {'이름':<8} {'부서':<10} {'직급':<15} {'월급':<10} {'입사일':<12} {'이메일'}")
    print("-" * 80)
    
    for emp in employees:
        emp_id, name, dept, pos, salary, hire_date, email = emp
        print(f"{emp_id:<3} {name:<8} {dept:<10} {pos:<15} {salary:,}원 {hire_date:<12} {email}")

# 직원 목록 출력
display_employees()
```

출력된 목록은 부서 이름의 가나다순(개발팀, 마케팅팀, 영업팀, 인사팀)으로, 같은 부서 안에서는 직급 이름순으로 정렬됩니다. ID가 1, 4, 2, 5, 3 순서로 섞여 나오는 것도 그 때문이에요. 데이터베이스는 `ORDER BY`를 쓰지 않으면 순서를 약속하지 않습니다. 순서가 중요하면 반드시 정렬을 요청하세요.

한 가지 더, 출력해 보면 열이 반듯하게 맞지 않습니다. `{name:<8}`은 "8칸 너비로 왼쪽 정렬"인데, 파이썬은 한글 한 글자도 1칸으로 셉니다. 하지만 터미널 화면에서 한글은 보통 영문자 두 개 너비를 차지하죠. 그래서 한글이 섞인 열은 오른쪽으로 밀려 보입니다. 한글 표를 반듯하게 맞추려면 글자 너비를 따로 계산해야 하는데, 17장에서 본 `unicodedata` 모듈의 `east_asian_width()`가 그때 쓰는 도구예요.

### 조건부 조회와 필터링

전체가 아니라 조건에 맞는 줄만 원할 때는 `WHERE`를 붙입니다. 조건에 들어갈 값도 역시 `?`로 자리만 잡고 따로 넘겨요. 값이 하나뿐일 때 `(department,)`처럼 **쉼표를 붙여야** 튜플이 된다는 점을 주의하세요. 쉼표가 없으면 괄호는 그냥 묶음 기호라서 문자열이 그대로 넘어갑니다.

```python
def find_employees_by_department(department: str):
    """특정 부서의 직원들을 조회합니다."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT name, position, salary
            FROM employees
            WHERE department = ?
            ORDER BY salary DESC
        """, (department,))
        return cursor.fetchall()

def get_high_salary_employees(min_salary: int = 6000000):
    """특정 월급 이상의 직원들을 조회합니다."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT name, department, position, salary
            FROM employees
            WHERE salary >= ?
            ORDER BY salary DESC
        """, (min_salary,))
        return cursor.fetchall()

# 부서별 직원 조회
print("\n=== 개발팀 직원 ===")
dev_employees = find_employees_by_department("개발팀")
for name, position, salary in dev_employees:
    print(f"{name} - {position}: {salary:,}원")

# 고액 월급 직원 조회
print("\n=== 월급 6백만원 이상 직원 ===")
high_earners = get_high_salary_employees()
for name, dept, position, salary in high_earners:
    print(f"{name}({dept} {position}): {salary:,}원")
```

개발팀은 김철수(7,000,000원)와 정수진(4,500,000원) 두 명, 월급 600만 원 이상은 김철수·최동욱·박영희 세 명이 나옵니다. `get_high_salary_employees()`처럼 기본값이 있는 매개변수를 두면, 자주 쓰는 조건은 인자 없이 부르고 필요할 때만 바꿔 부를 수 있어요.

## 18.2 데이터베이스 설계 원칙

### 정규화의 이해

동네 빵집 주문 장부를 생각해 봅시다. 단골 김고객이 열 번 주문할 때마다 장부에 이름, 이메일, 전화번호, 주소를 매번 적는다면 어떨까요? 같은 내용을 열 번 쓰는 것도 낭비지만, 진짜 문제는 김고객이 이사했을 때입니다. 열 줄을 모두 고쳐야 하고, 하나라도 빠뜨리면 "김고객의 주소가 두 개"인 장부가 돼 버려요.

해결책은 간단합니다. **고객 명부를 따로 두고, 주문 장부에는 고객 번호만 적는 것**이죠. 주소가 바뀌면 명부 한 줄만 고치면 됩니다. 이렇게 한 가지 사실은 한 곳에만 적도록 표를 나누는 것을 **정규화(normalization)** 라고 합니다.

아래 코드의 `bad_orders`가 바로 "매번 다 적는 장부"이고, 그 아래가 고객·상품·카테고리·주문·주문 상세로 나눈 설계입니다. 표끼리는 번호로 이어져요. `FOREIGN KEY (customer_id) REFERENCES customers (customer_id)`는 "주문 표의 `customer_id`는 고객 표에 실제로 있는 번호여야 한다"는 약속입니다. 이렇게 다른 표를 가리키는 열을 **외래 키(foreign key)** 라고 해요.

`order_items` 표가 따로 있는 이유도 보세요. 주문 하나에는 상품이 여러 개 들어가고, 상품 하나는 여러 주문에 들어갑니다. 이런 **다대다** 관계는 두 표만으로는 표현할 수 없어서, "몇 번 주문에 몇 번 상품이 몇 개"를 한 줄씩 적는 표를 가운데 둡니다. 영수증의 품목 한 줄 한 줄이 이 표의 행이라고 생각하면 됩니다.

```python
# 정규화되지 않은 설계 (문제가 있는 예시)
def create_bad_orders_table():
    """잘못된 주문 테이블 설계"""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bad_orders (
                order_id INTEGER PRIMARY KEY,
                customer_name TEXT,
                customer_email TEXT,
                customer_phone TEXT,
                product_name TEXT,
                product_price INTEGER,
                quantity INTEGER,
                order_date DATE
            )
        """)

# 정규화된 설계
def create_normalized_tables():
    """정규화된 테이블들을 생성합니다."""
    with get_connection() as conn:
        # 고객 테이블
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 상품 테이블
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                price INTEGER NOT NULL,
                description TEXT,
                stock_quantity INTEGER DEFAULT 0,
                category_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 카테고리 테이블
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        """)
        
        # 주문 테이블
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                total_amount INTEGER NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)
        
        # 주문 상세 테이블 (다대다 관계 해결)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        """)
        
        conn.commit()

# 정규화된 테이블 생성
create_normalized_tables()
print("정규화된 테이블들이 생성되었습니다.")
```

한 가지 놀라운 사실이 있습니다. SQLite는 외래 키 약속을 **기본적으로 검사하지 않아요**. 하위 호환성 때문에 검사 기능이 꺼진 채로 시작합니다. 그래서 지금 상태로는 고객 표에 없는 999번 고객의 주문도 아무 오류 없이 들어갑니다. 검사를 켜려면 연결할 때마다 `conn.execute("PRAGMA foreign_keys = ON")`을 먼저 실행해야 해요. 이 설정은 진행 중인 트랜잭션 안에서는 무시되므로, 연결하자마자 다른 문장보다 먼저 실행하는 것이 안전합니다. 켜고 나서 없는 고객 번호로 주문을 넣으면 `sqlite3.IntegrityError: FOREIGN KEY constraint failed`가 납니다. MySQL이나 PostgreSQL 같은 서버형 데이터베이스는 처음부터 검사합니다.

### 샘플 데이터 추가

나눈 표에 데이터를 채웁니다. 상품을 넣을 때 카테고리를 이름이 아니라 번호(`category_id` 1~4)로 적는 것을 보세요. 정규화된 설계에서는 이렇게 **번호로 서로를 가리킵니다**. 1번이 전자제품인 것은 카테고리를 넣은 순서대로 번호가 매겨졌기 때문이에요.

`INSERT OR IGNORE`는 "넣다가 규칙(UNIQUE 등)에 걸리면 오류를 내지 말고 그 줄은 건너뛰라"는 SQLite의 문법입니다. 그런데 걸릴 규칙이 있어야 건너뛰겠죠? 그래서 앞의 테이블 설계에서 고객의 이메일뿐 아니라 카테고리와 상품의 이름(`name TEXT UNIQUE NOT NULL`)에도 `UNIQUE`를 걸어 두었습니다. 덕분에 이 예제를 몇 번을 다시 실행해도 이미 있는 카테고리·고객·상품은 건너뛰어서, 같은 데이터가 두 벌 생기지 않아요. 이름에 `UNIQUE`가 없다면 실행할 때마다 '전자제품' 카테고리가 하나씩 늘고, 다음 절의 통계도 그만큼 부풀었을 겁니다. 중복되면 안 되는 열에는 처음부터 `UNIQUE`를 걸어 두는 것이 정답입니다. 그래도 예제를 처음 상태부터 다시 돌려 보고 싶다면 `korea_company.db` 파일을 지우고 시작하세요.

```python
def add_sample_data():
    """정규화된 테이블에 샘플 데이터를 추가합니다."""
    with get_connection() as conn:
        # 카테고리 추가
        categories = [
            ("전자제품", "컴퓨터, 스마트폰 등"),
            ("의류", "남성복, 여성복, 신발"),
            ("도서", "소설, 교육서, 전문서적"),
            ("가전제품", "냉장고, 세탁기, 에어컨")
        ]
        
        for name, desc in categories:
            conn.execute(
                "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                (name, desc)
            )
        
        # 고객 추가
        customers = [
            ("김고객", "kim@email.com", "010-1234-5678", "서울시 강남구"),
            ("이구매자", "lee@email.com", "010-2345-6789", "부산시 해운대구"),
            ("박소비자", "park@email.com", "010-3456-7890", "대구시 수성구"),
        ]
        
        for name, email, phone, address in customers:
            conn.execute("""
                INSERT OR IGNORE INTO customers (name, email, phone, address)
                VALUES (?, ?, ?, ?)
            """, (name, email, phone, address))
        
        # 상품 추가
        products = [
            ("갤럭시 스마트폰", 1200000, "최신 안드로이드 스마트폰", 50, 1),
            ("아이패드", 800000, "태블릿 컴퓨터", 30, 1),
            ("나이키 운동화", 150000, "편안한 러닝화", 100, 2),
            ("Python 프로그래밍", 35000, "초보자를 위한 파이썬 책", 200, 3),
            ("LG 냉장고", 1500000, "대용량 냉장고", 20, 4),
        ]
        
        for name, price, desc, stock, category_id in products:
            conn.execute("""
                INSERT OR IGNORE INTO products 
                (name, price, description, stock_quantity, category_id)
                VALUES (?, ?, ?, ?, ?)
            """, (name, price, desc, stock, category_id))
        
        conn.commit()

add_sample_data()
print("샘플 데이터가 추가되었습니다.")
```

## 18.3 SQL 쿼리 심화

표를 나눠 두면 중복은 사라지지만, 이번엔 반대 문제가 생깁니다. 상품 목록을 보여 줄 때 카테고리 이름이 필요한데, 상품 표에는 번호만 있죠. 흩어 놓은 정보를 필요할 때 다시 모으는 것이 이 절의 내용입니다.

### JOIN을 활용한 복합 조회

**JOIN**은 두 표를 짝 맞춰 옆으로 붙입니다. `products p JOIN categories c ON p.category_id = c.category_id`는 "상품의 카테고리 번호와 카테고리의 번호가 같은 줄끼리 붙여라"라는 뜻이에요. `products p`의 `p`는 표에 붙인 짧은 별명(alias)이라, 이후로는 `p.name`, `c.name`처럼 어느 표의 열인지 구분해서 쓸 수 있습니다. 두 표 모두 `name` 열이 있으니 별명 없이는 헷갈리겠죠. `AS product_name`은 결과 열에 붙이는 새 이름입니다.

```python
def get_products_with_category():
    """카테고리 정보와 함께 상품을 조회합니다."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT p.name as product_name, p.price, p.stock_quantity,
                   c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            ORDER BY c.name, p.price DESC
        """)
        return cursor.fetchall()

def display_products_with_category():
    """상품 목록을 카테고리와 함께 출력합니다."""
    products = get_products_with_category()
    
    print("\n=== 상품 목록 (카테고리별) ===")
    current_category = ""
    
    for product_name, price, stock, category_name in products:
        if category_name != current_category:
            current_category = category_name
            print(f"\n[{category_name}]")
            print("-" * 40)
        
        print(f"  {product_name:<20} {price:>10,}원 (재고: {stock}개)")

display_products_with_category()
```

결과는 카테고리 이름순(가전제품, 도서, 의류, 전자제품)으로, 같은 카테고리 안에서는 비싼 순으로 나옵니다. `display_products_with_category()`는 바로 앞 줄과 카테고리가 바뀔 때만 `[가전제품]` 같은 제목을 찍어요. SQL이 정렬을 해 줬기 때문에 가능한 방법입니다. 같은 카테고리가 줄줄이 붙어 나온다는 보장이 있으니까요.

### 집계 함수와 그룹화

`COUNT`, `AVG`, `MIN`, `MAX`, `SUM`은 여러 줄을 숫자 하나로 요약하는 **집계 함수**입니다. `GROUP BY`와 함께 쓰면 그룹마다 따로 요약해요. 20장에서 pandas의 `groupby()`로 할 일을 데이터베이스 안에서 하는 셈입니다.

여기서는 `JOIN` 대신 `LEFT JOIN`을 썼습니다. 그냥 `JOIN`은 양쪽에 짝이 있는 줄만 남기기 때문에, 상품이 하나도 없는 카테고리는 결과에서 아예 사라져요. `LEFT JOIN`은 왼쪽 표(카테고리)의 줄을 **짝이 없어도 모두 남기고**, 비는 칸은 `NULL`로 채웁니다. "상품 0개인 카테고리"도 통계에 나와야 하니 이쪽이 맞는 선택이죠. 파이썬 쪽에서는 `NULL`이 `None`으로 넘어오기 때문에, `display_category_statistics()`가 `avg_price or 0`처럼 `None`을 0으로 바꿔 주는 처리를 해 둔 것입니다.

```python
def get_category_statistics():
    """카테고리별 통계를 조회합니다."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT c.name as category_name,
                   COUNT(p.product_id) as product_count,
                   AVG(p.price) as avg_price,
                   MIN(p.price) as min_price,
                   MAX(p.price) as max_price,
                   SUM(p.stock_quantity) as total_stock
            FROM categories c
            LEFT JOIN products p ON c.category_id = p.category_id
            GROUP BY c.category_id, c.name
            ORDER BY product_count DESC
        """)
        return cursor.fetchall()

def display_category_statistics():
    """카테고리 통계를 출력합니다."""
    stats = get_category_statistics()
    
    print("\n=== 카테고리별 통계 ===")
    print(f"{'카테고리':<10} {'상품수':<6} {'평균가격':<12} {'최저가격':<12} {'최고가격':<12} {'총재고'}")
    print("-" * 80)
    
    for cat_name, count, avg_price, min_price, max_price, total_stock in stats:
        avg_price = int(avg_price) if avg_price else 0
        min_price = min_price or 0
        max_price = max_price or 0
        total_stock = total_stock or 0
        
        print(f"{cat_name:<10} {count:<6} {avg_price:>10,}원 {min_price:>10,}원 {max_price:>10,}원 {total_stock:>6}개")

display_category_statistics()
```

전자제품 2개(평균 1,000,000원), 나머지 카테고리는 1개씩 나옵니다. 지금은 모든 카테고리에 상품이 있어서 `JOIN`과 결과가 같지만, 상품이 없는 카테고리를 하나 추가해 보면 차이가 보입니다. `LEFT JOIN`에서는 그 카테고리가 상품 0개, 금액 0원인 줄로 나오고, 그냥 `JOIN`으로 바꾸면 그 줄이 사라져요.

### 서브쿼리 활용

"평균 가격보다 비싼 상품"을 찾으려면 평균 가격부터 알아야 합니다. SQL 문장 안에 괄호로 또 하나의 SQL을 넣으면, 안쪽 SQL의 결과를 바깥 SQL이 값처럼 쓸 수 있어요. 이것을 **서브쿼리(subquery)** 라고 합니다. 아래 `(SELECT AVG(price) FROM products)`가 먼저 계산되어 숫자 하나가 되고, 바깥 `WHERE p.price > …`가 그 숫자와 비교하는 거예요.

```python
def find_expensive_products():
    """평균 가격보다 비싼 상품들을 조회합니다."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT p.name, p.price, c.name as category
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.price > (
                SELECT AVG(price) FROM products
            )
            ORDER BY p.price DESC
        """)
        return cursor.fetchall()

def find_low_stock_products(threshold: int = 50):
    """재고가 부족한 상품들을 조회합니다."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT p.name, p.stock_quantity, c.name as category
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.stock_quantity < ?
            ORDER BY p.stock_quantity ASC
        """, (threshold,))
        return cursor.fetchall()

# 비싼 상품 조회
print("\n=== 평균가격보다 비싼 상품 ===")
expensive_products = find_expensive_products()
for name, price, category in expensive_products:
    print(f"{name}({category}): {price:,}원")

# 재고 부족 상품 조회
print("\n=== 재고 부족 상품 (50개 미만) ===")
low_stock = find_low_stock_products()
for name, stock, category in low_stock:
    print(f"{name}({category}): {stock}개 남음")
```

상품 다섯 개의 평균 가격은 737,000원이라 LG 냉장고, 갤럭시 스마트폰, 아이패드 세 개가 나옵니다. 재고 50개 미만은 LG 냉장고(20개)와 아이패드(30개)예요. 갤럭시 스마트폰은 재고가 정확히 50개라서 `< 50` 조건에 걸리지 않습니다. 경계값이 포함되는지 아닌지는 버그가 자주 숨는 곳이니, `<`와 `<=`를 고를 때 한 번 더 생각하세요.

## 18.4 트랜잭션과 예외 처리

### 트랜잭션 기초

친구에게 만 원을 계좌 이체한다고 해 봅시다. 은행 안에서는 두 가지 일이 일어납니다. ① 내 계좌에서 만 원을 빼고, ② 친구 계좌에 만 원을 더하기. 그런데 ①을 마친 순간 정전이 나면요? 내 돈은 빠졌는데 친구는 받지 못한, 만 원이 허공으로 사라진 상태가 됩니다.

그래서 데이터베이스는 여러 작업을 **한 묶음**으로 처리하는 방법을 제공합니다. 이 묶음을 **트랜잭션(transaction)** 이라고 해요. 트랜잭션 안의 작업은 **전부 성공하거나, 전부 없던 일이 되거나** 둘 중 하나입니다. 다 성공하면 `commit()`으로 확정하고, 중간에 하나라도 실패하면 `rollback()`으로 트랜잭션을 시작하기 전 상태로 되돌려요.

주문도 마찬가지입니다. 아래 함수는 ① 재고 확인, ② 주문 생성, ③ 주문 상세 추가와 재고 차감을 하나의 트랜잭션으로 묶습니다. 재고가 모자라거나 없는 상품 번호가 들어오면 ①에서 `ValueError`를 일으키고, `except`에서 `rollback()`을 부릅니다. ③을 하던 도중에 문제가 생겨도 마찬가지예요. 이미 만든 주문, 이미 깎은 재고까지 모두 트랜잭션 시작 전으로 되돌아가니, "주문은 생겼는데 재고는 그대로" 같은 어긋난 상태가 남지 않습니다. `cursor.lastrowid`는 방금 넣은 줄이 받은 번호(여기서는 주문 번호)를 알려 줍니다. 주문 상세 표에 이 번호를 적어야 하니까요. 마지막의 `finally`는 성공하든 실패하든 연결을 닫아 줍니다.

```python
def create_order_with_transaction(customer_id: int, items: list):
    """트랜잭션을 사용해 주문을 생성합니다."""
    conn = sqlite3.connect(db_path)
    
    try:
        # 트랜잭션 시작
        conn.execute("BEGIN TRANSACTION")
        
        # 1. 총 금액 계산 및 재고 확인
        total_amount = 0
        for product_id, quantity in items:
            # 상품 정보 조회
            cursor = conn.execute("""
                SELECT price, stock_quantity FROM products 
                WHERE product_id = ?
            """, (product_id,))
            
            product_info = cursor.fetchone()
            if not product_info:
                raise ValueError(f"상품 ID {product_id}가 존재하지 않습니다.")
            
            price, stock = product_info
            if stock < quantity:
                raise ValueError(f"재고가 부족합니다. 요청: {quantity}, 재고: {stock}")
            
            total_amount += price * quantity
        
        # 2. 주문 생성
        cursor = conn.execute("""
            INSERT INTO orders (customer_id, total_amount)
            VALUES (?, ?)
        """, (customer_id, total_amount))
        
        order_id = cursor.lastrowid
        
        # 3. 주문 상세 추가 및 재고 업데이트
        for product_id, quantity in items:
            # 상품 가격 다시 조회
            cursor = conn.execute(
                "SELECT price FROM products WHERE product_id = ?", 
                (product_id,)
            )
            unit_price = cursor.fetchone()[0]
            
            # 주문 상세 추가
            conn.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, unit_price))
            
            # 재고 차감
            conn.execute("""
                UPDATE products 
                SET stock_quantity = stock_quantity - ?
                WHERE product_id = ?
            """, (quantity, product_id))
        
        # 트랜잭션 커밋
        conn.commit()
        print(f"주문 {order_id}가 성공적으로 생성되었습니다. 총액: {total_amount:,}원")
        return order_id
        
    except Exception as e:
        # 오류 발생 시 롤백
        conn.rollback()
        print(f"주문 생성 실패: {e}")
        return None
    
    finally:
        conn.close()

# 주문 생성 테스트
test_order_items = [
    (1, 2),  # 갤럭시 스마트폰 2개
    (3, 1),  # 나이키 운동화 1개
]

order_id = create_order_with_transaction(1, test_order_items)
```

갤럭시 스마트폰 2개(2,400,000원)와 나이키 운동화 1개(150,000원)로 총액 2,550,000원짜리 주문이 생깁니다. 실패하는 경우도 직접 확인해 보세요. `[(1, 2), (5, 100)]`처럼 재고(20개)보다 많은 냉장고를 주문하면 "재고가 부족합니다" 메시지가 나오고, 주문 표와 재고에는 아무 변화도 남지 않습니다.

### 컨텍스트 매니저 활용

`try` / `except` / `finally`로 commit, rollback, close를 챙기는 코드는 트랜잭션이 필요한 함수마다 똑같이 반복됩니다. 반복되는 앞뒤 정리는 컨텍스트 매니저로 한 번만 써 두면 되죠. 13장에서 본 `@contextmanager`로 만든 `transaction()`은 `yield` 앞에서 연결을 열고, `with` 블록이 무사히 끝나면 commit, 예외가 나면 rollback 후 예외를 다시 던지고(`raise`), 어느 경우든 마지막에 연결을 닫습니다.

덕분에 `transfer_stock()` 본문에는 정리 코드가 한 줄도 없고 할 일만 남았어요. 재고가 부족해서 `ValueError`를 던지면 그 예외가 `transaction()`의 `except`로 전달되어 rollback이 일어나고, 호출한 쪽에도 예외가 그대로 올라갑니다. 앞의 함수처럼 오류를 `print`로 삼키지 않으니, 호출한 쪽에서 실패를 알고 대처할 수 있다는 것도 장점입니다.

```python
from contextlib import contextmanager

@contextmanager
def transaction():
    """트랜잭션 컨텍스트 매니저"""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def transfer_stock(from_product_id: int, to_product_id: int, quantity: int):
    """재고를 한 상품에서 다른 상품으로 이전합니다."""
    with transaction() as conn:
        # 출발 상품 재고 확인
        cursor = conn.execute(
            "SELECT stock_quantity FROM products WHERE product_id = ?",
            (from_product_id,)
        )
        from_stock = cursor.fetchone()
        
        if not from_stock or from_stock[0] < quantity:
            raise ValueError("재고가 부족합니다.")
        
        # 재고 이전 실행
        conn.execute("""
            UPDATE products 
            SET stock_quantity = stock_quantity - ?
            WHERE product_id = ?
        """, (quantity, from_product_id))
        
        conn.execute("""
            UPDATE products 
            SET stock_quantity = stock_quantity + ?
            WHERE product_id = ?
        """, (quantity, to_product_id))
        
        print(f"{quantity}개 재고가 상품 {from_product_id}에서 {to_product_id}로 이전되었습니다.")

# 재고 이전 테스트 (실제로는 실행하지 않음)
# transfer_stock(1, 2, 5)
```

## 18.5 데이터베이스 유틸리티와 모니터링

### 데이터베이스 정보 조회

남이 만든 데이터베이스 파일을 받았다면, 안에 어떤 표가 있고 각 표에 어떤 열이 있는지부터 알아야 합니다. SQLite는 이런 정보를 `sqlite_master`라는 특별한 표에 스스로 적어 둡니다. 데이터베이스가 자기 자신에 대해 적어 둔 목차인 셈이에요. `type='table'`인 줄만 고르면 표 목록이 나오고, `sqlite_`로 시작하는 SQLite 내부용 표는 `NOT LIKE 'sqlite_%'`로 뺍니다. 표 하나의 열 정보는 `PRAGMA table_info(표이름)`으로 봅니다.

```python
def get_table_info():
    """데이터베이스의 모든 테이블 정보를 조회합니다."""
    with get_connection() as conn:
        # 테이블 목록 조회
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        print("=== 데이터베이스 테이블 목록 ===")
        for table in tables:
            table_name = table[0]
            print(f"\n[{table_name}]")
            
            # 각 테이블의 구조 정보 조회
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                cid, name, data_type, not_null, default, pk = col
                nullable = "NOT NULL" if not_null else "NULL"
                primary = "PRIMARY KEY" if pk else ""
                print(f"  {name} {data_type} {nullable} {primary}")

get_table_info()
```

결과에서 `id INTEGER NULL PRIMARY KEY`처럼 기본 키가 `NULL`로 표시되는 게 이상해 보일 거예요. `PRAGMA table_info`는 `NOT NULL`을 **직접 적은 열만** 표시하기 때문입니다. SQLite에서 `INTEGER PRIMARY KEY` 열은 비워 두면 번호가 자동으로 채워지니, 실제로 빈 값이 저장되지는 않습니다.

이 함수는 표 이름을 `?`가 아니라 f-문자열로 SQL에 끼워 넣었습니다. 방금 `?`가 안전하다고 했는데 왜일까요? `?` 자리에는 **값**만 들어갈 수 있고, 표 이름이나 열 이름 같은 **SQL의 뼈대**는 들어갈 수 없기 때문입니다. 여기서는 표 이름이 데이터베이스가 직접 알려 준 목록에서 왔으니 괜찮지만, 사용자가 입력한 표 이름을 이렇게 끼워 넣으면 18.10절의 공격에 그대로 열립니다. 바로 아래 `export_table_to_csv()`도 같은 방식이니, 이 함수에 표 이름을 넘길 때는 허용된 이름 목록과 대조해서 넘기세요.

### 데이터 백업과 복원

SQLite 데이터베이스는 파일 하나라서 백업도 쉽습니다. `backup_database()`는 17장에서 본 `shutil.copy2()`로 파일을 통째로 복사해요. 다만 다른 프로그램이 그 순간에 데이터베이스에 쓰고 있다면, 쓰다 만 상태가 복사될 수 있습니다. 사용 중인 데이터베이스를 안전하게 복사하려면 `sqlite3` 연결 객체의 `backup()` 메서드를 쓰세요. SQLite가 직접 일관된 상태를 맞춰서 다른 연결로 복사해 줍니다.

`export_table_to_csv()`는 표를 CSV로 내보냅니다. 커서의 `description`에는 결과 열마다 정보가 튜플로 들어 있고, 그 첫 번째 칸이 열 이름이에요. 그래서 `description[0]`을 모으면 CSV 머리줄이 됩니다.

```python
def backup_database(backup_path: str):
    """데이터베이스를 백업합니다."""
    import shutil
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"데이터베이스가 {backup_path}에 백업되었습니다.")
    except Exception as e:
        print(f"백업 실패: {e}")

def export_table_to_csv(table_name: str, csv_path: str):
    """테이블 데이터를 CSV 파일로 내보냅니다."""
    import csv
    
    with get_connection() as conn:
        cursor = conn.execute(f"SELECT * FROM {table_name}")
        
        # 컬럼 이름 가져오기
        columns = [description[0] for description in cursor.description]
        
        # CSV 파일로 저장
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)  # 헤더 쓰기
            writer.writerows(cursor.fetchall())  # 데이터 쓰기
        
        print(f"{table_name} 테이블이 {csv_path}로 내보내졌습니다.")

# 백업 실행 예시 (주석 처리)
# backup_database("korea_company_backup.db")
# export_table_to_csv("employees", "employees_export.csv")
```

## 18.6 ORM (Object-Relational Mapping) 개념

### ORM이란?

지금까지는 파이썬 코드 안에 SQL 문장을 문자열로 적었습니다. 결과는 `('김철수', '개발팀', ...)` 같은 튜플로 돌아왔고요. 그러다 보니 `emp[1]`이 이름인지 부서인지 매번 SQL을 다시 보고 세어야 했죠.

파이썬은 객체로 생각하는 언어이고, 데이터베이스는 표로 생각하는 언어입니다. 둘 사이에 **통역사**를 두면 어떨까요? 우리는 `employee.name`, `employee.save()`처럼 파이썬답게 말하고, 통역사가 그것을 `SELECT`, `INSERT` 같은 SQL로 바꿔 전달하는 거예요. 이 통역사를 **ORM(Object-Relational Mapping, 객체-관계 매핑)** 이라고 합니다. 표 하나가 클래스 하나, 표의 줄 하나가 객체 하나, 열 하나가 속성 하나에 대응해요.

파이썬에서 가장 널리 쓰이는 ORM은 다음 절에서 볼 SQLAlchemy입니다. 그 전에 ORM이 속으로 무슨 일을 하는지 보려고, 아주 작은 ORM을 직접 만들어 봅니다.

### 간단한 ORM 클래스 구현

`BaseModel`은 모든 모델이 함께 쓸 기능을 담은 부모 클래스입니다. 클래스 이름 `Employee`를 소문자로 바꾸고 `s`를 붙여 표 이름 `employees`를 만들고(`get_table_name`), 조회 결과의 열 이름과 값을 `dict(zip(columns, row))`로 짝지은 뒤 `cls(**data)`로 객체를 만듭니다. 열 이름이 곧 데이터클래스의 필드 이름이라서 가능한 일이에요. `Employee`는 이것을 물려받고, 자기 표에 맞는 `save()`와 `delete()`를 더합니다. `save()`는 `id`가 없으면 새 줄을 넣고, 있으면 기존 줄을 고치는 방식으로 하나의 메서드로 두 가지 일을 처리해요.

```python
from dataclasses import dataclass
from typing import Optional, List, Any
import sqlite3

@dataclass
class BaseModel:
    """기본 모델 클래스"""
    id: Optional[int] = None
    
    @classmethod
    def get_table_name(cls) -> str:
        """테이블 이름을 반환합니다."""
        return cls.__name__.lower() + 's'
    
    @classmethod
    def find_all(cls):
        """모든 레코드를 조회합니다."""
        table_name = cls.get_table_name()
        with get_connection() as conn:
            cursor = conn.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # 컬럼 이름 가져오기
            columns = [desc[0] for desc in cursor.description]
            
            # 객체 리스트로 변환
            results = []
            for row in rows:
                data = {col: val for col, val in zip(columns, row) if col in cls.__dataclass_fields__}
                results.append(cls(**data))
            return results
    
    @classmethod
    def find_by_id(cls, record_id: int):
        """ID로 레코드를 조회합니다."""
        table_name = cls.get_table_name()
        with get_connection() as conn:
            cursor = conn.execute(
                f"SELECT * FROM {table_name} WHERE id = ?", 
                (record_id,)
            )
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                data = {col: val for col, val in zip(columns, row) if col in cls.__dataclass_fields__}
                return cls(**data)
            return None

@dataclass
class Employee(BaseModel):
    """직원 모델 클래스"""
    name: str = ""
    department: str = ""
    position: str = ""
    salary: int = 0
    hire_date: str = ""
    email: str = ""
    
    def save(self):
        """직원 정보를 저장합니다."""
        with get_connection() as conn:
            if self.id is None:
                # 새 레코드 삽입
                cursor = conn.execute("""
                    INSERT INTO employees (name, department, position, salary, hire_date, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.name, self.department, self.position, 
                     self.salary, self.hire_date, self.email))
                self.id = cursor.lastrowid
            else:
                # 기존 레코드 업데이트
                conn.execute("""
                    UPDATE employees 
                    SET name=?, department=?, position=?, salary=?, hire_date=?, email=?
                    WHERE id=?
                """, (self.name, self.department, self.position,
                     self.salary, self.hire_date, self.email, self.id))
            conn.commit()
    
    def delete(self):
        """직원 정보를 삭제합니다."""
        if self.id is not None:
            with get_connection() as conn:
                conn.execute("DELETE FROM employees WHERE id = ?", (self.id,))
                conn.commit()
                self.id = None

    @classmethod
    def find_by_department(cls, department: str) -> List['Employee']:
        """부서별 직원을 조회합니다."""
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM employees WHERE department = ?
                ORDER BY salary DESC
            """, (department,))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            results = []
            for row in rows:
                data = {col: val for col, val in zip(columns, row) if col in cls.__dataclass_fields__}
                results.append(cls(**data))
            return results

# ORM 사용 예시
print("\n=== ORM 사용 예시 ===")

# 모든 직원 조회
all_employees = Employee.find_all()
print(f"총 직원 수: {len(all_employees)}")

# 특정 직원 조회
if all_employees:
    first_employee = Employee.find_by_id(all_employees[0].id)
    print(f"첫 번째 직원: {first_employee.name} ({first_employee.department})")

# 부서별 직원 조회
dev_team = Employee.find_by_department("개발팀")
print(f"개발팀 직원 수: {len(dev_team)}")
for emp in dev_team:
    print(f"  {emp.name} - {emp.position}: {emp.salary:,}원")
```

이제 결과를 `emp[1]`이 아니라 `emp.name`, `emp.position`으로 꺼냅니다. 훨씬 읽기 쉽죠.

조회 결과를 객체로 바꾸는 줄이 `dict(zip(columns, row))`가 아니라 `if col in cls.__dataclass_fields__`로 열을 거르는 모양인 데에도 이유가 있습니다. `cls(**data)`는 넘긴 키가 모두 데이터클래스의 필드여야 해요. 18.8절에서 `employees` 표에 `birth_date` 열을 추가하는데, 열을 거르지 않으면 그 뒤에 이 예제를 다시 실행할 때 `TypeError: Employee.__init__() got an unexpected keyword argument 'birth_date'`가 납니다. 표는 바뀌었는데 클래스는 그대로이기 때문이에요. 그래서 클래스가 아는 필드(`__dataclass_fields__`에 이름이 있는 것)만 골라 넘기도록 했습니다. 대신 새 열 `birth_date`의 값은 객체에 담기지 않으니, 그 값까지 쓰려면 클래스에도 필드를 더해야 합니다. 표와 코드가 함께 바뀌어야 한다는 이 문제는 18.8절의 주제이기도 합니다. 관계(고객의 주문들), 여러 데이터베이스 지원, 이런 열 변화까지 제대로 다루려면 직접 만드는 것보다 검증된 라이브러리를 쓰는 편이 낫습니다.

## 18.7 SQLAlchemy 기초

### SQLAlchemy 설치 및 설정

SQLAlchemy는 파이썬에서 가장 널리 쓰이는 데이터베이스 라이브러리입니다. 표준 라이브러리가 아니므로 코드 첫 줄 주석처럼 프로젝트 폴더에서 `uv add sqlalchemy`로 먼저 설치합니다.

설정은 세 가지로 이루어집니다.

- **엔진(engine)**: 데이터베이스와 연결하는 출입문입니다. `"sqlite:///korea_shop.db"` 같은 주소로 어떤 데이터베이스인지 알려 줘요. 주소 앞부분만 `postgresql://...`로 바꾸면 같은 코드로 PostgreSQL에 연결할 수 있습니다.
- **세션(session)**: 장바구니입니다. 객체를 담고(`add`), 고치고, 다 됐으면 한 번에 계산(`commit`)해요. `sessionmaker`는 이 장바구니를 찍어 내는 틀입니다.
- **모델(model)**: `Base`를 상속한 클래스가 표 하나입니다. `Column`으로 열을, `ForeignKey`로 외래 키를 선언해요.

새로 등장하는 `relationship()`이 ORM의 진짜 힘입니다. `Customer.orders`와 `Order.customer`를 짝지어 두면, 주문 객체에서 `order.customer.name`처럼 **점 하나로 다른 표의 정보를 따라갈 수 있어요**. 뒤에서 SQLAlchemy가 필요한 JOIN이나 조회를 대신 만들어 줍니다. `back_populates`는 두 방향의 관계가 서로 짝이라는 표시이고, `Order.order_items`의 `cascade="all, delete-orphan"`은 주문을 지우면 딸린 주문 상세도 함께 지우라는 뜻입니다.

이 예제는 `korea_company.db`가 아닌 새 파일 `korea_shop.db`를 씁니다. 앞에서 sqlite3로 만든 표와 이름이 겹치지만, 파일이 다르니 서로 영향을 주지 않아요.

```python
# 터미널에서 설치:
# uv add sqlalchemy

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone


def utc_now():
    """시간대 정보가 붙은 현재 UTC 시각을 돌려줍니다."""
    return datetime.now(timezone.utc)

# SQLAlchemy 설정
DATABASE_URL = "sqlite:///korea_shop.db"
engine = create_engine(DATABASE_URL, echo=False)  # echo=True로 설정하면 SQL 로그 출력

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 모델 정의
class Customer(Base):
    """고객 모델"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(DateTime, default=utc_now)
    
    # 관계 정의
    orders = relationship("Order", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(name='{self.name}', email='{self.email}')>"

class Category(Base):
    """카테고리 모델"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 관계 정의
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"

class Product(Base):
    """상품 모델"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(Text)
    stock_quantity = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=utc_now)
    
    # 관계 정의
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product(name='{self.name}', price={self.price})>"

class Order(Base):
    """주문 모델"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_date = Column(DateTime, default=utc_now)
    status = Column(String(50), default="pending")
    total_amount = Column(Integer, nullable=False)
    
    # 관계 정의
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, total_amount={self.total_amount})>"

class OrderItem(Base):
    """주문 상세 모델"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    
    # 관계 정의
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    
    def __repr__(self):
        return f"<OrderItem(product_id={self.product_id}, quantity={self.quantity})>"

# 테이블 생성
Base.metadata.create_all(bind=engine)
print("SQLAlchemy 테이블이 생성되었습니다.")
```

마지막 줄 `Base.metadata.create_all()`은 `Base`를 상속한 모든 모델을 보고 `CREATE TABLE` 문장을 만들어 실행합니다. SQL을 한 줄도 쓰지 않았는데 표 다섯 개가 생겼죠. 이미 있는 표는 건너뜁니다.

오래된 자료에서는 다르게 쓴 두 곳을 자주 만납니다. 하나는 `from sqlalchemy.ext.declarative import declarative_base`인데, SQLAlchemy 2.0부터 `declarative_base()`는 `sqlalchemy.orm`으로 자리를 옮겨서 옛 위치로 불러오면 `MovedIn20Warning`이 납니다. 다른 하나는 기본값으로 쓴 `datetime.utcnow`인데, 파이썬 3.12부터 쓰지 말라는 `DeprecationWarning`이 나와요. 시간대 정보가 없는 시각을 돌려주기 때문입니다. 그래서 예제는 시간대 정보가 있는 `datetime.now(timezone.utc)`를 돌려주는 `utc_now()` 함수를 만들어 `default=utc_now`로 넘겼습니다. 괄호 없이 함수 자체를 넘긴다는 점에 주의하세요. `default=utc_now()`라고 쓰면 모델을 정의하는 순간의 시각 하나가 모든 줄에 똑같이 들어갑니다.

### SQLAlchemy CRUD 작업

**CRUD**는 데이터를 다루는 네 가지 기본 동작, Create(만들기), Read(읽기), Update(고치기), Delete(지우기)의 머리글자입니다. SQLAlchemy에서는 이것이 이렇게 바뀝니다.

| 하고 싶은 일 | sqlite3 + SQL | SQLAlchemy |
|---|---|---|
| 만들기 | `INSERT INTO ...` | `session.add(객체)` |
| 읽기 | `SELECT ... WHERE ...` | `session.query(클래스).filter(...)` |
| 고치기 | `UPDATE ... SET ...` | `객체.속성 = 새값` |
| 지우기 | `DELETE FROM ...` | `session.delete(객체)` |
| 확정 | `conn.commit()` | `session.commit()` |

아래 함수는 카테고리, 고객, 상품을 차례로 넣습니다. 넣기 전에 `filter(...).first()`로 같은 이름이나 이메일이 이미 있는지 확인하니, 여러 번 실행해도 중복되지 않아요. 18.2절의 `INSERT OR IGNORE`와 달리 `UNIQUE` 규칙에 기대지 않고 코드로 직접 확인한 거죠. 상품을 넣을 때는 카테고리를 다시 조회해서 `electronics.id`처럼 실제 번호를 씁니다.

맨 위의 `get_db_session()`은 새 세션(장바구니) 하나를 만들어 돌려줄 뿐이고, 세션을 닫는 일은 각 함수의 `finally: session.close()`가 맡아요.

```python
def get_db_session():
    """데이터베이스 세션을 반환합니다. 닫는 일은 호출한 쪽이 맡습니다."""
    return SessionLocal()

def add_sample_data_sqlalchemy():
    """SQLAlchemy를 사용해 샘플 데이터를 추가합니다."""
    session = get_db_session()
    
    try:
        # 카테고리 추가
        categories = [
            Category(name="전자제품", description="스마트폰, 노트북 등"),
            Category(name="의류", description="남성복, 여성복"),
            Category(name="도서", description="소설, 전문서적"),
        ]
        
        for category in categories:
            # 중복 체크
            existing = session.query(Category).filter(Category.name == category.name).first()
            if not existing:
                session.add(category)
        
        session.commit()
        
        # 고객 추가
        customers = [
            Customer(name="김고객", email="kim@example.com", phone="010-1234-5678", address="서울시 강남구"),
            Customer(name="이구매자", email="lee@example.com", phone="010-2345-6789", address="부산시 해운대구"),
            Customer(name="박쇼핑", email="park@example.com", phone="010-3456-7890", address="대구시 중구"),
        ]
        
        for customer in customers:
            existing = session.query(Customer).filter(Customer.email == customer.email).first()
            if not existing:
                session.add(customer)
        
        session.commit()
        
        # 상품 추가 (카테고리 ID 조회 후)
        electronics = session.query(Category).filter(Category.name == "전자제품").first()
        clothing = session.query(Category).filter(Category.name == "의류").first()
        books = session.query(Category).filter(Category.name == "도서").first()
        
        products = [
            Product(name="최신 스마트폰", price=1200000, description="5G 지원", 
                   stock_quantity=50, category_id=electronics.id),
            Product(name="블루투스 이어폰", price=200000, description="노이즈 캔슬링", 
                   stock_quantity=100, category_id=electronics.id),
            Product(name="캐주얼 셔츠", price=80000, description="100% 면", 
                   stock_quantity=200, category_id=clothing.id),
            Product(name="Python 완벽 가이드", price=35000, description="개발자 필독서", 
                   stock_quantity=150, category_id=books.id),
        ]
        
        for product in products:
            existing = session.query(Product).filter(Product.name == product.name).first()
            if not existing:
                session.add(product)
        
        session.commit()
        print("SQLAlchemy 샘플 데이터가 추가되었습니다.")
        
    except Exception as e:
        session.rollback()
        print(f"데이터 추가 오류: {e}")
    finally:
        session.close()

# 샘플 데이터 추가
add_sample_data_sqlalchemy()
```

### SQLAlchemy 쿼리 작업

이번에는 꺼내 봅니다. `session.query(Product)`는 "상품을 찾아 줘"이고, 뒤에 `.join()`, `.filter()`, `.order_by()`를 이어 붙여 조건을 더합니다. 마지막에 `.all()`(모두 리스트로), `.first()`(첫 하나) 같은 것을 불러야 실제로 SQL이 실행돼요. 조건을 `Product.price >= 500000`처럼 파이썬 비교식으로 쓰는 것이 신기하죠? 이 식은 `True`/`False`가 되는 게 아니라, SQLAlchemy가 SQL의 `WHERE` 조건으로 번역할 수 있는 특별한 객체가 됩니다.

5번의 `func.count()`, `func.avg()`는 SQL의 집계 함수를 그대로 부르는 방법이고, `.outerjoin()`은 18.3절의 `LEFT JOIN`과 같습니다.

```python
def demo_sqlalchemy_queries():
    """SQLAlchemy 쿼리 예제를 실행합니다."""
    session = get_db_session()
    
    try:
        print("\n=== SQLAlchemy 쿼리 예제 ===")
        
        # 1. 모든 상품 조회 (카테고리 포함)
        products = session.query(Product).join(Category).all()
        print(f"\n1. 전체 상품 수: {len(products)}")
        for product in products[:3]:  # 처음 3개만 출력
            print(f"   {product.name} ({product.category.name}): {product.price:,}원")
        
        # 2. 특정 카테고리의 상품 조회
        electronics = session.query(Product).join(Category).filter(
            Category.name == "전자제품"
        ).all()
        print(f"\n2. 전자제품 카테고리 상품 수: {len(electronics)}")
        for product in electronics:
            print(f"   {product.name}: {product.price:,}원 (재고: {product.stock_quantity})")
        
        # 3. 가격 범위로 상품 검색
        expensive_products = session.query(Product).filter(
            Product.price >= 500000
        ).order_by(Product.price.desc()).all()
        print(f"\n3. 50만원 이상 상품: {len(expensive_products)}개")
        
        # 4. 고객별 정보 조회
        customers = session.query(Customer).all()
        print(f"\n4. 등록된 고객 수: {len(customers)}")
        for customer in customers:
            print(f"   {customer.name} ({customer.email}) - {customer.address}")
        
        # 5. 카테고리별 상품 통계
        from sqlalchemy import func
        category_stats = session.query(
            Category.name,
            func.count(Product.id).label('product_count'),
            func.avg(Product.price).label('avg_price'),
            func.sum(Product.stock_quantity).label('total_stock')
        ).outerjoin(Product).group_by(Category.id, Category.name).all()
        
        print(f"\n5. 카테고리별 통계:")
        for cat_name, count, avg_price, total_stock in category_stats:
            avg_price = int(avg_price) if avg_price else 0
            total_stock = total_stock if total_stock else 0
            print(f"   {cat_name}: {count}개 상품, 평균가격 {avg_price:,}원, 총재고 {total_stock}개")
        
    except Exception as e:
        print(f"쿼리 실행 오류: {e}")
    finally:
        session.close()

# 쿼리 예제 실행
demo_sqlalchemy_queries()
```

1번 결과의 `product.category.name`을 다시 보세요. 상품 객체에서 점 하나로 카테고리 이름까지 따라갔습니다. 18.3절에서 JOIN을 직접 쓰던 것과 비교하면 `relationship()`이 무슨 일을 해 주는지 실감이 날 거예요. 실행하면 상품 4개, 전자제품 2개, 50만 원 이상 1개, 고객 3명이 나오고, 5번 통계에서 전자제품의 평균 가격은 700,000원입니다.

### SQLAlchemy 주문 처리

18.4절의 주문 생성을 SQLAlchemy로 다시 써 봅니다. 눈여겨볼 곳은 두 군데예요.

하나는 `session.flush()`입니다. 주문 상세를 만들려면 주문 번호가 필요한데, 번호는 데이터베이스에 넣어야 생기죠. `flush()`는 지금까지 장바구니에 담은 것을 데이터베이스에 **보내기만 하고 확정은 하지 않습니다**. 그래서 번호는 받아 오면서도, 뒤에서 오류가 나면 `rollback()`으로 모두 되돌릴 수 있어요. `commit()`이 "계산 완료"라면 `flush()`는 "계산대에 올려놓기"쯤 됩니다.

다른 하나는 재고 차감이 `product.stock_quantity -= quantity`, 그냥 속성을 고치는 한 줄이라는 점입니다. `UPDATE` 문장은 어디에도 없어요. 세션이 바뀐 객체를 기억하고 있다가 `commit()` 때 알아서 `UPDATE`를 보냅니다.

```python
def create_order_sqlalchemy(customer_email: str, items: list):
    """SQLAlchemy를 사용해 주문을 생성합니다."""
    session = get_db_session()
    
    try:
        # 고객 조회
        customer = session.query(Customer).filter(Customer.email == customer_email).first()
        if not customer:
            raise ValueError(f"고객을 찾을 수 없습니다: {customer_email}")
        
        # 새 주문 생성
        new_order = Order(customer_id=customer.id, total_amount=0)
        session.add(new_order)
        session.flush()  # ID를 얻기 위해 flush
        
        total_amount = 0
        
        # 주문 상세 추가
        for product_id, quantity in items:
            # 상품 조회 및 재고 확인
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError(f"상품을 찾을 수 없습니다: ID {product_id}")
            
            if product.stock_quantity < quantity:
                raise ValueError(f"재고 부족: {product.name} (요청: {quantity}, 재고: {product.stock_quantity})")
            
            # 주문 상세 항목 생성
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price
            )
            session.add(order_item)
            
            # 재고 차감
            product.stock_quantity -= quantity
            
            # 총액 계산
            total_amount += product.price * quantity
        
        # 주문 총액 업데이트
        new_order.total_amount = total_amount
        
        # 트랜잭션 커밋
        session.commit()
        
        print(f"주문이 성공적으로 생성되었습니다.")
        print(f"주문 ID: {new_order.id}")
        print(f"고객: {customer.name}")
        print(f"총액: {total_amount:,}원")
        
        return new_order.id
        
    except Exception as e:
        session.rollback()
        print(f"주문 생성 실패: {e}")
        return None
    finally:
        session.close()

def get_order_details(order_id: int):
    """주문 상세 정보를 조회합니다."""
    session = get_db_session()
    
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            print(f"주문을 찾을 수 없습니다: ID {order_id}")
            return
        
        print(f"\n=== 주문 상세 정보 (ID: {order.id}) ===")
        print(f"고객: {order.customer.name}")
        print(f"이메일: {order.customer.email}")
        print(f"주문일시: {order.order_date}")
        print(f"상태: {order.status}")
        print(f"총액: {order.total_amount:,}원")
        print("\n주문 상품:")
        
        for item in order.order_items:
            print(f"  - {item.product.name}: {item.quantity}개 × {item.unit_price:,}원 = {item.subtotal:,}원")
        
    except Exception as e:
        print(f"주문 조회 오류: {e}")
    finally:
        session.close()

# 주문 생성 테스트
test_order_items = [
    (1, 1),  # 스마트폰 1개
    (3, 2),  # 셔츠 2개
]

order_id = create_order_sqlalchemy("kim@example.com", test_order_items)
if order_id:
    get_order_details(order_id)
```

스마트폰 1개(1,200,000원)와 셔츠 2개(160,000원)로 총액 1,360,000원짜리 주문이 만들어지고, `get_order_details()`가 `order.customer.name`, `item.product.name`처럼 관계를 따라가며 영수증을 출력합니다. 주문일시가 우리 시각보다 9시간 이르게 찍히는 것도 보일 거예요. 모델에서 `default=utc_now`로 **세계 표준시(UTC)** 를 저장했기 때문입니다. SQLite에는 시간대를 저장할 자리가 없어서 `+00:00` 꼬리표 없이 시각만 남습니다. 서버에는 UTC로 저장하고 화면에 보여 줄 때 한국 시간으로 바꾸는 것이 흔한 방식이에요. 17장의 `zoneinfo` 예제가 그 변환 방법입니다.

## 18.8 데이터베이스 마이그레이션

### 스키마 변경 관리

서비스를 운영하다 보면 표의 모양, 즉 **스키마(schema)** 를 바꿔야 할 때가 꼭 옵니다. 직원 생년월일을 저장해 달라는 요청이 오면 `employees` 표에 열을 하나 더해야 하죠. 내 컴퓨터에서는 `ALTER TABLE` 한 줄이면 끝나지만, 같은 데이터베이스가 동료의 컴퓨터, 테스트 서버, 실제 서비스 서버에 하나씩 있다면 이야기가 달라집니다. 어느 데이터베이스에 어디까지 적용했는지 기억에 의존하면 반드시 하나쯤 빠뜨려요.

집 리모델링 공사 일지를 떠올려 보세요. "1차: 거실 콘센트 추가, 2차: 욕실 타일 교체"처럼 공사마다 번호를 붙여 기록해 두면, 어느 집이 몇 차 공사까지 끝났는지 일지만 보고 알 수 있습니다. 데이터베이스도 똑같이 합니다. 스키마 변경 하나하나에 **버전 번호**를 붙여 기록하고, 데이터베이스 안에 "나는 몇 번까지 적용됐다"를 적어 두는 거예요. 이것을 **마이그레이션(migration)** 이라고 합니다.

아래 코드는 이 생각을 직접 구현한 것입니다. `schema_migrations` 표가 공사 일지예요. `execute_migration()`은 지금 버전보다 큰 번호의 변경만 실행하고, 실행한 뒤 일지에 기록합니다. 그래서 이 코드를 몇 번을 다시 실행해도 같은 변경이 두 번 적용되지 않아요. 변경과 기록을 한 트랜잭션으로 묶었으니, 중간에 실패하면 변경도 기록도 남지 않습니다.

```python
def create_migration_table():
    """마이그레이션 이력을 저장할 테이블을 생성합니다."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def get_current_version():
    """현재 스키마 버전을 조회합니다."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT MAX(version) FROM schema_migrations
        """)
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0

def execute_migration(version: int, description: str, sql_commands: list):
    """마이그레이션을 실행합니다."""
    current_version = get_current_version()
    
    if version <= current_version:
        print(f"마이그레이션 v{version}은 이미 실행되었습니다.")
        return
    
    with get_connection() as conn:
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # SQL 명령어들 실행
            for sql in sql_commands:
                conn.execute(sql)
            
            # 마이그레이션 이력 기록
            conn.execute("""
                INSERT INTO schema_migrations (version, description)
                VALUES (?, ?)
            """, (version, description))
            
            conn.commit()
            print(f"마이그레이션 v{version} 완료: {description}")
            
        except Exception as e:
            conn.rollback()
            print(f"마이그레이션 v{version} 실패: {e}")

# 마이그레이션 테이블 생성
create_migration_table()

# 예시 마이그레이션 1: 직원 테이블에 생년월일 컬럼 추가
migration_v1 = [
    "ALTER TABLE employees ADD COLUMN birth_date DATE",
    "ALTER TABLE employees ADD COLUMN department_code TEXT"
]

execute_migration(1, "직원 테이블에 생년월일과 부서코드 컬럼 추가", migration_v1)

# 예시 마이그레이션 2: 상품 평점 테이블 생성
migration_v2 = [
    """
    CREATE TABLE IF NOT EXISTS product_reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    """,
    "CREATE INDEX idx_product_reviews_product_id ON product_reviews (product_id)",
    "CREATE INDEX idx_product_reviews_rating ON product_reviews (rating)"
]

execute_migration(2, "상품 리뷰 시스템 추가", migration_v2)

print(f"현재 스키마 버전: {get_current_version()}")
```

처음 실행하면 v1, v2가 차례로 적용되고 "현재 스키마 버전: 2"가 나옵니다. 다시 실행하면 두 변경 모두 "이미 실행되었습니다"로 건너뛰어요.

이 손수 만든 방식은 원리를 보여 주기에는 좋지만 빈 곳이 많습니다. 한번 적용한 변경을 되돌리는 방법(되돌리기)이 없고, 18.6절에서 본 것처럼 표가 바뀌어도 파이썬 모델 클래스는 그대로라서 둘이 쉽게 어긋납니다. 18.6절의 미니 ORM은 모르는 열을 걸러 내는 것으로 겨우 버티고 있을 뿐이에요. 실제 프로젝트에서는 이 일을 전문으로 하는 도구를 씁니다.

### Alembic으로 마이그레이션 관리하기

**Alembic**은 SQLAlchemy를 만든 사람이 함께 만든 마이그레이션 도구입니다. 하는 일은 앞의 코드와 같아요. 변경마다 버전을 붙이고, 데이터베이스에 현재 버전을 적어 두고, 아직 적용하지 않은 변경만 실행합니다. 다른 점은 변경 하나하나가 **파이썬 파일**이고, 파일마다 적용하는 방법(`upgrade`)과 **되돌리는 방법(`downgrade`)** 을 함께 적는다는 것이에요. 이 파일들을 git으로 함께 관리하면, 동료는 코드를 받은 뒤 명령 한 줄로 자기 데이터베이스를 같은 버전으로 맞출 수 있습니다.

설치하고, 프로젝트 폴더에서 마이그레이션 작업 공간을 만듭니다.

```bash
uv add alembic
uv run alembic init migrations
```

`init`은 설정 파일 `alembic.ini`와 `migrations` 폴더를 만듭니다. 폴더 안의 `env.py`는 Alembic이 데이터베이스에 연결하는 방법을, `versions` 폴더는 앞으로 만들 변경 파일들을 담아요. 처음 만든 직후에는 "`alembic.ini`의 연결 설정을 고친 다음 진행하라"는 안내가 나옵니다. `alembic.ini`를 열어 `sqlalchemy.url` 줄을 연결할 데이터베이스 주소로 바꿉니다. SQLAlchemy 엔진에 쓰던 그 주소예요.

```text
sqlalchemy.url = sqlite:///shop.db
```

이제 첫 번째 변경을 만듭니다. `-m` 뒤에는 공사 일지에 적을 설명을 씁니다.

```bash
uv run alembic revision -m "create employees table"
```

```text
Generating migrations/versions/ed1201dba05f_create_employees_table.py ...  done
```

파일 이름 앞의 `ed1201dba05f`가 이 변경의 버전 번호(revision ID)입니다. 1, 2, 3 같은 순번이 아니라 무작위로 만든 값이라 여러분이 실행하면 다른 값이 나와요. 순서는 파일 안의 `down_revision`이 "내 바로 앞 버전은 무엇인가"를 가리키는 방식으로 이어집니다. 첫 번째 파일은 앞 버전이 없으니 `None`이에요. 만들어진 파일에는 빈 `upgrade()`와 `downgrade()`가 들어 있고, 그 안을 채우는 것이 우리 몫입니다.

```python
def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("department", sa.String(50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("employees")
```

`op`는 Alembic이 제공하는 공사 도구 상자입니다. `op.create_table()`로 표를 만들고, 되돌릴 때는 `op.drop_table()`로 지워요. 같은 방법으로 두 번째 변경 `alembic revision -m "add birth_date to employees"`를 만들고, 앞의 v1과 같은 일을 적습니다. 이번 파일의 `down_revision`에는 첫 번째 파일의 번호가 자동으로 들어갑니다.

```python
def upgrade() -> None:
    op.add_column("employees", sa.Column("birth_date", sa.Date))


def downgrade() -> None:
    op.drop_column("employees", "birth_date")
```

이제 적용합니다. `head`는 "가장 최신 버전까지"라는 뜻이에요.

```bash
uv run alembic upgrade head
```

```text
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> ed1201dba05f, create employees table
INFO  [alembic.runtime.migration] Running upgrade ed1201dba05f -> aa8f2edc3c08, add birth_date to employees
```

두 변경이 순서대로 적용됐습니다. 지금 데이터베이스가 몇 번 버전인지는 `alembic current`로, 변경의 순서는 `alembic history`로 봅니다.

```bash
uv run alembic current
uv run alembic history
```

```text
aa8f2edc3c08 (head)
ed1201dba05f -> aa8f2edc3c08 (head), add birth_date to employees
<base> -> ed1201dba05f, create employees table
```

(`current`를 실행하면 위 결과 앞에 `upgrade` 때와 같은 `INFO` 두 줄이 먼저 나옵니다.) Alembic은 이 버전 번호를 데이터베이스 안의 `alembic_version` 표에 적어 둡니다. 앞에서 직접 만든 `schema_migrations` 표와 같은 역할이죠.

잘못 적용했다면 되돌릴 수 있습니다. `downgrade -1`은 한 단계 전으로 돌아가라는 뜻이에요.

```bash
uv run alembic downgrade -1
```

```text
INFO  [alembic.runtime.migration] Running downgrade aa8f2edc3c08 -> ed1201dba05f, add birth_date to employees
```

(이 앞에도 `INFO` 두 줄이 먼저 나옵니다.) 두 번째 파일의 `downgrade()`가 실행되어 `birth_date` 열이 사라지고, 현재 버전은 다시 `ed1201dba05f`가 됩니다. 되돌리기를 직접 적어 두는 것이 귀찮아 보여도, 배포한 변경에 문제가 생겼을 때 이것이 안전한 퇴로가 됩니다.

> **Q. 모델 클래스를 고치면 마이그레이션 파일을 자동으로 만들어 주지는 않나요?**
> 만들어 줍니다. `migrations/env.py`의 `target_metadata`에 18.7절의 `Base.metadata`를 연결해 두면, `alembic revision --autogenerate -m "설명"`이 모델 클래스와 실제 데이터베이스를 비교해서 차이를 `upgrade()`/`downgrade()`로 적은 초안을 만들어 줍니다. 다만 어디까지나 **초안**입니다. 열 이름을 바꾼 것을 "열 하나 삭제, 열 하나 추가"로 읽는 것처럼 의도를 오해할 수 있으니, 만들어진 파일은 반드시 읽어 보고 고친 다음 적용하세요.

## 18.9 성능 최적화

### 인덱스 활용

두꺼운 전공 책에서 "트랜잭션"이라는 말이 나오는 쪽을 찾으려면 어떻게 하나요? 첫 쪽부터 넘기지 않고, 책 맨 뒤의 **찾아보기(색인)** 를 펼치죠. 가나다순으로 정리된 색인에서 단어를 찾으면 쪽 번호가 바로 나옵니다.

데이터베이스의 **인덱스(index)** 가 바로 이 색인입니다. 인덱스가 없으면 `WHERE department = '개발팀'`을 처리할 때 표를 첫 줄부터 끝 줄까지 모두 훑어야 해요(전체 스캔). 부서 열에 인덱스를 만들어 두면 정렬된 색인에서 '개발팀'을 바로 찾아 해당 줄로 건너뜁니다. 대신 공짜는 아닙니다. 책에 색인이 있으면 쪽수가 늘듯 인덱스도 저장 공간을 차지하고, 줄을 넣거나 고칠 때마다 색인도 함께 고쳐야 하니 쓰기가 조금 느려져요. 그래서 **자주 검색하거나 정렬하는 열**에만 만듭니다.

아래 코드는 검색 조건(`department`, `price`), 표를 잇는 외래 키(`category_id`, `customer_id`), 정렬 기준(`salary`, `order_date`)에 인덱스를 만듭니다. `UNIQUE INDEX`는 색인이면서 동시에 "겹치면 안 된다"는 규칙 역할도 해요. 출력에는 `인덱스 생성: idx_employees_department`처럼 인덱스 이름이 찍힙니다. SQL 문장을 `" ON "`에서 잘라 앞부분의 마지막 낱말을 꺼낸 거예요. 문장의 마지막 낱말을 꺼내면 `(department)`처럼 괄호 속 열 이름이 나와 버립니다.

```python
def create_performance_indexes():
    """성능 향상을 위한 인덱스를 생성합니다."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_employees_department ON employees (department)",
        "CREATE INDEX IF NOT EXISTS idx_employees_salary ON employees (salary)",
        "CREATE INDEX IF NOT EXISTS idx_products_price ON products (price)",
        "CREATE INDEX IF NOT EXISTS idx_products_category ON products (category_id)",
        "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_orders_date ON orders (order_date)",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_email ON customers (email)",
    ]
    
    with get_connection() as conn:
        for index_sql in indexes:
            try:
                conn.execute(index_sql)
                index_name = index_sql.split(" ON ")[0].split()[-1]
                print(f"인덱스 생성: {index_name}")
            except Exception as e:
                print(f"인덱스 생성 실패: {e}")
        conn.commit()

create_performance_indexes()
```

인덱스를 만들었다고 데이터베이스가 꼭 그것을 쓰는 것은 아닙니다. 실제로 쓰는지는 SQL 앞에 `EXPLAIN QUERY PLAN`을 붙여서 "이 문장을 어떻게 처리할 계획이야?"라고 물어보면 알 수 있어요.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE employees (name TEXT, department TEXT)")
sql = "SELECT * FROM employees WHERE department = ?"

print(conn.execute("EXPLAIN QUERY PLAN " + sql, ("개발팀",)).fetchall())
conn.execute("CREATE INDEX idx_employees_department ON employees (department)")
print(conn.execute("EXPLAIN QUERY PLAN " + sql, ("개발팀",)).fetchall())
```

```text
[(2, 0, 216, 'SCAN employees')]
[(3, 0, 62, 'SEARCH employees USING INDEX idx_employees_department (department=?)')]
```

`":memory:"`는 파일 대신 메모리에 임시 데이터베이스를 만드는 특별한 이름이라 실험할 때 편합니다. 인덱스를 만들기 전에는 `SCAN employees`, 표 전체를 훑겠다는 계획이었는데, 만든 뒤에는 `SEARCH ... USING INDEX`, 색인으로 바로 찾겠다는 계획으로 바뀌었어요. 튜플 앞의 숫자들은 SQLite 내부의 계획 번호라서 신경 쓰지 않아도 되고, 마지막 문자열만 읽으면 됩니다.

### 쿼리 성능 분석

이번에는 시간을 직접 재 봅니다. `time_query()`는 SQL 하나를 실행하는 데 걸린 시간을 밀리초(ms)로 출력해요. 시간을 잴 때는 `time.time()`보다 짧은 구간을 정밀하게 재도록 만든 `time.perf_counter()`가 더 알맞습니다.

측정하기 전에 `create_test_data()`가 테스트 직원 1000명을 넣습니다. 이메일이 `UNIQUE`라서 `INSERT OR IGNORE`가 이미 있는 직원은 건너뛰니, 여러 번 실행해도 1000명이 더 쌓이지는 않아요. 직원이 1000명 남짓이면 부서별 검색은 200행 남짓을 돌려주는데, 그래도 모든 쿼리가 1ms 안팎에 끝납니다. 이 정도 크기에서는 인덱스가 있든 없든 체감할 차이가 나지 않아요. 인덱스의 효과는 표가 수십만, 수백만 줄로 커질 때 드러납니다. 각 쿼리가 실제로 인덱스를 쓰는지는 시간보다 앞에서 본 `EXPLAIN QUERY PLAN`으로 확인하는 편이 정확합니다. 첫 번째 쿼리는 바로 앞에서 만든 `department` 인덱스를 씁니다.

이 1000명은 데이터베이스 파일에 그대로 남는다는 점도 기억하세요. 이 장의 예제를 처음부터 다시 실행하면 18.1절의 직원 목록에 테스트 직원까지 함께 나옵니다. 처음 상태로 돌아가고 싶다면 `korea_company.db`를 지우고 시작하면 됩니다.

```python
def analyze_query_performance():
    """쿼리 성능을 분석합니다."""
    import time
    
    # 성능 테스트용 대량 데이터 생성 (실제 환경에서만 실행)
    def create_test_data():
        with get_connection() as conn:
            # 대량의 테스트 직원 데이터 생성
            test_employees = []
            departments = ["개발팀", "마케팅팀", "영업팀", "인사팀", "재무팀"]
            
            for i in range(1000):
                name = f"테스트직원{i:04d}"
                dept = departments[i % len(departments)]
                salary = 3000000 + (i * 1000)
                email = f"test{i:04d}@company.co.kr"
                test_employees.append((name, dept, "직원", salary, "2023-01-01", email))
            
            conn.executemany("""
                INSERT OR IGNORE INTO employees 
                (name, department, position, salary, hire_date, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, test_employees)
            conn.commit()
    
    # 성능 테스트 함수
    def time_query(query_name, sql, params=None):
        with get_connection() as conn:
            start_time = time.time()
            
            if params:
                cursor = conn.execute(sql, params)
            else:
                cursor = conn.execute(sql)
            
            results = cursor.fetchall()
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000  # 밀리초
            print(f"{query_name}: {execution_time:.2f}ms (결과 {len(results)}행)")
    
    create_test_data()  # 테스트 직원 1000명 추가 (이메일이 같으면 건너뜀)
    print("\n=== 쿼리 성능 분석 ===")

    # department 인덱스를 사용한 검색
    time_query(
        "부서별 검색 (인덱스 사용)",
        "SELECT * FROM employees WHERE department = ?",
        ("개발팀",)
    )
    
    # 인덱스를 사용한 검색
    time_query(
        "월급 범위 검색",
        "SELECT * FROM employees WHERE salary BETWEEN ? AND ?",
        (5000000, 7000000)
    )
    
    # 정렬 쿼리
    time_query(
        "월급순 정렬",
        "SELECT * FROM employees ORDER BY salary DESC LIMIT 10"
    )
    
    # 집계 쿼리
    time_query(
        "부서별 평균 월급",
        """
        SELECT department, AVG(salary) as avg_salary, COUNT(*) as emp_count
        FROM employees 
        GROUP BY department 
        ORDER BY avg_salary DESC
        """
    )

# 성능 분석 실행
analyze_query_performance()
```

### 연결 풀링과 최적화

데이터베이스 연결을 여는 데는 생각보다 품이 듭니다. 특히 네트워크 너머의 데이터베이스 서버라면 접속하고, 로그인하고, 준비하는 데 시간이 걸려요. 요청이 올 때마다 연결을 새로 열고 닫는 것은, 손님이 올 때마다 직원을 새로 채용했다가 손님이 가면 내보내는 것과 같습니다.

**연결 풀(connection pool)** 은 직원 대기실입니다. 미리 연결 몇 개를 열어 대기실(`Queue`)에 넣어 두고, 필요한 코드가 하나 꺼내 쓴 다음 **닫지 않고 돌려놓습니다**. 아래 `get_connection()`이 `finally`에서 `self.pool.put(conn)`으로 연결을 반납하는 부분이 그것이에요. 대기실이 비어 있으면 `timeout=10`초 동안 누가 반납하기를 기다리고, 그래도 없으면 예외를 냅니다. 여러 스레드가 같은 연결을 나눠 쓸 수 있도록 `check_same_thread=False`를 주었는데, sqlite3는 원래 연결을 만든 스레드에서만 쓰도록 막아 두기 때문입니다. 대신 한 연결을 두 스레드가 **동시에** 쓰지 않도록 하는 책임은 우리에게 넘어와요. 풀에서 꺼낸 연결은 반납하기 전까지 한 사람만 쓰니, 이 구조가 그 약속을 지켜 줍니다.

연결을 만들 때 실행하는 `PRAGMA`들은 SQLite의 동작 방식을 바꾸는 설정입니다. `journal_mode=WAL`은 쓰는 동안에도 다른 연결이 읽을 수 있게 해 주는 방식이라 여러 스레드가 함께 쓸 때 유리하고, `synchronous=NORMAL`은 디스크 기록 확인을 조금 줄여 속도를 얻는 대신 정전 같은 사고 때의 안전성을 약간 양보합니다.

실제로는 이런 풀을 직접 만들 일이 드뭅니다. 18.7절의 SQLAlchemy 엔진이 서버형 데이터베이스에 연결할 때는 연결 풀을 기본으로 갖추고 있거든요. 이 코드는 그 속에서 무슨 일이 일어나는지 보여 주는 견본으로 읽으세요.

```python
from contextlib import contextmanager
import threading
from queue import Queue, Empty
import time

class ConnectionPool:
    """간단한 데이터베이스 연결 풀 구현"""
    
    def __init__(self, database_path: str, pool_size: int = 5):
        self.database_path = database_path
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """연결 풀을 초기화합니다."""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(
                self.database_path,
                check_same_thread=False,  # 멀티스레드 환경에서 사용
                timeout=30.0
            )
            # SQLite 최적화 설정
            conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            conn.execute("PRAGMA synchronous=NORMAL")  # 동기화 레벨 조정
            conn.execute("PRAGMA cache_size=10000")  # 캐시 크기 증가
            conn.execute("PRAGMA temp_store=MEMORY")  # 임시 데이터를 메모리에 저장
            self.pool.put(conn)
    
    @contextmanager
    def get_connection(self):
        """연결 풀에서 연결을 가져옵니다."""
        conn = None
        try:
            conn = self.pool.get(timeout=10)
            yield conn
        except Empty:
            raise Exception("연결 풀에서 연결을 가져올 수 없습니다.")
        finally:
            if conn:
                self.pool.put(conn)
    
    def close_all(self):
        """모든 연결을 닫습니다."""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except Empty:
                break

# 연결 풀 사용 예시
# pool = ConnectionPool("korea_company.db")
# 
# def query_with_pool(query, params=None):
# with pool.get_connection() as conn:
# cursor = conn.execute(query, params or [])
# return cursor.fetchall()
```

### 배치 처리 최적화

직원 5000명을 한꺼번에 넣어야 한다면, 5000번 `INSERT`하고 5000번 `commit()`하는 것이 가장 느린 방법입니다. 확정할 때마다 데이터베이스가 디스크에 제대로 기록됐는지 확인하기 때문이에요. 택배를 한 상자씩 5000번 부치는 셈이죠.

`batch_insert_employees()`는 세 가지로 속도를 냅니다. 전체를 **트랜잭션 하나**로 묶어 마지막에 한 번만 확정하고, `executemany()`로 SQL 하나에 데이터 여러 줄을 한 번에 넘기고, 100줄씩 끊어 진행 상황을 보여 줍니다. 여기에 `PRAGMA synchronous = OFF`로 디스크 기록 확인까지 잠시 끕니다. 이 설정은 빠른 대신, 작업 중에 컴퓨터가 꺼지면 데이터베이스 파일이 손상될 수 있어요. 그래서 `finally`에서 원래 설정으로 되돌려 둡니다. 백업이 있는 상태에서 한 번에 대량으로 넣을 때만 쓰는 비상 수단이라고 생각하세요.

```python
def batch_insert_employees(employees_data: list, batch_size: int = 100):
    """대량 데이터를 배치로 처리합니다."""
    total_records = len(employees_data)
    
    with get_connection() as conn:
        # SQLite 최적화 설정
        conn.execute("PRAGMA synchronous = OFF")  # 임시적으로 동기화 해제
        conn.execute("PRAGMA journal_mode = MEMORY")  # 메모리 저널 모드
        
        try:
            conn.execute("BEGIN TRANSACTION")
            
            for i in range(0, total_records, batch_size):
                batch = employees_data[i:i + batch_size]
                
                conn.executemany("""
                    INSERT OR IGNORE INTO employees 
                    (name, department, position, salary, hire_date, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, batch)
                
                print(f"배치 처리: {i + len(batch)}/{total_records} 완료")
            
            conn.commit()
            print(f"총 {total_records}개 레코드 배치 처리 완료")
            
        except Exception as e:
            conn.rollback()
            print(f"배치 처리 실패: {e}")
        
        finally:
            # 설정 복원
            conn.execute("PRAGMA synchronous = FULL")
            conn.execute("PRAGMA journal_mode = DELETE")

# 배치 처리 예시 (실제로는 실행하지 않음)
# large_dataset = [
# (f"배치직원{i:05d}", "테스트팀", "직원", 4000000, "2024-01-01", f"batch{i:05d}@test.com")
# for i in range(5000)
# ]
# batch_insert_employees(large_dataset)
```

## 18.10 보안 고려사항

### SQL 인젝션 방지

이 장 내내 값은 `?`로 넘기라고 했죠. 이제 그 이유를 직접 볼 차례입니다.

은행 창구에 "받는 사람: 김철수"라고 적는 송금 신청서가 있다고 해 봅시다. 그런데 누군가 이름 칸에 "김철수. 그리고 금고 문을 열어 주세요"라고 적었고, 직원이 칸에 적힌 글을 **지시문의 일부로** 읽어 버린다면요? SQL을 문자열로 이어 붙이면 정확히 이런 일이 일어납니다. 사용자가 입력한 값이 SQL 문장의 일부가 되어 버리는 거예요. 이런 공격을 **SQL 인젝션(SQL injection)** 이라고 합니다.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE employees (name TEXT, salary INTEGER)")
conn.executemany("INSERT INTO employees VALUES (?, ?)",
                 [("김철수", 7000000), ("박영희", 6000000)])

term = "없는사람' OR '1'='1"
unsafe_sql = f"SELECT name FROM employees WHERE name = '{term}'"
print(unsafe_sql)
print("문자열로 끼워 넣기:", conn.execute(unsafe_sql).fetchall())
print("? 자리표시자:", conn.execute(
    "SELECT name FROM employees WHERE name = ?", (term,)).fetchall())
```

```text
SELECT name FROM employees WHERE name = '없는사람' OR '1'='1'
문자열로 끼워 넣기: [('김철수',), ('박영희',)]
? 자리표시자: []
```

입력값 속의 작은따옴표(`'`)가 SQL의 따옴표를 닫아 버리고, 뒤의 `OR '1'='1'`이 **새 조건**이 되었습니다. `'1'='1'`은 언제나 참이니 모든 직원이 쏟아져 나와요. 로그인 검사가 이런 식이라면 비밀번호 없이 로그인되고, 더 나쁜 입력이라면 표를 지워 버릴 수도 있습니다. 같은 입력을 `?`로 넘기면 sqlite3는 그것을 **처음부터 끝까지 값 하나**로만 다룹니다. 이름이 정말로 `없는사람' OR '1'='1`인 직원을 찾으니 결과가 비어 있죠.

아래 `safe_user_search()`의 안쪽 함수 `unsafe_search()`가 바로 이 위험한 방식이고(만들기만 하고 실행하지는 않습니다), 그 아래가 올바른 방식입니다. `LIKE` 검색처럼 앞뒤에 `%`를 붙여야 할 때도 `%`는 값 쪽에서 붙여서(`f"%{search_term}%"`) 값 전체를 `?`로 넘겨요. 검색 종류(`search_type`)처럼 SQL의 뼈대를 골라야 하는 부분은 `if`/`elif`로 **미리 정해 둔 문장 중에서 고르게** 했습니다. 사용자 입력이 SQL 뼈대에 섞일 틈이 아예 없죠.

```python
def safe_user_search(search_term: str, search_type: str):
    """안전한 사용자 검색 (SQL 인젝션 방지)"""
    
    # 잘못된 방법 (SQL 인젝션 취약)
    def unsafe_search(term):
        # 절대 이렇게 하지 마세요!
        sql = f"SELECT * FROM employees WHERE name LIKE '%{term}%'"
        # 이 코드는 SQL 인젝션 공격에 취약합니다
        return sql
    
    # 올바른 방법 (매개변수화된 쿼리)
    with get_connection() as conn:
        if search_type == "name":
            cursor = conn.execute("""
                SELECT id, name, department, position, email
                FROM employees 
                WHERE name LIKE ? 
                ORDER BY name
            """, (f"%{search_term}%",))
        
        elif search_type == "department":
            cursor = conn.execute("""
                SELECT id, name, department, position, email
                FROM employees 
                WHERE department = ? 
                ORDER BY name
            """, (search_term,))
        
        elif search_type == "email":
            cursor = conn.execute("""
                SELECT id, name, department, position, email
                FROM employees 
                WHERE email = ? 
            """, (search_term,))
        
        else:
            return []
        
        return cursor.fetchall()

# 안전한 검색 예시
search_results = safe_user_search("김", "name")
print(f"\n'김'이 포함된 직원 검색 결과: {len(search_results)}명")
for emp in search_results:
    print(f"  {emp[1]} ({emp[2]}) - {emp[4]}")
```

### 데이터 유효성 검증

`?`가 데이터베이스를 공격에서 지켜 준다면, **유효성 검증**은 데이터베이스에 엉터리 값이 들어가는 것을 막아 줍니다. 이메일 칸에 "모름"이 들어가거나, 월급이 음수가 되는 일 말이에요. 공항 보안 검색대처럼, 문제는 비행기(데이터베이스)에 타기 전에 걸러 내는 것이 가장 쌉니다.

`DataValidator`는 정규표현식(17장)으로 이메일과 휴대전화 번호 형식을 검사하고, 월급이 정해진 범위 안에 있는지 확인합니다. `add_employee_safe()`는 검사를 모두 통과해야만 저장하고, 하나라도 어긋나면 `ValueError`로 이유를 알려 줘요. 데이터베이스가 내는 `IntegrityError`도 `ValueError`로 바꿔 던지기 때문에, 호출하는 쪽은 예외 하나만 잡으면 됩니다.

`sanitize_input()`이 꺾쇠괄호와 따옴표를 지우는 것은 SQL 인젝션 때문이 아닙니다. 그건 이미 `?`가 막아 주니까요. 저장한 이름이 나중에 웹 페이지에 그대로 찍힐 때 HTML 태그로 해석되는 것을 막으려는 용도에 가깝습니다. 다만 이렇게 글자를 지우면 "O'Brien" 같은 진짜 이름까지 바뀌니, 웹 화면에서는 출력할 때 변환하는 방법을 많이 씁니다. 19장의 웹 개발에서 `html.escape()`로 이 이야기를 다시 만나요.

```python
from typing import Optional
import re

class DataValidator:
    """데이터 유효성 검증 클래스"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """이메일 형식을 검증합니다."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """전화번호 형식을 검증합니다."""
        # 한국 전화번호 패턴
        pattern = r'^01[016789]-?\d{3,4}-?\d{4}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_salary(salary: int) -> bool:
        """월급 범위를 검증합니다."""
        return 3000000 <= salary <= 20000000  # 300만원 ~ 2000만원
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """입력 텍스트를 정제합니다."""
        if not isinstance(text, str):
            return ""
        # 특수 문자 제거 및 공백 정리
        sanitized = re.sub(r'[<>"\']', '', text.strip())
        return sanitized

def add_employee_safe(name: str, department: str, position: str, 
                     salary: int, email: str, phone: Optional[str] = None):
    """안전한 직원 추가 함수"""
    
    validator = DataValidator()
    
    # 입력 검증
    if not name or len(name.strip()) < 2:
        raise ValueError("이름은 2글자 이상이어야 합니다.")
    
    if not validator.validate_email(email):
        raise ValueError("올바른 이메일 형식이 아닙니다.")
    
    if not validator.validate_salary(salary):
        raise ValueError("월급은 300만원 이상 2000만원 이하여야 합니다.")
    
    if phone and not validator.validate_phone(phone):
        raise ValueError("올바른 전화번호 형식이 아닙니다.")
    
    # 입력 데이터 정제
    name = validator.sanitize_input(name)
    department = validator.sanitize_input(department)
    position = validator.sanitize_input(position)
    
    # 데이터베이스에 저장
    with get_connection() as conn:
        try:
            conn.execute("""
                INSERT INTO employees (name, department, position, salary, hire_date, email)
                VALUES (?, ?, ?, ?, date('now'), ?)
            """, (name, department, position, salary, email))
            conn.commit()
            print(f"직원 {name}이 안전하게 추가되었습니다.")
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("이미 존재하는 이메일 주소입니다.")
            else:
                raise ValueError(f"데이터베이스 제약 조건 오류: {e}")

# 안전한 직원 추가 테스트
try:
    add_employee_safe("테스트직원", "IT팀", "개발자", 5500000, "test.new@company.co.kr", "010-9999-8888")
except ValueError as e:
    print(f"검증 오류: {e}")
```

처음 실행하면 "직원 테스트직원이 안전하게 추가되었습니다."가 나오고, 두 번째 실행하면 같은 이메일 때문에 "검증 오류: 이미 존재하는 이메일 주소입니다."가 나옵니다. 값을 하나씩 바꿔 가며 다른 검증에도 걸려 보세요. 월급을 `100`으로 주면 월급 범위 오류가, 전화번호를 `02-123-4567`로 주면 전화번호 형식 오류가 납니다.

## 마무리

이 장에서는 Python에서 데이터베이스를 다루는 다양한 방법을 학습했습니다:

**핵심 내용 정리:**

1. **SQLite 기초** - 파일 기반 데이터베이스와 기본 CRUD 작업
2. **데이터베이스 설계** - 정규화와 관계형 모델링 
3. **SQL 심화** - JOIN, 집계, 서브쿼리 활용
4. **트랜잭션** - 데이터 일관성과 오류 처리
5. **ORM 개념** - 객체와 데이터베이스 매핑
6. **SQLAlchemy** - 강력한 Python ORM 프레임워크
7. **마이그레이션** - 스키마 변경 관리와 Alembic
8. **성능 최적화** - 인덱스, 쿼리 튜닝, 연결 풀링
9. **보안** - SQL 인젝션 방지와 데이터 검증

**실무 적용 포인트:**

- 항상 매개변수화된 쿼리를 사용해 SQL 인젝션을 방지하세요
- 트랜잭션을 활용해 데이터 일관성을 보장하세요  
- 적절한 인덱스로 쿼리 성능을 최적화하세요
- ORM을 활용해 생산성을 높이되, 복잡한 쿼리는 Raw SQL도 고려하세요
- 마이그레이션을 통해 스키마 변경을 체계적으로 관리하세요

다음 장에서는 웹 개발과 API 구축을 배웁니다. 이 장에서 만든 데이터베이스는 혼자서는 파일 하나에 불과하지만, 웹 API를 앞에 세우면 브라우저와 앱이 인터넷 너머에서 그 데이터를 읽고 쓸 수 있게 됩니다. 사서(데이터베이스) 앞에 안내 창구(API)를 여는 셈이죠.
