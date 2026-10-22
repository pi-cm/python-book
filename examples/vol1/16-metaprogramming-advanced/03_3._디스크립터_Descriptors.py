"""1권 Chapter 16: 메타프로그래밍과 고급 기법 — 3. 디스크립터 (Descriptors)

원고: manuscript/chapters/16-metaprogramming-advanced.md (523줄부터)
"""

# ---- 원고 523줄 ----
class TestDescriptors:
    def test_basic_descriptor(self):
        """기본 디스크립터 구현"""
        class Temperature:
            def __set_name__(self, owner, name):
                self.name = name  # 이 디스크립터가 붙은 속성 이름 ('온도')
            
            def __get__(self, obj, objtype=None):
                if obj is None:
                    return self
                return obj.__dict__[self.name]  # 값은 인스턴스마다 따로 보관
            
            def __set__(self, obj, value):
                if not isinstance(value, (int, float)):
                    raise TypeError("온도는 숫자여야 합니다")
                if value < -273.15:
                    raise ValueError("절대영도보다 낮을 수 없습니다")
                obj.__dict__[self.name] = value
            
            def __delete__(self, obj):
                raise AttributeError("온도는 삭제할 수 없습니다")
        
        class 날씨:
            온도 = Temperature()
            
            def __init__(self, 온도):
                self.온도 = 온도
        
        weather = 날씨(25.5)
        assert weather.온도 == 25.5
        
        # 객체마다 온도를 따로 가짐
        다른_날씨 = 날씨(30)
        assert weather.온도 == 25.5 and 다른_날씨.온도 == 30
        
        with pytest.raises(ValueError):
            weather.온도 = -300  # 절대영도보다 낮음
        
        with pytest.raises(AttributeError):
            del weather.온도
    
    def test_property_implementation(self):
        """프로퍼티 구현 원리 이해"""
        class MyProperty:
            def __init__(self, fget=None, fset=None, fdel=None):
                self.fget = fget
                self.fset = fset
                self.fdel = fdel
            
            def __get__(self, obj, objtype=None):
                if obj is None:
                    return self
                if self.fget is None:
                    raise AttributeError("읽을 수 없는 속성")
                return self.fget(obj)
            
            def __set__(self, obj, value):
                if self.fset is None:
                    raise AttributeError("설정할 수 없는 속성")
                self.fset(obj, value)
            
            def __delete__(self, obj):
                if self.fdel is None:
                    raise AttributeError("삭제할 수 없는 속성")
                self.fdel(obj)
        
        class 원:
            def __init__(self, 반지름):
                self._반지름 = 반지름
            
            def _get_면적(self):
                return 3.14159 * self._반지름 ** 2
            
            면적 = MyProperty(fget=_get_면적)
        
        circle = 원(5)
        assert abs(circle.면적 - 78.53975) < 0.001
        
        with pytest.raises(AttributeError):
            circle.면적 = 100  # 설정 불가
