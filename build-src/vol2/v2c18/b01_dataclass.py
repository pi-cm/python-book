import json
from dataclasses import asdict, dataclass, fields, replace


@dataclass(frozen=True)
class 학습설정:
    """실험 하나를 정하는 값들. 기본값이 곧 '기준 실험'이다."""
    모델: str = "mlp"
    학습률: float = 1e-3
    배치_크기: int = 64
    에폭: int = 2
    드롭아웃: float = 0.0
    씨앗: int = 0


기준 = 학습설정()
print(기준)

# 기준에서 한두 개만 바꾼 실험들: 원본은 그대로 두고 새 설정을 만든다
후보들 = [replace(기준, 학습률=학습률) for 학습률 in (3e-4, 1e-3, 3e-3)]
후보들.append(replace(기준, 모델="cnn", 드롭아웃=0.3))
for 설정 in 후보들:
    print(설정.모델, 설정.학습률, 설정.드롭아웃)

try:
    기준.학습률 = 0.1                       # frozen=True: 실험 도중에 몰래 바꿀 수 없다
except Exception as e:
    print("바꾸기 실패:", type(e).__name__)

# 딕셔너리로 바꾸면 JSON으로 저장할 수 있다
글 = json.dumps(asdict(후보들[-1]), ensure_ascii=False)
print(글)
다시 = 학습설정(**json.loads(글))
print("저장했다 불러와도 같은가:", 다시 == 후보들[-1])
print("필드 이름:", [f.name for f in fields(학습설정)])
