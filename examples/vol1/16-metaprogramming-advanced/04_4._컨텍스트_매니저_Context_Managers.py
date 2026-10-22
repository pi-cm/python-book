"""1권 Chapter 16: 메타프로그래밍과 고급 기법 — 4. 컨텍스트 매니저 (Context Managers)

원고: manuscript/chapters/16-metaprogramming-advanced.md (627줄부터)
"""

# ---- 원고 627줄 ----
class 조용히:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"정리 중 (예외: {exc_type.__name__ if exc_type else None})")
        return True   # True를 돌려주면 예외를 삼킴


with 조용히():
    1 / 0
print("프로그램은 계속됩니다")

# ---- 원고 649줄 ----
class TestContextManagers:
    def test_basic_context_manager(self):
        """기본 컨텍스트 매니저 구현"""
        class 파일관리자:
            def __init__(self, 파일명, 모드):
                self.파일명 = 파일명
                self.모드 = 모드
                self.파일 = None
            
            def __enter__(self):
                print(f"파일 열기: {self.파일명}")
                self.파일 = open(self.파일명, self.모드)
                return self.파일
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                print(f"파일 닫기: {self.파일명}")
                if self.파일:
                    self.파일.close()
                # 예외를 다시 발생시키려면 False 반환 (기본값)
                return False
        
        import tempfile
        import os
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp_name = tmp.name
            tmp.write("테스트 내용")
        
        try:
            with 파일관리자(tmp_name, 'r') as f:
                content = f.read()
                assert content == "테스트 내용"
        finally:
            os.unlink(tmp_name)
    
    def test_contextlib_usage(self):
        """contextlib을 이용한 컨텍스트 매니저"""
        from contextlib import contextmanager
        
        @contextmanager
        def 데이터베이스_트랜잭션():
            print("트랜잭션 시작")
            transaction = {"committed": False, "data": []}
            try:
                yield transaction
                print("트랜잭션 커밋")
                transaction["committed"] = True
            except Exception:
                print("트랜잭션 롤백")
                transaction["committed"] = False
                transaction["data"].clear()
                raise
        
        # 성공 케이스
        with 데이터베이스_트랜잭션() as trans:
            trans["data"].append("새 데이터")
        
        assert trans["committed"] == True
        assert "새 데이터" in trans["data"]
        
        # 예외 발생 케이스
        try:
            with 데이터베이스_트랜잭션() as trans:
                trans["data"].append("문제 데이터")
                raise ValueError("오류 발생!")
        except ValueError:
            pass
        
        assert trans["committed"] == False
        assert len(trans["data"]) == 0
