#!/usr/bin/env python3
"""
파이썬 백과사전 빌드 스크립트

기능:
- Markdown 파일들을 PDF, EPUB, DOCX로 변환
- 코드 예제 검증
- 링크 유효성 검사
- 진행률 통계

의존성:
- pandoc
- weasyprint (PDF 생성)
- gitbook-cli (선택사항)
"""

import subprocess
import json
from pathlib import Path
from typing import List
import argparse

# 권별 원고 폴더, 출력 파일 이름, 장 수
VOLUMES = {
    1: ("manuscript", "파이썬_완전_백과사전", 20),
    2: ("manuscript-vol2", "파이썬_완전_백과사전_2권_PyTorch", 21),
}


class BookBuilder:
    def __init__(self, volume: int = 1):
        manuscript_dir, self.book_name, self.chapter_count = VOLUMES[volume]
        self.manuscript_dir = Path(manuscript_dir)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def build_pdf(self):
        """Pandoc을 사용하여 PDF 생성"""
        print("📄 PDF 빌드 중...")
        
        # 모든 마크다운 파일 수집
        md_files = self._collect_markdown_files()
        
        # xelatex는 pandoc 임시 폴더에서 돌므로 글꼴 경로를 절대경로로 넘긴다
        tools_dir = Path(__file__).resolve().parent
        font_dir_tex = self.output_dir / ".book-fonts.tex"
        font_dir_tex.write_text(
            f"\\newcommand{{\\bookfontdir}}{{{(tools_dir / 'fonts').as_posix()}}}\n",
            encoding="utf-8",
        )

        # Pandoc 명령어 실행
        cmd = [
            "pandoc",
            # 인용 블록 안 "학습 목표" 목록처럼 빈 줄 없이 시작하는 목록도 목록으로 읽는다
            "--from", "markdown+lists_without_preceding_blankline",
            "--to", "pdf",
            "--output", str(self.output_dir / f"{self.book_name}.pdf"),
            "--toc",  # 목차 생성
            "--toc-depth=2",
            # 원고 제목에 이미 절 번호가 있으므로 --number-sections는 쓰지 않는다
            "--highlight-style=tango",  # 코드 하이라이팅
            "--pdf-engine=xelatex",
            "--lua-filter", str(tools_dir / "book.lua"),
            # 장 파일의 상대경로 이미지(../assets/images/...)를 찾도록 장 폴더를 기준에 넣는다
            "--resource-path", f".:{self.manuscript_dir / 'chapters'}",
            "--include-in-header", str(font_dir_tex),
            "--include-in-header", str(tools_dir / "pdf-header.tex"),
            "-V", "documentclass=book",
            "-V", "fontsize=11pt",
            # 판형: 188×257mm (국내 IT 단행본 판형)
            "-V", "geometry:paperwidth=188mm,paperheight=257mm,inner=22mm,outer=18mm,top=24mm,bottom=24mm,headsep=8mm",
            "-V", "lang=ko",
        ] + md_files
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ PDF 생성 완료!")
        except subprocess.CalledProcessError as e:
            print(f"❌ PDF 생성 실패: {e}")
    
    def build_epub(self):
        """EPUB 전자책 생성"""
        print("📱 EPUB 빌드 중...")
        
        md_files = self._collect_markdown_files()
        
        cmd = [
            "pandoc",
            "--from", "markdown",
            "--to", "epub3",
            "--output", str(self.output_dir / f"{self.book_name}.epub"),
            "--toc",
            "--toc-depth=3",
            "--epub-cover-image=assets/images/cover.png",
            "--epub-metadata=metadata.xml",
        ] + md_files
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ EPUB 생성 완료!")
        except subprocess.CalledProcessError as e:
            print(f"❌ EPUB 생성 실패: {e}")
    
    def build_docx(self):
        """Word 문서 생성 (출판사 제출용)"""
        print("📝 DOCX 빌드 중...")
        
        md_files = self._collect_markdown_files()
        
        cmd = [
            "pandoc",
            "--from", "markdown",
            "--to", "docx",
            "--output", str(self.output_dir / f"{self.book_name}.docx"),
            "--toc",
            "--highlight-style=tango",
            "--reference-doc=templates/reference.docx",  # 스타일 템플릿
        ] + md_files
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ DOCX 생성 완료!")
        except subprocess.CalledProcessError as e:
            print(f"❌ DOCX 생성 실패: {e}")
    
    def validate_code_examples(self):
        """코드 예제 검증"""
        print("🔍 코드 예제 검증 중...")
        
        errors = []
        for md_file in self.manuscript_dir.rglob("*.md"):
            errors.extend(self._validate_python_code_in_file(md_file))
        
        if errors:
            print(f"❌ {len(errors)}개 코드 오류 발견:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✅ 모든 코드 예제 검증 완료!")
    
    def generate_stats(self):
        """진행률 및 통계 생성"""
        print("📊 통계 생성 중...")
        
        stats = {
            "총_파일_수": 0,
            "총_단어_수": 0,
            "총_코드_블록_수": 0,
            "완성된_챕터": [],
            "진행중_챕터": [],
            "예상_페이지_수": 0
        }
        
        for md_file in self.manuscript_dir.rglob("*.md"):
            stats["총_파일_수"] += 1
            content = md_file.read_text(encoding='utf-8')
            stats["총_단어_수"] += len(content.split())
            stats["총_코드_블록_수"] += content.count("```python")
            
            # 완성도 확인
            if "TODO" in content or "작성 예정" in content:
                stats["진행중_챕터"].append(str(md_file))
            else:
                stats["완성된_챕터"].append(str(md_file))
        
        stats["예상_페이지_수"] = stats["총_단어_수"] // 500  # 한 페이지당 약 500단어
        
        # 결과 출력
        print("📊 통계 결과:")
        print(f"  - 총 파일 수: {stats['총_파일_수']}개")
        print(f"  - 총 단어 수: {stats['총_단어_수']:,}개")
        print(f"  - 코드 블록 수: {stats['총_코드_블록_수']}개")
        print(f"  - 완성된 챕터: {len(stats['완성된_챕터'])}개")
        print(f"  - 진행중 챕터: {len(stats['진행중_챕터'])}개")
        print(f"  - 예상 페이지 수: {stats['예상_페이지_수']}페이지")
        
        # JSON 파일로 저장
        with open(self.output_dir / "stats.json", "w", encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    
    def _collect_markdown_files(self) -> List[str]:
        """올바른 순서로 마크다운 파일 수집"""
        files = []
        
        # 챕터들을 순서대로
        for i in range(1, self.chapter_count + 1):
            pattern = f"chapters/{i:02d}-*.md"
            chapter_files = list(self.manuscript_dir.glob(pattern))
            if chapter_files:
                files.extend([str(f) for f in chapter_files])
        
        # 레퍼런스들
        ref_files = list((self.manuscript_dir / "references").glob("*.md"))
        files.extend([str(f) for f in sorted(ref_files)])
        
        # 부록들
        appendix_files = list((self.manuscript_dir / "appendix").glob("*.md"))
        files.extend([str(f) for f in sorted(appendix_files)])
        
        return files
    
    def _validate_python_code_in_file(self, file_path: Path) -> List[str]:
        """파일 내 Python 코드 검증"""
        errors = []
        content = file_path.read_text(encoding='utf-8')
        
        # 코드 블록 추출
        import re
        code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        
        for i, code in enumerate(code_blocks):
            try:
                compile(code, f"{file_path}:block_{i}", "exec")
            except SyntaxError as e:
                errors.append(f"{file_path}의 코드블록 {i+1}: {e}")
        
        return errors

def main():
    parser = argparse.ArgumentParser(description="파이썬 백과사전 빌드 도구")
    parser.add_argument("--pdf", action="store_true", help="PDF 생성")
    parser.add_argument("--epub", action="store_true", help="EPUB 생성")
    parser.add_argument("--docx", action="store_true", help="DOCX 생성")
    parser.add_argument("--validate", action="store_true", help="코드 검증")
    parser.add_argument("--stats", action="store_true", help="통계 생성")
    parser.add_argument("--all", action="store_true", help="모든 작업 수행")
    parser.add_argument("--vol", type=int, choices=sorted(VOLUMES), default=1, help="빌드할 권 (기본 1권)")
    
    args = parser.parse_args()
    builder = BookBuilder(args.vol)
    
    if args.all or args.validate:
        builder.validate_code_examples()
    
    if args.all or args.stats:
        builder.generate_stats()
    
    if args.all or args.pdf:
        builder.build_pdf()
    
    if args.all or args.epub:
        builder.build_epub()
    
    if args.all or args.docx:
        builder.build_docx()
    
    if not any([args.pdf, args.epub, args.docx, args.validate, args.stats, args.all]):
        print("사용법: python build.py [--pdf] [--epub] [--docx] [--validate] [--stats] [--all]")

if __name__ == "__main__":
    main()