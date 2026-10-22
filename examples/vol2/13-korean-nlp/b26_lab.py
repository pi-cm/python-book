# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.12 실습: 뉴스 제목 주제 분류기 만들기 · manuscript-vol2/chapters/13-korean-nlp.md:1192]
import torch
from datasets import load_dataset
from sklearn.metrics import classification_report
from torch.utils.data import DataLoader
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          DataCollatorWithPadding, get_linear_schedule_with_warmup)


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


# 1) 데이터: KLUE YNAT 뉴스 제목 주제 분류 (CC BY-SA 4.0)
자료 = load_dataset("klue/klue", "ynat")
주제들 = 자료["train"].features["label"].names
print("주제:", 주제들)
학습 = 자료["train"].shuffle(seed=0).select(range(6000))
검증 = 자료["validation"].shuffle(seed=0).select(range(3000))
print(학습[0]["title"], "→", 주제들[학습[0]["label"]])

# 2) 토큰화: 제목만 남기고 나머지 열은 버린다
이름 = "klue/bert-base"
토크나이저 = AutoTokenizer.from_pretrained(이름)


def 토큰화(묶음: dict) -> dict:
    return 토크나이저(묶음["title"], truncation=True, max_length=48)


열 = ["guid", "title", "url", "date"]
학습 = 학습.map(토큰화, batched=True, remove_columns=열).rename_column("label", "labels")
검증 = 검증.map(토큰화, batched=True, remove_columns=열).rename_column("label", "labels")
묶기 = DataCollatorWithPadding(토크나이저)
학습_로더 = DataLoader(학습, batch_size=32, shuffle=True, collate_fn=묶기,
                       generator=torch.Generator().manual_seed(0))
검증_로더 = DataLoader(검증, batch_size=128, collate_fn=묶기)

# 3) 모델: 주제 7개짜리 분류 머리를 붙인다
torch.manual_seed(0)
장치 = 장치_고르기()
모델 = AutoModelForSequenceClassification.from_pretrained(
    이름, num_labels=len(주제들), id2label=dict(enumerate(주제들)),
    label2id={t: i for i, t in enumerate(주제들)}).to(장치)

# 4) 학습: 13.9절과 같은 루프
에폭 = 2
옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=5e-5, weight_decay=0.01)
전체_걸음 = 에폭 * len(학습_로더)
스케줄러 = get_linear_schedule_with_warmup(옵티마이저, int(0.1 * 전체_걸음), 전체_걸음)
for 에폭_번호 in range(1, 에폭 + 1):
    모델.train()
    손실_합 = 0.0
    for 배치 in 학습_로더:
        배치 = {k: v.to(장치) for k, v in 배치.items()}
        출력 = 모델(**배치)
        출력.loss.backward()
        torch.nn.utils.clip_grad_norm_(모델.parameters(), 1.0)
        옵티마이저.step()
        스케줄러.step()
        옵티마이저.zero_grad()
        손실_합 += 출력.loss.item()
    print(f"에폭 {에폭_번호}: 학습 손실 {손실_합 / len(학습_로더):.4f}")

# 5) 평가: 주제별 정밀도·재현율·F1
모델.eval()
예측, 정답 = [], []
with torch.no_grad():
    for 배치 in 검증_로더:
        배치 = {k: v.to(장치) for k, v in 배치.items()}
        예측 += 모델(**배치).logits.argmax(-1).tolist()
        정답 += 배치["labels"].tolist()
print(classification_report(정답, 예측, target_names=주제들, digits=3))

# 6) 새 제목 넣어 보기 (예제용으로 지어낸 제목)
for 제목 in ["반도체 수출 석 달 연속 증가", "국가대표팀 월드컵 예선 첫 승",
             "주말 전국에 비 소식 기온 뚝", "새 스마트폰 인공지능 비서 탑재"]:
    입력 = 토크나이저(제목, return_tensors="pt").to(장치)
    with torch.no_grad():
        확률 = 모델(**입력).logits.softmax(-1)[0]
    print(f"{제목} → {주제들[확률.argmax()]} ({확률.max():.2f})")
