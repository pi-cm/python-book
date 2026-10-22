# [1권 Chapter 13: 상속과 다형성 (Inheritance and Polymorphism) · 13.5 실전 프로젝트: 한국 기업 HR 관리 시스템 · manuscript/chapters/13-inheritance-polymorphism.md:1675]
# test_hr_system.py
import pytest
from datetime import datetime, date

def test_employee_hierarchy():
    """직원 계층 구조 테스트"""
    # 다양한 직급의 직원들이 올바른 계층을 형성해야 함
    ceo = CEO("김대표", 120000000)
    cto = CTO("박기술", 80000000, "Engineering")
    dev_manager = DevelopmentManager("이개발", 60000000, "Backend", 10)
    senior_dev = SeniorDeveloper("최시니어", 50000000, ["Python", "Go"], 8)
    junior_dev = JuniorDeveloper("신입김", 35000000, ["Python"], 0)
    
    # 보고 관계 설정
    cto.add_subordinate(dev_manager)
    dev_manager.add_subordinate(senior_dev)
    dev_manager.add_subordinate(junior_dev)
    senior_dev.add_mentee(junior_dev)
    
    # 계층 관계 검증
    assert junior_dev.get_direct_manager() == dev_manager
    assert senior_dev.get_department_head() == cto
    assert len(dev_manager.get_all_subordinates()) == 2

def test_payroll_calculation():
    """급여 계산 시스템 테스트"""
    employees = [
        CEO("김대표", 120000000),
        SeniorDeveloper("최시니어", 50000000, ["Python", "Go"], 8),
        JuniorDeveloper("신입김", 35000000, ["Python"], 0),
    ]
    payroll = PayrollProcessor()
    
    for employee in employees:
        salary_info = payroll.calculate_monthly_salary(employee)
        assert salary_info.base_salary > 0
        assert salary_info.total_before_tax >= salary_info.base_salary
        assert salary_info.total_deductions > 0  # 세금과 4대 보험 공제
        assert salary_info.net_salary < salary_info.total_before_tax

def test_performance_evaluation():
    """성과 평가 시스템 테스트"""
    employee = SeniorDeveloper("테스트", 50000000, ["Python"], 5)
    evaluator = PerformanceEvaluator()
    
    # 평가 항목 추가
    evaluator.add_evaluation_criteria("기술 역량", 0.4)
    evaluator.add_evaluation_criteria("협업 능력", 0.3) 
    evaluator.add_evaluation_criteria("리더십", 0.3)
    
    # 평가 진행
    evaluation = evaluator.evaluate(employee, {
        "기술 역량": 4.5,
        "협업 능력": 4.0,
        "리더십": 3.8
    })
    
    assert evaluation.overall_score > 0
    assert evaluation.grade in ['S', 'A', 'B', 'C', 'D']
    assert len(evaluation.feedback) > 0
