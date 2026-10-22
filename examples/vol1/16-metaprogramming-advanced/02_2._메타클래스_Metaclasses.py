"""1권 Chapter 16: 메타프로그래밍과 고급 기법 — 2. 메타클래스 (Metaclasses)

원고: manuscript/chapters/16-metaprogramming-advanced.md (334줄부터)
"""

# ---- 원고 334줄 ----
class TestMetaclassBasics:
    def test_type_as_metaclass(self):
        """type을 이용한 동적 클래스 생성"""
        # 일반적인 클래스 정의와 동일한 효과
        def init_method(self, 이름):
            self.이름 = 이름
        
        def 인사_method(self):
            return f"안녕하세요, {self.이름}님!"
        
        # type(name, bases, dict)로 클래스 생성
        사람 = type('사람', (), {
            '__init__': init_method,
            '인사': 인사_method
        })
        
        person = 사람("김철수")
        assert person.이름 == "김철수"
        assert person.인사() == "안녕하세요, 김철수님!"
    
    def test_custom_metaclass(self):
        """커스텀 메타클래스 정의"""
        class SingletonMeta(type):
            _instances = {}
            
            def __call__(cls, *args, **kwargs):
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
                return cls._instances[cls]
        
        class 로거(metaclass=SingletonMeta):
            def __init__(self):
                self.로그들 = []
            
            def 로그(self, 메시지):
                self.로그들.append(메시지)
        
        logger1 = 로거()
        logger2 = 로거()
        
        assert logger1 is logger2
        
        logger1.로그("테스트 메시지")
        assert "테스트 메시지" in logger2.로그들

# ---- 원고 391줄 ----
class TestMetaclassApplications:
    def test_validation_metaclass(self):
        """필드 유효성 검사 메타클래스"""
        import inspect

        class ValidatedMeta(type):
            def __new__(mcs, name, bases, namespace):
                cls = super().__new__(mcs, name, bases, namespace)

                # 유효성 검사 규칙 수집: 클래스 본문의 '이름: 타입' 어노테이션
                validators = inspect.get_annotations(cls)

                def validate_init(original_init):
                    signature = inspect.signature(original_init)

                    @wraps(original_init)
                    def new_init(self, *args, **kwargs):
                        # 위치 인자와 키워드 인자를 매개변수 이름에 짝지음
                        bound = signature.bind(self, *args, **kwargs)
                        for field, value in bound.arguments.items():
                            validator = validators.get(field)
                            if validator and not isinstance(value, validator):
                                raise TypeError(
                                    f"{field}는 {validator.__name__} 타입이어야 합니다"
                                )
                        return original_init(self, *args, **kwargs)
                    return new_init

                if '__init__' in namespace:
                    cls.__init__ = validate_init(namespace['__init__'])

                return cls
        
        class 학생(metaclass=ValidatedMeta):
            이름: str
            나이: int
            
            def __init__(self, 이름, 나이):
                self.이름 = 이름
                self.나이 = 나이
        
        # 정상 생성
        student = 학생("김철수", 20)
        assert student.이름 == "김철수"
        
        # 타입 오류
        with pytest.raises(TypeError):
            학생("김철수", "스무살")  # 나이가 문자열
    
    def test_orm_like_metaclass(self):
        """ORM과 유사한 메타클래스"""
        class ModelMeta(type):
            def __new__(mcs, name, bases, namespace):
                if name == 'Model':
                    return super().__new__(mcs, name, bases, namespace)
                
                # 필드 정보 수집
                fields = {}
                for key, value in namespace.items():
                    if isinstance(value, type):  # 타입 어노테이션
                        fields[key] = value
                
                namespace['_fields'] = fields
                
                # save 메서드 자동 추가
                def save(self):
                    data = {}
                    for field in fields:
                        if hasattr(self, field):
                            data[field] = getattr(self, field)
                    return data
                
                namespace['save'] = save
                
                return super().__new__(mcs, name, bases, namespace)
        
        class Model(metaclass=ModelMeta):
            pass
        
        class 사용자(Model):
            이름 = str
            이메일 = str
            
            def __init__(self, 이름, 이메일):
                self.이름 = 이름
                self.이메일 = 이메일
        
        user = 사용자("김철수", "kim@example.com")
        saved_data = user.save()
        
        assert saved_data == {"이름": "김철수", "이메일": "kim@example.com"}
        assert "이름" in 사용자._fields

# ---- 원고 488줄 ----
class Base:
    registry = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Base.registry.append(cls.__name__)   # 자식 클래스가 생길 때마다 등록


class A(Base):
    pass


class B(Base):
    pass

print(Base.registry)   # ['A', 'B']
