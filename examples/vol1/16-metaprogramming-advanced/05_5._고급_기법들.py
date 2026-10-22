"""1권 Chapter 16: 메타프로그래밍과 고급 기법 — 5. 고급 기법들

원고: manuscript/chapters/16-metaprogramming-advanced.md (739줄부터)
"""

# ---- 원고 739줄 ----
class TestDynamicAttributes:
    def test_getattr_setattr(self):
        """동적 속성 접근 구현"""
        class 설정관리자:
            def __init__(self):
                self._설정들 = {}
            
            def __getattr__(self, name):
                if name.startswith('_'):
                    raise AttributeError(f"'{name}' 속성이 없습니다")
                return self._설정들.get(name, None)
            
            def __setattr__(self, name, value):
                if name.startswith('_'):
                    super().__setattr__(name, value)
                else:
                    if not hasattr(self, '_설정들'):
                        super().__setattr__('_설정들', {})
                    self._설정들[name] = value
            
            def __delattr__(self, name):
                if name in self._설정들:
                    del self._설정들[name]
                else:
                    raise AttributeError(f"'{name}' 속성이 없습니다")
        
        config = 설정관리자()
        config.데이터베이스_호스트 = "localhost"
        config.포트 = 5432
        
        assert config.데이터베이스_호스트 == "localhost"
        assert config.포트 == 5432
        assert config.존재하지않는설정 is None
        
        del config.포트
        assert config.포트 is None
    
    def test_slots_optimization(self):
        """__slots__를 이용한 최적화"""
        class 일반클래스:
            def __init__(self, x, y):
                self.x = x
                self.y = y
        
        class 최적화클래스:
            __slots__ = ['x', 'y']
            
            def __init__(self, x, y):
                self.x = x
                self.y = y
        
        normal = 일반클래스(1, 2)
        optimized = 최적화클래스(1, 2)
        
        # 일반 클래스는 __dict__ 있음
        assert hasattr(normal, '__dict__')
        normal.z = 3  # 동적 속성 추가 가능
        
        # 슬롯 클래스는 __dict__ 없음
        assert not hasattr(optimized, '__dict__')
        
        with pytest.raises(AttributeError):
            optimized.z = 3  # 동적 속성 추가 불가

# ---- 원고 813줄 ----
class TestOperatorOverloading:
    def test_arithmetic_operators(self):
        """산술 연산자 오버로딩"""
        class 벡터:
            def __init__(self, x, y):
                self.x = x
                self.y = y
            
            def __add__(self, other):
                return 벡터(self.x + other.x, self.y + other.y)
            
            def __sub__(self, other):
                return 벡터(self.x - other.x, self.y - other.y)
            
            def __mul__(self, scalar):
                return 벡터(self.x * scalar, self.y * scalar)
            
            def __rmul__(self, scalar):
                return self.__mul__(scalar)
            
            def __abs__(self):
                return (self.x ** 2 + self.y ** 2) ** 0.5
            
            def __eq__(self, other):
                return self.x == other.x and self.y == other.y
            
            def __repr__(self):
                return f"벡터({self.x}, {self.y})"
        
        v1 = 벡터(3, 4)
        v2 = 벡터(1, 2)
        
        # 벡터 덧셈
        v3 = v1 + v2
        assert v3.x == 4 and v3.y == 6
        
        # 벡터 뺄셈
        v4 = v1 - v2
        assert v4.x == 2 and v4.y == 2
        
        # 스칼라 곱셈
        v5 = v1 * 2
        v6 = 3 * v1
        assert v5.x == 6 and v5.y == 8
        assert v6.x == 9 and v6.y == 12
        
        # 크기 계산
        assert abs(벡터(3, 4)) == 5.0
