# [1권 Chapter 13: 상속과 다형성 (Inheritance and Polymorphism) · 13.5 실전 프로젝트: 한국 기업 HR 관리 시스템 · manuscript/chapters/13-inheritance-polymorphism.md:2413]
# hr_system_advanced.py
from abc import ABC, abstractmethod
from typing import Dict, List, TypeAlias, NewType, Literal
from pydantic import BaseModel, field_validator, Field
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

# 앞의 GREEN 단계에서 만든 클래스를 그대로 가져와 확장합니다 (같은 폴더의 hr_management_system.py)
from hr_management_system import (
    BaseEmployee, CEO, CTO, Department, EmployeeLevel, JuniorDeveloper, SeniorDeveloper,
)

# 타입 별칭과 NewType
EmployeeID: TypeAlias = str
Salary: TypeAlias = int
Score = NewType('Score', float)

class EmployeeData(BaseModel):
    """Pydantic를 활용한 데이터 검증"""
    name: str = Field(..., min_length=2, max_length=30)
    annual_salary: int = Field(..., gt=0, le=500000000)
    department: str
    hire_date: datetime = Field(default_factory=datetime.now)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    
    @field_validator('name')
    @classmethod
    def validate_korean_name(cls, v):
        if not any('가' <= c <= '힣' for c in v):
            raise ValueError('한국어 이름을 입력해주세요')
        return v

class HRSystemOptimized:
    """최적화된 HR 시스템"""
    
    def __init__(self):
        self._employees: Dict[EmployeeID, BaseEmployee] = {}
        self._department_index: Dict[Department, List[EmployeeID]] = {}
        self._level_index: Dict[EmployeeLevel, List[EmployeeID]] = {}
    
    async def add_employee_async(self, employee: BaseEmployee) -> None:
        """비동기 직원 추가"""
        await asyncio.sleep(0.1)  # DB 저장 시뮬레이션
        self._employees[employee.employee_id] = employee
        self._update_indices(employee)
        print(f"[O] {employee.name} 등록 완료 (비동기)")
    
    def _update_indices(self, employee: BaseEmployee) -> None:
        """인덱스 업데이트"""
        # 부서별 인덱스
        if employee.department not in self._department_index:
            self._department_index[employee.department] = []
        self._department_index[employee.department].append(employee.employee_id)
        
        # 직급별 인덱스
        if employee.level not in self._level_index:
            self._level_index[employee.level] = []
        self._level_index[employee.level].append(employee.employee_id)
    
    def get_employees_by_department(self, department: Department) -> List[BaseEmployee]:
        """부서별 직원 조회 (O(1) 인덱스 활용)"""
        employee_ids = self._department_index.get(department, [])
        return [self._employees[eid] for eid in employee_ids]
    
    def get_employees_by_level(self, level: EmployeeLevel) -> List[BaseEmployee]:
        """직급별 직원 조회"""
        employee_ids = self._level_index.get(level, [])
        return [self._employees[eid] for eid in employee_ids]
    
    @asynccontextmanager
    async def bulk_operation(self):
        """대량 작업용 컨텍스트 매니저"""
        print("대량 작업 시작...")
        start_time = datetime.now()
        try:
            yield self
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            print(f"[O] 대량 작업 완료 (소요 시간: {duration:.2f}초)")

# 고급 디자인 패턴 적용
class Command(ABC):
    """커맨드 패턴"""
    
    @abstractmethod
    async def execute(self) -> None:
        pass
    
    @abstractmethod
    async def undo(self) -> None:
        pass

class HireEmployeeCommand(Command):
    """직원 채용 커맨드"""
    
    def __init__(self, hr_system: HRSystemOptimized, employee: BaseEmployee):
        self.hr_system = hr_system
        self.employee = employee
        self.executed = False
    
    async def execute(self) -> None:
        await self.hr_system.add_employee_async(self.employee)
        self.executed = True
        print(f"[O] 채용 완료: {self.employee.name}")
    
    async def undo(self) -> None:
        if self.executed:
            # 실제로는 직원 제거 로직
            print(f"[!] 채용 취소: {self.employee.name}")
            self.executed = False

class PromoteEmployeeCommand(Command):
    """직원 승진 커맨드"""
    
    def __init__(self, employee: BaseEmployee, new_level: EmployeeLevel, 
                 new_salary: int):
        self.employee = employee
        self.new_level = new_level
        self.new_salary = new_salary
        self.old_level = employee.level
        self.old_salary = employee.annual_salary
        self.executed = False
    
    async def execute(self) -> None:
        self.employee.level = self.new_level
        self.employee.annual_salary = self.new_salary
        self.executed = True
        print(f"승진 완료: {self.employee.name} → {self.new_level.korean_name}")
    
    async def undo(self) -> None:
        if self.executed:
            self.employee.level = self.old_level
            self.employee.annual_salary = self.old_salary
            self.executed = False
            print(f"[!] 승진 취소: {self.employee.name}")

class HRCommandProcessor:
    """커맨드 프로세서"""
    
    def __init__(self):
        self._history: List[Command] = []
    
    async def execute_command(self, command: Command) -> None:
        """커맨드 실행"""
        await command.execute()
        self._history.append(command)
    
    async def undo_last_command(self) -> None:
        """마지막 커맨드 취소"""
        if self._history:
            last_command = self._history.pop()
            await last_command.undo()
        else:
            print("취소할 커맨드가 없습니다.")

# 종합 테스트 및 시연
async def main():
    """메인 실행 함수"""
    print("=== 고급 HR 시스템 시연 ===")
    
    hr_system = HRSystemOptimized()
    command_processor = HRCommandProcessor()
    
    # 직원들 생성
    employees = [
        CEO("김대표", 150000000),
        CTO("박기술", 100000000, "AI 혁신"),
        SeniorDeveloper("최개발", 60000000, ["Python", "Go"], 7),
        JuniorDeveloper("신입김", 40000000, ["Python"], 0.5)
    ]
    
    # 비동기 대량 채용
    async with hr_system.bulk_operation():
        for employee in employees:
            hire_command = HireEmployeeCommand(hr_system, employee)
            await command_processor.execute_command(hire_command)
    
    # 부서별 조회
    dev_employees = hr_system.get_employees_by_department(Department.ENGINEERING)
    print(f"\n개발팀 직원 수: {len(dev_employees)}명")
    
    # 승진 처리
    junior = next(emp for emp in employees if isinstance(emp, JuniorDeveloper))
    promote_command = PromoteEmployeeCommand(junior, EmployeeLevel.SENIOR, 50000000)
    await command_processor.execute_command(promote_command)
    
    # 승진 취소 시연
    print("\n승진 취소 시연:")
    await command_processor.undo_last_command()
    
    print("\n=== 시연 완료 ===")

if __name__ == "__main__":
    asyncio.run(main())
