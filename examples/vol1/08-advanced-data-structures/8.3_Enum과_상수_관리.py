"""1권 Chapter 8: 고급 데이터 구조 — 8.3 Enum과 상수 관리

원고: manuscript/chapters/08-advanced-data-structures.md (369줄부터)
"""

# ---- 원고 369줄 ----
from enum import Enum, IntEnum, Flag, auto
from typing import Dict, Any

class KoreanGrade(Enum):
    """한국 학점 시스템"""
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C_PLUS = "C+"
    C = "C"
    D_PLUS = "D+"
    D = "D"
    F = "F"
    
    @property
    def gpa_value(self) -> float:
        """GPA 값 반환"""
        gpa_mapping = {
            self.A_PLUS: 4.5, self.A: 4.0,
            self.B_PLUS: 3.5, self.B: 3.0,
            self.C_PLUS: 2.5, self.C: 2.0,
            self.D_PLUS: 1.5, self.D: 1.0,
            self.F: 0.0
        }
        return gpa_mapping[self]
    
    @property
    def korean_name(self) -> str:
        """한글 등급명"""
        korean_mapping = {
            self.A_PLUS: "매우우수", self.A: "우수",
            self.B_PLUS: "양호", self.B: "보통",
            self.C_PLUS: "미흡", self.C: "부족",
            self.D_PLUS: "매우부족", self.D: "불량",
            self.F: "낙제"
        }
        return korean_mapping[self]

class Priority(IntEnum):
    """우선순위 (정수 기반)"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    
    def __str__(self):
        korean_names = {
            self.LOW: "낮음",
            self.MEDIUM: "보통", 
            self.HIGH: "높음",
            self.CRITICAL: "긴급"
        }
        return korean_names[self]

class FilePermission(Flag):
    """파일 권한 (비트 플래그)"""
    READ = auto()
    WRITE = auto() 
    EXECUTE = auto()
    
    def to_korean(self) -> str:
        """한글 권한 설명"""
        permissions = []
        if self & FilePermission.READ:
            permissions.append("읽기")
        if self & FilePermission.WRITE:
            permissions.append("쓰기")
        if self & FilePermission.EXECUTE:
            permissions.append("실행")
        return ", ".join(permissions) if permissions else "권한 없음"

# 사용 예제
def demonstrate_enums():
    """Enum 시연"""
    print("한국 학점 시스템:")
    grades = [KoreanGrade.A_PLUS, KoreanGrade.B, KoreanGrade.C_PLUS, KoreanGrade.F]
    
    for grade in grades:
        print(f"{grade.value}: {grade.korean_name} (GPA: {grade.gpa_value})")
    
    print(f"\n평균 GPA: {sum(g.gpa_value for g in grades) / len(grades):.2f}")
    
    print("\n우선순위 비교:")
    task_priority = Priority.HIGH
    if task_priority >= Priority.HIGH:
        print(f"{task_priority} 우선순위 작업은 즉시 처리해야 합니다.")
    
    print("\n파일 권한:")
    file_perm = FilePermission.READ | FilePermission.WRITE
    print(f"현재 권한: {file_perm.to_korean()}")
    
    # 실행 권한 추가
    file_perm |= FilePermission.EXECUTE
    print(f"실행 권한 추가 후: {file_perm.to_korean()}")

demonstrate_enums()

# ---- 원고 477줄 ----
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

class OrderStatus(Enum):
    """주문 상태"""
    PENDING = "주문대기"
    CONFIRMED = "주문확인" 
    PREPARING = "준비중"
    SHIPPING = "배송중"
    DELIVERED = "배송완료"
    CANCELLED = "주문취소"
    RETURNED = "반품"
    
    def can_transition_to(self, new_status: 'OrderStatus') -> bool:
        """상태 전환 가능 여부 확인"""
        valid_transitions = {
            self.PENDING: {self.CONFIRMED, self.CANCELLED},
            self.CONFIRMED: {self.PREPARING, self.CANCELLED},
            self.PREPARING: {self.SHIPPING, self.CANCELLED},
            self.SHIPPING: {self.DELIVERED, self.RETURNED},
            self.DELIVERED: {self.RETURNED},
            self.CANCELLED: set(),  # 취소된 주문은 다른 상태로 변경 불가
            self.RETURNED: set()    # 반품된 주문은 다른 상태로 변경 불가
        }
        
        return new_status in valid_transitions.get(self, set())

@dataclass
class Order:
    """주문 클래스"""
    order_id: str
    customer_name: str
    product_name: str
    quantity: int
    price: int
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    status_history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.status_history is None:
            self.status_history = []
            self.status_history.append({
                "status": self.status,
                "timestamp": self.created_at,
                "note": "주문 생성"
            })
    
    def change_status(self, new_status: OrderStatus, note: str = "") -> bool:
        """주문 상태 변경"""
        if not self.status.can_transition_to(new_status):
            print(f"[X] {self.status.value}에서 {new_status.value}로 변경할 수 없습니다.")
            return False
        
        old_status = self.status
        self.status = new_status
        self.status_history.append({
            "status": new_status,
            "timestamp": datetime.now(),
            "note": note or f"{old_status.value} → {new_status.value}"
        })
        
        print(f"[O] 주문 {self.order_id}: {old_status.value} → {new_status.value}")
        return True
    
    def get_total_price(self) -> int:
        """총 가격 계산"""
        return self.price * self.quantity
    
    def print_status_history(self):
        """상태 변경 이력 출력"""
        print(f"\n주문 {self.order_id} 상태 이력:")
        for entry in self.status_history:
            timestamp = entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {timestamp} | {entry['status'].value} | {entry['note']}")

# 주문 처리 시뮬레이션
def simulate_order_processing():
    """주문 처리 시뮬레이션"""
    order = Order(
        order_id="ORD-2023-1201-001",
        customer_name="김철수",
        product_name="파이썬 프로그래밍 책",
        quantity=2,
        price=25000
    )
    
    print(f"새 주문 생성: {order.customer_name} - {order.product_name}")
    print(f"총 금액: {order.get_total_price():,}원")
    
    # 정상적인 주문 처리 과정
    order.change_status(OrderStatus.CONFIRMED, "결제 완료")
    order.change_status(OrderStatus.PREPARING, "상품 포장 시작")
    order.change_status(OrderStatus.SHIPPING, "택배 발송")
    
    # 잘못된 상태 변경 시도
    order.change_status(OrderStatus.PENDING, "되돌리기 시도")  # 실패해야 함
    
    # 정상 완료
    order.change_status(OrderStatus.DELIVERED, "고객 수령 확인")
    
    order.print_status_history()

simulate_order_processing()
