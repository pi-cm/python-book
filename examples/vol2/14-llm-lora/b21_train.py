# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.9 실습: 1권 도우미로 미세조정하기 · manuscript-vol2/chapters/14-llm-lora.md:1144]
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from torch.nn.utils.rnn import pad_sequence

from 문답도우미 import 불러오기, 어댑터_경로, 예제_만들기
from 일권문답 import 학습_문답

torch.manual_seed(0)
토크나이저, 모델 = 불러오기()
설정 = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, task_type="CAUSAL_LM",
                  target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
모델 = get_peft_model(모델, 설정)
예제들 = [예제_만들기(토크나이저, 질문, 답) for 질문, 답 in 학습_문답]
print("가장 긴 예제:", max(len(입력) for 입력, _ in 예제들), "토큰")

옵티마이저 = torch.optim.AdamW([p for p in 모델.parameters() if p.requires_grad], lr=1e-3)
생성기 = torch.Generator().manual_seed(0)
배치_크기 = 8
for 에폭 in range(1, 9):
    모델.train()
    손실합 = 0.0
    순서 = torch.randperm(len(예제들), generator=생성기).tolist()
    for i in range(0, len(순서), 배치_크기):
        묶음 = [예제들[j] for j in 순서[i:i + 배치_크기]]
        # 7장 7.7절처럼 길이가 다른 예제를 채워서(padding) 묶는다
        입력 = pad_sequence([x for x, _ in 묶음], batch_first=True,
                            padding_value=토크나이저.pad_token_id)
        정답 = pad_sequence([y for _, y in 묶음], batch_first=True, padding_value=-100)
        마스크 = pad_sequence([torch.ones(len(x), dtype=torch.long) for x, _ in 묶음],
                              batch_first=True)
        손실 = 모델(input_ids=입력, attention_mask=마스크, labels=정답).loss
        옵티마이저.zero_grad()
        손실.backward()
        옵티마이저.step()
        손실합 += 손실.item() * len(묶음)
    print(f"에폭 {에폭}: 학습 손실 {손실합 / len(예제들):.3f}")

모델.save_pretrained(어댑터_경로)                       # LoRA 부분(A, B)만 저장된다
for 파일 in sorted(Path(어댑터_경로).iterdir()):
    print(f"{파일.name}: {파일.stat().st_size / 1024**2:.2f} MB")
