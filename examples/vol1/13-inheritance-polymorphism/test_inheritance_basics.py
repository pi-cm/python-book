# [1권 Chapter 13: 상속과 다형성 (Inheritance and Polymorphism) · 13.1 상속 기초 - TDD로 시작하기 · manuscript/chapters/13-inheritance-polymorphism.md:38]
# test_inheritance_basics.py
import pytest
from abc import ABC, abstractmethod

def test_basic_inheritance():
    """기본 상속 관계 테스트"""
    # 이 테스트들은 처음엔 실패해야 함
    
    # 1. 부모 클래스 Employee가 존재해야 함
    employee = Employee("김철수", "개발팀", 35_000_000)
    assert employee.name == "김철수"
    assert employee.department == "개발팀" 
    assert employee.salary == 35_000_000
    
    # 2. 자식 클래스 Developer가 Employee를 상속해야 함
    dev = Developer("이영희", "개발팀", 40_000_000, "Python")
    assert isinstance(dev, Employee)  # is-a 관계
    assert dev.programming_language == "Python"
    
    # 3. 메서드 상속이 작동해야 함
    assert "김철수" in employee.introduce()
    assert "이영희" in dev.introduce()

def test_method_overriding():
    """메서드 오버라이딩 테스트"""
    
    # Manager는 introduce 메서드를 오버라이드해야 함
    manager = Manager("박부장", "영업팀", 60_000_000, 5)
    intro = manager.introduce()
    
    assert "부장" in intro or "관리자" in intro
    assert "5명" in intro
    assert manager.calculate_bonus() > 0

def test_super_usage():
    """super() 함수 사용 테스트"""
    
    # 자식 클래스에서 부모의 메서드를 확장해야 함
    senior_dev = SeniorDeveloper("최시니어", "개발팀", 55_000_000, "Java", 7)
    
    # 부모의 소개에 경력이 추가되어야 함
    intro = senior_dev.introduce()
    assert "최시니어" in intro
    assert "7년" in intro
    
    # 급여 계산이 확장되어야 함
    assert senior_dev.calculate_total_compensation() > senior_dev.salary

# 이 시점에서 이 테스트들은 모두 실패해야 함 (RED)
