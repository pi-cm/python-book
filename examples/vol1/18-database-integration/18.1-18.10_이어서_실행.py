"""1권 Chapter 18: 데이터베이스 연동 — 18.1 SQLite 기초와 Python 연동 ~ 18.10 보안 고려사항 (앞 절의 정의를 이어 쓰므로 한 파일로 묶음)

원고: manuscript/chapters/18-database-integration.md (38줄부터)
"""

# ---- 원고 38줄 ----
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

# ---- 원고 87줄 ----
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

# ---- 원고 121줄 ----
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

# ---- 원고 156줄 ----
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

# ---- 원고 206줄 ----
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

# ---- 원고 302줄 ----
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

# ---- 원고 363줄 ----
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

# ---- 원고 402줄 ----
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

# ---- 원고 445줄 ----
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

# ---- 원고 497줄 ----
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

# ---- 원고 586줄 ----
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

# ---- 원고 640줄 ----
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

# ---- 원고 680줄 ----
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

# ---- 원고 728줄 ----
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

# ---- 원고 874줄 ----
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

# ---- 원고 1009줄 ----
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

# ---- 원고 1088줄 ----
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

# ---- 원고 1156줄 ----
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

# ---- 원고 1268줄 ----
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

# ---- 원고 1386줄 ----
def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("department", sa.String(50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("employees")

# ---- 원고 1402줄 ----
def upgrade() -> None:
    op.add_column("employees", sa.Column("birth_date", sa.Date))


def downgrade() -> None:
    op.drop_column("employees", "birth_date")

# ---- 원고 1464줄 ----
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

# ---- 원고 1492줄 ----
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE employees (name TEXT, department TEXT)")
sql = "SELECT * FROM employees WHERE department = ?"

print(conn.execute("EXPLAIN QUERY PLAN " + sql, ("개발팀",)).fetchall())
conn.execute("CREATE INDEX idx_employees_department ON employees (department)")
print(conn.execute("EXPLAIN QUERY PLAN " + sql, ("개발팀",)).fetchall())

# ---- 원고 1519줄 ----
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

# ---- 원고 1609줄 ----
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

# ---- 원고 1677줄 ----
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

# ---- 원고 1729줄 ----
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

# ---- 원고 1755줄 ----
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
