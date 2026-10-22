"""1권 Chapter 7: 딕셔너리와 집합 — 7.7 실무 예제: 한국어 텍스트 분석 시스템

원고: manuscript/chapters/07-dictionaries-sets.md (539줄부터)
"""

# ---- 원고 539줄 ----
from collections import Counter, defaultdict
import re

class KoreanTextAnalyzer:
    """한국어 텍스트 분석기"""
    
    def __init__(self):
        self.stop_words = {
            "이", "그", "저", "것", "수", "등", "들", "및", "또는", 
            "하지만", "그러나", "따라서", "즉", "예를 들어"
        }
        
    def analyze_text(self, text):
        """텍스트 종합 분석"""
        # 기본 통계
        char_count = len(text)
        char_count_no_space = len(text.replace(' ', ''))
        word_count = len(text.split())
        line_count = text.count('\n') + 1
        
        # 문자 분석
        char_frequency = self._analyze_characters(text)
        
        # 단어 분석
        word_frequency = self._analyze_words(text)
        
        # 문장 분석
        sentence_analysis = self._analyze_sentences(text)
        
        return {
            "기본통계": {
                "전체문자수": char_count,
                "공백제외문자수": char_count_no_space,
                "단어수": word_count,
                "줄수": line_count
            },
            "문자분석": char_frequency,
            "단어분석": word_frequency,
            "문장분석": sentence_analysis
        }
    
    def _analyze_characters(self, text):
        """문자 빈도 분석"""
        # 한글, 영문, 숫자, 기타 분류
        korean_chars = set()
        english_chars = set()
        digits = set()
        special_chars = set()
        
        char_frequency = Counter(text.replace(' ', '').replace('\n', ''))
        
        for char in char_frequency:
            if '가' <= char <= '힣' or 'ㄱ' <= char <= 'ㅣ':
                korean_chars.add(char)
            elif 'a' <= char.lower() <= 'z':
                english_chars.add(char)
            elif char.isdigit():
                digits.add(char)
            else:
                special_chars.add(char)
        
        return {
            "총_고유문자수": len(char_frequency),
            "한글문자": {
                "개수": len(korean_chars),
                "빈출문자": char_frequency.most_common(10)
            },
            "영문문자수": len(english_chars),
            "숫자문자수": len(digits),
            "특수문자수": len(special_chars)
        }
    
    def _analyze_words(self, text):
        """단어 분석"""
        # 간단한 한국어 토큰화 (공백 기준)
        words = text.split()
        
        # 불용어 제거
        meaningful_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 1
        ]
        
        word_frequency = Counter(meaningful_words)
        
        return {
            "전체단어수": len(words),
            "유의미단어수": len(meaningful_words),
            "고유단어수": len(set(meaningful_words)),
            "평균단어길이": sum(len(word) for word in meaningful_words) / len(meaningful_words) if meaningful_words else 0,
            "빈출단어": word_frequency.most_common(10),
            "긴단어": sorted(set(meaningful_words), key=len, reverse=True)[:5]
        }
    
    def _analyze_sentences(self, text):
        """문장 분석"""
        # 문장 구분 (간단한 방식)
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        sentence_lengths = [len(s) for s in sentences]
        
        return {
            "문장수": len(sentences),
            "평균문장길이": sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            "최장문장길이": max(sentence_lengths) if sentence_lengths else 0,
            "최단문장길이": min(sentence_lengths) if sentence_lengths else 0
        }

# ---- 원고 653줄 ----
def demonstrate_text_analysis():
    """텍스트 분석 시연"""
    
    # 분석할 한국어 텍스트
    sample_text = """
파이썬은 1991년 귀도 반 로섬이 개발한 프로그래밍 언어입니다.
파이썬의 철학은 코드의 가독성과 단순함을 중시합니다.
들여쓰기를 사용하여 코드 블록을 구분하는 특징이 있습니다.
파이썬은 객체지향, 함수형, 절차형 프로그래밍을 모두 지원합니다.
웹 개발, 데이터 분석, 인공지능, 자동화 등 다양한 분야에서 사용됩니다.
배우기 쉽고 강력한 기능을 제공하여 전 세계 개발자들이 사용합니다.
"""
    
    analyzer = KoreanTextAnalyzer()
    results = analyzer.analyze_text(sample_text)
    
    print("한국어 텍스트 분석 결과")
    print("=" * 50)
    
    # 기본 통계
    basic_stats = results["기본통계"]
    print(f"\n기본 통계:")
    print(f"  전체 문자 수: {basic_stats['전체문자수']}자")
    print(f"  공백 제외: {basic_stats['공백제외문자수']}자")
    print(f"  단어 수: {basic_stats['단어수']}개")
    print(f"  줄 수: {basic_stats['줄수']}줄")
    
    # 문자 분석
    char_analysis = results["문자분석"]
    print(f"\n문자 분석:")
    print(f"  고유 문자 수: {char_analysis['총_고유문자수']}개")
    print(f"  한글 문자 수: {char_analysis['한글문자']['개수']}개")
    print(f"  빈출 문자 TOP 5:")
    for char, count in char_analysis['한글문자']['빈출문자'][:5]:
        print(f"    '{char}': {count}회")
    
    # 단어 분석
    word_analysis = results["단어분석"]
    print(f"\n단어 분석:")
    print(f"  전체 단어 수: {word_analysis['전체단어수']}개")
    print(f"  유의미 단어 수: {word_analysis['유의미단어수']}개")
    print(f"  고유 단어 수: {word_analysis['고유단어수']}개")
    print(f"  평균 단어 길이: {word_analysis['평균단어길이']:.1f}자")
    print(f"  빈출 단어 TOP 5:")
    for word, count in word_analysis['빈출단어'][:5]:
        print(f"    '{word}': {count}회")
    
    # 문장 분석
    sentence_analysis = results["문장분석"]
    print(f"\n문장 분석:")
    print(f"  문장 수: {sentence_analysis['문장수']}개")
    print(f"  평균 문장 길이: {sentence_analysis['평균문장길이']:.1f}자")
    print(f"  최장 문장 길이: {sentence_analysis['최장문장길이']}자")

# 텍스트 분석 실행
demonstrate_text_analysis()

# ---- 원고 724줄 ----
class AdvancedKoreanAnalyzer(KoreanTextAnalyzer):
    """고급 한국어 텍스트 분석기"""
    
    def __init__(self):
        super().__init__()
        self.pos_patterns = {
            "조사": ["은", "는", "이", "가", "을", "를", "의", "에", "에서", "로", "으로"],
            "어미": ["다", "요", "습니다", "었다", "았다", "겠다", "면서", "지만"],
            "접속사": ["그리고", "하지만", "그러나", "따라서", "그러므로", "또한"]
        }
    
    def compare_texts(self, text1, text2):
        """두 텍스트 비교 분석"""
        analysis1 = self.analyze_text(text1)
        analysis2 = self.analyze_text(text2)
        
        # 공통 단어 찾기
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        common_words = words1 & words2
        unique_to_text1 = words1 - words2
        unique_to_text2 = words2 - words1
        
        # 유사도 계산 (자카드 유사도)
        jaccard_similarity = len(common_words) / len(words1 | words2) if words1 | words2 else 0
        
        return {
            "공통단어": list(common_words),
            "텍스트1_고유단어": list(unique_to_text1),
            "텍스트2_고유단어": list(unique_to_text2),
            "자카드_유사도": jaccard_similarity,
            "분석1": analysis1,
            "분석2": analysis2
        }
    
    def extract_keywords(self, text, top_n=10):
        """키워드 추출"""
        words = [word for word in text.split() if len(word) > 2]
        word_freq = Counter(words)
        
        # 불용어와 조사/어미 제거
        filtered_words = {}
        for word, freq in word_freq.items():
            if (word not in self.stop_words and 
                not any(word.endswith(pattern) for patterns in self.pos_patterns.values() for pattern in patterns)):
                filtered_words[word] = freq
        
        # 빈도순 정렬
        keywords = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return keywords
    
    def generate_summary_stats(self, texts):
        """여러 텍스트의 종합 통계"""
        all_analyses = [self.analyze_text(text) for text in texts]
        
        # 전체 통계 집계
        total_chars = sum(analysis["기본통계"]["전체문자수"] for analysis in all_analyses)
        total_words = sum(analysis["기본통계"]["단어수"] for analysis in all_analyses)
        
        # 모든 단어 수집
        all_words = []
        for text in texts:
            all_words.extend(text.split())
        
        unique_words = set(all_words)
        word_frequency = Counter(all_words)
        
        return {
            "텍스트수": len(texts),
            "총문자수": total_chars,
            "총단어수": total_words,
            "고유단어수": len(unique_words),
            "평균텍스트길이": total_chars / len(texts),
            "전체빈출단어": word_frequency.most_common(20),
            "어휘다양성": len(unique_words) / total_words if total_words > 0 else 0
        }

# 고급 분석 시연
def demonstrate_advanced_analysis():
    """고급 분석 기능 시연"""
    
    texts = [
        "파이썬은 직관적이고 배우기 쉬운 프로그래밍 언어입니다. 다양한 라이브러리가 있어서 개발이 빠릅니다.",
        "자바는 객체지향 프로그래밍 언어입니다. 플랫폼 독립적이며 대규모 애플리케이션 개발에 적합합니다.",
        "자바스크립트는 웹 개발의 핵심 언어입니다. 프론트엔드와 백엔드 모두에서 사용할 수 있습니다."
    ]
    
    analyzer = AdvancedKoreanAnalyzer()
    
    print("\n고급 텍스트 분석")
    print("=" * 50)
    
    # 종합 통계
    summary = analyzer.generate_summary_stats(texts)
    print(f"\n종합 통계:")
    print(f"  분석 텍스트 수: {summary['텍스트수']}개")
    print(f"  총 문자 수: {summary['총문자수']}자")
    print(f"  고유 단어 수: {summary['고유단어수']}개")
    print(f"  어휘 다양성: {summary['어휘다양성']:.3f}")
    
    # 키워드 추출
    combined_text = " ".join(texts)
    keywords = analyzer.extract_keywords(combined_text, 5)
    print(f"\n주요 키워드:")
    for word, freq in keywords:
        print(f"  {word}: {freq}회")
    
    # 텍스트 간 비교
    comparison = analyzer.compare_texts(texts[0], texts[1])
    print(f"\n텍스트 1-2 비교:")
    print(f"  공통 단어: {len(comparison['공통단어'])}개")
    print(f"  유사도: {comparison['자카드_유사도']:.3f}")

demonstrate_advanced_analysis()
