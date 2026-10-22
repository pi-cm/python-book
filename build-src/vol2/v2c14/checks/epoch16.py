"""14장 Q&A 보강용 확인 실험: b21과 같은 설정으로 에폭만 8→16으로 늘려 평가 지표를 잰다(원고 블록 아님)."""
import sys

import torch
from peft import LoraConfig, get_peft_model
from torch.nn.utils.rnn import pad_sequence

sys.path.insert(0, sys.argv[1])
from 문답도우미 import 불러오기, 예제_만들기, 평가  # noqa: E402
from 일권문답 import 시험_문답, 학습_문답  # noqa: E402

torch.manual_seed(0)
토크나이저, 모델 = 불러오기()
설정 = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, task_type="CAUSAL_LM",
                  target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
모델 = get_peft_model(모델, 설정)
예제들 = [예제_만들기(토크나이저, 질문, 답) for 질문, 답 in 학습_문답]
옵티마이저 = torch.optim.AdamW([p for p in 모델.parameters() if p.requires_grad], lr=1e-3)
생성기 = torch.Generator().manual_seed(0)
for 에폭 in range(1, 17):
    모델.train()
    순서 = torch.randperm(len(예제들), generator=생성기).tolist()
    for i in range(0, len(순서), 8):
        묶음 = [예제들[j] for j in 순서[i:i + 8]]
        입력 = pad_sequence([x for x, _ in 묶음], batch_first=True, padding_value=토크나이저.pad_token_id)
        정답 = pad_sequence([y for _, y in 묶음], batch_first=True, padding_value=-100)
        마스크 = pad_sequence([torch.ones(len(x), dtype=torch.long) for x, _ in 묶음], batch_first=True)
        손실 = 모델(input_ids=입력, attention_mask=마스크, labels=정답).loss
        옵티마이저.zero_grad(); 손실.backward(); 옵티마이저.step()
    if 에폭 in (8, 16):
        모델.eval()
        for 이름, 문답 in [("학습", 학습_문답), ("시험", 시험_문답)]:
            l, nl, acc = 평가(모델, 토크나이저, 문답)
            print(f"에폭 {에폭} {이름}: 답 손실 {l:.3f}, 장 번호 자리 손실 {nl:.3f}, 장 번호 맞힘 {acc:.0%}", flush=True)
