# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.9 사전학습 인코더 미세조정 · manuscript-vol2/chapters/13-korean-nlp.md:918]
import torch
from torch.utils.data import DataLoader
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          get_linear_schedule_with_warmup)

from 한국어도구 import NSMC_읽기


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


torch.manual_seed(0)
장치 = 장치_고르기()
이름 = "klue/bert-base"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForSequenceClassification.from_pretrained(
    이름, num_labels=2, id2label={0: "부정", 1: "긍정"}, label2id={"부정": 0, "긍정": 1}).to(장치)

학습 = NSMC_읽기("ratings_train.txt", 5000)
시험 = NSMC_읽기("ratings_test.txt", 5000)


def 묶기(배치: list[tuple[str, int]]) -> dict[str, torch.Tensor]:
    """토크나이저가 패딩·자르기·마스크를 한 번에 해 준다(7장 collate_fn의 역할)."""
    입력 = 토크나이저([s for s, _ in 배치], padding=True, truncation=True,
                     max_length=64, return_tensors="pt")
    입력["labels"] = torch.tensor([y for _, y in 배치])
    return 입력


학습_로더 = DataLoader(학습, batch_size=32, shuffle=True, collate_fn=묶기,
                       generator=torch.Generator().manual_seed(0))
시험_로더 = DataLoader(시험, batch_size=128, collate_fn=묶기)


def 정확도() -> float:
    모델.eval()
    맞음 = 0
    with torch.no_grad():
        for 배치 in 시험_로더:
            배치 = {k: v.to(장치) for k, v in 배치.items()}
            맞음 += (모델(**배치).logits.argmax(-1) == 배치["labels"]).sum().item()
    return 맞음 / len(시험)


에폭 = 2
옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=3e-5, weight_decay=0.01)
전체_걸음 = 에폭 * len(학습_로더)
스케줄러 = get_linear_schedule_with_warmup(옵티마이저, int(0.1 * 전체_걸음), 전체_걸음)

print(f"미세조정 전 시험 정확도: {정확도():.4f}")
for 에폭_번호 in range(1, 에폭 + 1):
    모델.train()
    손실_합 = 0.0
    for 배치 in 학습_로더:
        배치 = {k: v.to(장치) for k, v in 배치.items()}
        출력 = 모델(**배치)                     # labels를 함께 주면 손실까지 계산해 준다
        출력.loss.backward()
        torch.nn.utils.clip_grad_norm_(모델.parameters(), 1.0)
        옵티마이저.step()
        스케줄러.step()
        옵티마이저.zero_grad()
        손실_합 += 출력.loss.item()
    print(f"에폭 {에폭_번호}: 학습 손실 {손실_합 / len(학습_로더):.4f}, 시험 정확도 {정확도():.4f}")

모델.save_pretrained("data/감성모델")
토크나이저.save_pretrained("data/감성모델")
