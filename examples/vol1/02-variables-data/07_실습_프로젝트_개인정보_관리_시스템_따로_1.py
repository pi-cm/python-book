"""1권 Chapter 2. 변수와 데이터 — 실습 프로젝트: 개인정보 관리 시스템

원고: manuscript/chapters/02-variables-data.md (879줄부터)
"""

# ---- 원고 879줄 ----
from typing import Dict, List, Optional, Literal
from datetime import datetime, date
import json

class 한국인정보:
    """한국인 개인정보를 관리하는 클래스"""
    
    def __init__(
        self,
        이름: str,
        생년월일: str,  # "YYYY-MM-DD" 형식
        성별: Literal["남", "여"],
        거주지: str,
        직업: Optional[str] = None,
        연락처: Optional[str] = None,
        이메일: Optional[str] = None
    ):
        self.이름 = 이름
        self.생년월일 = datetime.strptime(생년월일, "%Y-%m-%d").date()
        self.성별 = 성별
        self.거주지 = 거주지
        self.직업 = 직업
        self.연락처 = 연락처
        self.이메일 = 이메일
        self.등록일 = datetime.now()
    
    @property
    def 나이(self) -> int:
        """현재 나이 계산"""
        오늘 = date.today()
        나이 = 오늘.year - self.생년월일.year
        
        # 생일이 안 지났으면 1살 빼기
        if (오늘.month, 오늘.day) < (self.생년월일.month, self.생년월일.day):
            나이 -= 1
        
        return 나이
    
    @property
    def 연령대(self) -> str:
        """연령대 반환 (10대, 20대, ...)"""
        return f"{(self.나이 // 10) * 10}대"
    
    def 자기소개(self) -> str:
        """자기소개 문장 생성"""
        직업_부분 = f", {self.직업}" if self.직업 else ""
        return f"안녕하세요! 저는 {self.거주지}에 거주하는 {self.나이}세 {self.이름}입니다{직업_부분}."
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "이름": self.이름,
            "생년월일": self.생년월일.isoformat(),
            "성별": self.성별,
            "거주지": self.거주지,
            "직업": self.직업,
            "연락처": self.연락처,
            "이메일": self.이메일,
            "나이": self.나이,
            "연령대": self.연령대,
            "등록일": self.등록일.isoformat()
        }
    
    def __str__(self) -> str:
        return f"{self.이름}({self.성별}, {self.나이}세, {self.거주지})"
    
    def __repr__(self) -> str:
        return f"한국인정보(이름='{self.이름}', 나이={self.나이}, 거주지='{self.거주지}')"

class 정보관리시스템:
    """개인정보 관리 시스템"""
    
    def __init__(self):
        self.사람들: List[한국인정보] = []
    
    def 등록(self, 사람: 한국인정보) -> None:
        """새 사람 정보 등록"""
        # 중복 체크
        for 기존_사람 in self.사람들:
            if 기존_사람.이름 == 사람.이름 and 기존_사람.생년월일 == 사람.생년월일:
                raise ValueError(f"{사람.이름}님은 이미 등록되어 있습니다.")
        
        self.사람들.append(사람)
        print(f"[O] {사람.이름}님이 등록되었습니다.")
    
    def 검색_이름(self, 이름: str) -> List[한국인정보]:
        """이름으로 검색"""
        return [사람 for 사람 in self.사람들 if 이름 in 사람.이름]
    
    def 검색_거주지(self, 거주지: str) -> List[한국인정보]:
        """거주지로 검색"""
        return [사람 for 사람 in self.사람들 if 거주지 in 사람.거주지]
    
    def 연령대_통계(self) -> Dict[str, int]:
        """연령대별 통계"""
        통계 = {}
        for 사람 in self.사람들:
            연령대 = 사람.연령대
            통계[연령대] = 통계.get(연령대, 0) + 1
        return dict(sorted(통계.items()))
    
    def 성별_통계(self) -> Dict[str, int]:
        """성별 통계"""
        통계 = {"남": 0, "여": 0}
        for 사람 in self.사람들:
            통계[사람.성별] += 1
        return 통계
    
    def 지역별_통계(self) -> Dict[str, int]:
        """지역별 통계"""
        통계 = {}
        for 사람 in self.사람들:
            # 거주지에서 시/도 추출
            지역 = 사람.거주지.split()[0]
            통계[지역] = 통계.get(지역, 0) + 1
        return dict(sorted(통계.items(), key=lambda x: x[1], reverse=True))
    
    def 전체_목록(self) -> None:
        """전체 등록자 목록 출력"""
        if not self.사람들:
            print("등록된 사람이 없습니다.")
            return
        
        print(f"\n{'='*70}")
        print(f"{'이름':^10} {'성별':^6} {'나이':^6} {'거주지':^15} {'직업':^15}")
        print(f"{'='*70}")
        
        for 사람 in sorted(self.사람들, key=lambda x: x.나이):
            직업 = 사람.직업 or "미입력"
            print(f"{사람.이름:^10} {사람.성별:^6} {사람.나이:^6} {사람.거주지:^15} {직업:^15}")
        
        print(f"{'='*70}")
        print(f"총 {len(self.사람들)}명 등록됨")
    
    def 통계_출력(self) -> None:
        """전체 통계 출력"""
        print(f"\n=== 등록자 통계 ===")
        print(f"총 등록자 수: {len(self.사람들)}명")
        
        # 성별 통계
        성별통계 = self.성별_통계()
        print(f"\n성별 분포:")
        for 성별, 수 in 성별통계.items():
            비율 = (수 / len(self.사람들)) * 100 if self.사람들 else 0
            print(f"  {성별}: {수}명 ({비율:.1f}%)")
        
        # 연령대 통계
        연령통계 = self.연령대_통계()
        print(f"\n연령대 분포:")
        for 연령대, 수 in 연령통계.items():
            비율 = (수 / len(self.사람들)) * 100
            바 = "█" * (수 * 20 // max(연령통계.values())) if 수 > 0 else ""
            print(f"  {연령대}: {수}명 ({비율:.1f}%) {바}")
        
        # 지역 통계
        지역통계 = self.지역별_통계()
        print(f"\n지역 분포 (상위 5개):")
        for i, (지역, 수) in enumerate(list(지역통계.items())[:5], 1):
            비율 = (수 / len(self.사람들)) * 100
            print(f"  {i}. {지역}: {수}명 ({비율:.1f}%)")
    
    def 저장_JSON(self, 파일명: str) -> None:
        """JSON 파일로 저장"""
        데이터 = [사람.to_dict() for 사람 in self.사람들]
        with open(파일명, 'w', encoding='utf-8') as f:
            json.dump(데이터, f, ensure_ascii=False, indent=2)
        print(f"{파일명}에 저장되었습니다.")

def 샘플_데이터_생성() -> 정보관리시스템:
    """테스트용 샘플 데이터 생성"""
    시스템 = 정보관리시스템()
    
    샘플_사람들 = [
        ("김철수", "1990-05-15", "남", "서울특별시 강남구", "개발자", "010-1234-5678", "kim@email.com"),
        ("이영희", "1985-12-03", "여", "부산광역시 해운대구", "디자이너", "010-9876-5432", "lee@email.com"),
        ("박민수", "1995-08-20", "남", "대구광역시 수성구", "교사", "010-5555-1234", "park@email.com"),
        ("최미경", "1992-03-10", "여", "인천광역시 연수구", "간호사", "010-7777-9999", "choi@email.com"),
        ("정대호", "1988-11-25", "남", "광주광역시 서구", "의사", "010-3333-7777", "jung@email.com"),
        ("홍지은", "1993-07-08", "여", "대전광역시 유성구", "연구원", "010-2222-8888", "hong@email.com"),
        ("강동현", "1991-01-30", "남", "서울특별시 마포구", "기획자", "010-4444-6666", "kang@email.com"),
        ("윤서영", "1987-09-12", "여", "경기도 수원시", "변호사", "010-6666-4444", "yoon@email.com"),
    ]
    
    for 데이터 in 샘플_사람들:
        사람 = 한국인정보(*데이터)
        시스템.등록(사람)
    
    return 시스템

# 메인 실행 함수
def main():
    """메인 프로그램"""
    print("한국인 개인정보 관리 시스템")
    print("=" * 40)
    
    # 샘플 데이터로 시작
    시스템 = 샘플_데이터_생성()
    
    while True:
        print(f"\n메뉴")
        print("1. 전체 목록")
        print("2. 이름 검색")
        print("3. 거주지 검색")
        print("4. 통계 보기")
        print("5. 새 사람 등록")
        print("6. JSON 저장")
        print("0. 종료")
        
        선택 = input("\n선택하세요 (0-6): ").strip()
        
        match 선택:
            case "1":
                시스템.전체_목록()
            
            case "2":
                이름 = input("검색할 이름: ").strip()
                결과 = 시스템.검색_이름(이름)
                if 결과:
                    print(f"\n'{이름}' 검색 결과:")
                    for 사람 in 결과:
                        print(f"  - {사람}")
                        print(f"    {사람.자기소개()}")
                else:
                    print(f"'{이름}'에 해당하는 사람을 찾을 수 없습니다.")
            
            case "3":
                거주지 = input("검색할 거주지: ").strip()
                결과 = 시스템.검색_거주지(거주지)
                if 결과:
                    print(f"\n'{거주지}' 거주자:")
                    for 사람 in 결과:
                        print(f"  - {사람}")
                else:
                    print(f"'{거주지}'에 거주하는 사람을 찾을 수 없습니다.")
            
            case "4":
                시스템.통계_출력()
            
            case "5":
                try:
                    print("\n새 사람 등록:")
                    이름 = input("이름: ").strip()
                    생년월일 = input("생년월일 (YYYY-MM-DD): ").strip()
                    성별 = input("성별 (남/여): ").strip()
                    거주지 = input("거주지: ").strip()
                    직업 = input("직업 (선택사항): ").strip() or None
                    연락처 = input("연락처 (선택사항): ").strip() or None
                    이메일 = input("이메일 (선택사항): ").strip() or None
                    
                    새_사람 = 한국인정보(이름, 생년월일, 성별, 거주지, 직업, 연락처, 이메일)
                    시스템.등록(새_사람)
                    
                except ValueError as e:
                    print(f"[X] 오류: {e}")
                except Exception as e:
                    print(f"[X] 입력 오류: {e}")
            
            case "6":
                파일명 = input("저장할 파일명 (기본: 개인정보.json): ").strip()
                if not 파일명:
                    파일명 = "개인정보.json"
                시스템.저장_JSON(파일명)
            
            case "0":
                print("프로그램을 종료합니다.")
                break
            
            case _:
                print("[X] 잘못된 선택입니다.")

# 프로그램 실행
if __name__ == "__main__":
    main()
