"""terms.py와 찾은 장 번호로 부록 C 원고를 만든다."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from terms import KO, EN
여기 = Path(__file__).parent
장 = {k: v[0] for k, v in json.load(open(여기 / "found2.json")).items()}
# 굵게 쓴 첫 자리가 예고(다음 장 미리보기 등)인 용어는 실제로 설명한 장으로 고친다
고침 = {"교차 검증": 3, "그래디언트 부스팅": 3, "재현성": 8, "표준편차": 1, "FastAPI": 20,
        "Hugging Face": 13, "nn.Module": 6, "Pipeline": 2, "state_dict": 6, "ReLU": 6,
        "순환 신경망": 11, "합성곱 신경망": 9, "병목": 7, "인코더": 12, "디코더": 12,
        "bfloat16": 16, "DDP": 17, "FlashAttention": 16, "CUDA": 4,
        "준비 운동": 4, "임베딩": 11}
장.update(고침)
초성 = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
기본 = {"ㄲ": "ㄱ", "ㄸ": "ㄷ", "ㅃ": "ㅂ", "ㅆ": "ㅅ", "ㅉ": "ㅈ"}
def 첫소리(s: str) -> str:
    c = 초성[(ord(s[0]) - 0xAC00) // 588]
    return 기본.get(c, c)
줄 = []
지금 = None
for 용어, 영문, 뜻, _ in sorted(KO, key=lambda r: r[0]):
    c = 첫소리(용어)
    if c != 지금:
        지금 = c
        줄 += ["", f"### {c}", "", "| 용어 | 영문 | 뜻 | 장 |", "|---|---|---|---|"]
    줄.append(f"| {용어} | {영문} | {뜻} | {장[용어]}장 |")
줄 += ["", "## C.2 영문으로 쓰는 용어", "", "약자나 이름을 영문 그대로 부르는 용어는 알파벳순으로 따로 모았습니다.", "",
       "| 용어 | 풀어 쓴 이름 | 뜻 | 장 |", "|---|---|---|---|"]
for 용어, 영문, 뜻, _ in sorted(EN, key=lambda r: r[0].lower()):
    줄.append(f"| {용어} | {영문 or '—'} | {뜻} | {장[용어]}장 |")
머리 = (여기 / "head.md").read_text(encoding="utf-8")
꼬리 = (여기 / "tail.md").read_text(encoding="utf-8")
Path(sys.argv[1]).write_text(머리.rstrip() + "\n" + "\n".join(줄) + "\n\n" + 꼬리, encoding="utf-8")
print("한글", len(KO), "영문", len(EN), "합계", len(KO) + len(EN))
from collections import Counter
print(sorted(Counter(장.values()).items()))
