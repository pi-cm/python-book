"""1권 Chapter 11: 객체 지향 프로그래밍 — 11.3 상속과 다형성

원고: manuscript/chapters/11-object-oriented-programming.md (478줄부터)
"""

# ---- 원고 478줄 ----
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

class Vehicle(ABC):
    """차량 추상 기본 클래스"""
    
    def __init__(self, brand: str, model: str, year: int, price: int):
        self.brand = brand
        self.model = model
        self.year = year
        self.price = price
        self.mileage = 0
        self.is_running = False
    
    @abstractmethod
    def start_engine(self) -> str:
        """엔진 시작 (추상 메서드)"""
        pass
    
    @abstractmethod
    def stop_engine(self) -> str:
        """엔진 정지 (추상 메서드)"""
        pass
    
    @abstractmethod
    def get_fuel_efficiency(self) -> float:
        """연비 반환 (추상 메서드)"""
        pass
    
    def get_basic_info(self) -> str:
        """기본 정보 반환"""
        return f"{self.brand} {self.model} ({self.year}년식)"
    
    def drive(self, distance: int) -> str:
        """운전"""
        if not self.is_running:
            return "[X] 엔진을 먼저 시작하세요"
        
        self.mileage += distance
        return f"{distance}km 운전했습니다. 총 주행거리: {self.mileage:,}km"
    
    def get_age(self) -> int:
        """차량 연식 계산"""
        return datetime.now().year - self.year

class KoreanCar(Vehicle):
    """한국 자동차 클래스"""
    
    def __init__(self, brand: str, model: str, year: int, price: int, 
                 displacement: float, fuel_type: str = "gasoline"):
        super().__init__(brand, model, year, price)
        self.displacement = displacement  # 배기량 (리터)
        self.fuel_type = fuel_type
        self.warranty_years = 5  # 한국차 기본 보증 5년
    
    def start_engine(self) -> str:
        if self.is_running:
            return "[X] 이미 엔진이 가동 중입니다"
        
        self.is_running = True
        return f"[O] {self.get_basic_info()} 엔진 시동 완료!"
    
    def stop_engine(self) -> str:
        if not self.is_running:
            return "[X] 엔진이 이미 정지되어 있습니다"
        
        self.is_running = False
        return f"{self.get_basic_info()} 엔진 정지"
    
    def get_fuel_efficiency(self) -> float:
        """한국차 연비 계산 (km/L)"""
        base_efficiency = 12.0  # 기본 12km/L
        
        # 배기량에 따른 연비 조정
        if self.displacement <= 1.0:
            return base_efficiency + 3.0
        elif self.displacement <= 1.6:
            return base_efficiency + 1.0
        elif self.displacement <= 2.0:
            return base_efficiency
        else:
            return base_efficiency - 2.0
    
    def check_warranty(self) -> str:
        """보증 기간 확인"""
        age = self.get_age()
        remaining = self.warranty_years - age
        
        if remaining > 0:
            return f"[O] 보증 기간 {remaining}년 남음"
        else:
            return f"[X] 보증 기간 {abs(remaining)}년 경과"

class ElectricCar(Vehicle):
    """전기 자동차 클래스"""
    
    def __init__(self, brand: str, model: str, year: int, price: int,
                 battery_capacity: float, range_km: int):
        super().__init__(brand, model, year, price)
        self.battery_capacity = battery_capacity  # kWh
        self.range_km = range_km  # 1회 충전 주행거리
        self.battery_level = 100  # 배터리 잔량 (%)
        self.is_charging = False
    
    def start_engine(self) -> str:
        if self.battery_level <= 0:
            return "[X] 배터리가 방전되었습니다. 충전이 필요합니다."
        
        if self.is_running:
            return "[X] 이미 전원이 켜져 있습니다"
        
        self.is_running = True
        return f"{self.get_basic_info()} 전원 켜짐! (배터리: {self.battery_level}%)"
    
    def stop_engine(self) -> str:
        if not self.is_running:
            return "[X] 이미 전원이 꺼져 있습니다"
        
        self.is_running = False
        return f"{self.get_basic_info()} 전원 종료"
    
    def get_fuel_efficiency(self) -> float:
        """전기차 효율성 (km/kWh)"""
        return self.range_km / self.battery_capacity
    
    def drive(self, distance: int) -> str:
        """전기차 운전 (배터리 소모 포함)"""
        if not self.is_running:
            return "[X] 전원을 먼저 켜세요"
        
        # 배터리 소모 계산
        battery_consumption = (distance / self.range_km) * 100
        
        if self.battery_level < battery_consumption:
            return f"[X] 배터리 부족! 현재 {self.battery_level:.1f}%, 필요 {battery_consumption:.1f}%"
        
        self.battery_level -= battery_consumption
        self.mileage += distance
        
        return f"{distance}km 운전 완료. 배터리: {self.battery_level:.1f}%, 총 주행거리: {self.mileage:,}km"
    
    def charge(self, time_hours: float) -> str:
        """배터리 충전"""
        if self.is_running:
            return "[X] 충전하려면 전원을 먼저 끄세요"
        
        # 1시간에 20% 충전으로 가정
        charge_amount = min(time_hours * 20, 100 - self.battery_level)
        self.battery_level += charge_amount
        
        return f"{time_hours}시간 충전 완료! 배터리: {self.battery_level:.1f}%"

# 다형성 시연
def test_vehicle(vehicle: Vehicle) -> None:
    """차량 테스트 함수 (다형성 활용)"""
    print(f"\n{vehicle.get_basic_info()} 테스트")
    print(f"연식: {vehicle.get_age()}년")
    print(f"연비/효율성: {vehicle.get_fuel_efficiency():.1f}")
    
    print(vehicle.start_engine())
    print(vehicle.drive(50))
    print(vehicle.stop_engine())
    
    # 전기차인 경우 추가 기능 테스트
    if isinstance(vehicle, ElectricCar):
        print(vehicle.charge(2.0))
    
    # 한국차인 경우 보증 확인
    if isinstance(vehicle, KoreanCar):
        print(vehicle.check_warranty())

# 사용 예제
vehicles: List[Vehicle] = [
    KoreanCar("현대", "소나타", 2020, 25000000, 2.0),
    KoreanCar("기아", "K5", 2022, 28000000, 1.6),
    ElectricCar("테슬라", "Model 3", 2023, 50000000, 75.0, 400)
]

# 다형성을 활용한 모든 차량 테스트
for vehicle in vehicles:
    test_vehicle(vehicle)
