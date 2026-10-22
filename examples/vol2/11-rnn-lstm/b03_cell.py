# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.2 RNN 셀: 메모장을 고쳐 쓰며 읽기 · manuscript-vol2/chapters/11-rnn-lstm.md:133]
import torch

torch.manual_seed(0)
입력_크기, 메모_크기 = 3, 4                  # 한 시점의 특성 3개, 메모장 칸 4개
W_x = torch.randn(입력_크기, 메모_크기) * 0.5   # 새로 읽은 것 → 메모
W_h = torch.randn(메모_크기, 메모_크기) * 0.5   # 지난 메모 → 새 메모
b = torch.zeros(메모_크기)


def rnn_셀(x: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
    """지금 읽은 x와 지난 메모 h로 새 메모를 쓴다."""
    return torch.tanh(x @ W_x + h @ W_h + b)


순서열 = torch.randn(2, 5, 입력_크기)      # (배치 2, 길이 5, 특성 3)
h = torch.zeros(2, 메모_크기)              # 처음에는 빈 메모장
메모들 = []
for t in range(순서열.shape[1]):           # 한 시점씩 차례로 읽는다
    h = rnn_셀(순서열[:, t], h)            # (2, 3)과 (2, 4) → (2, 4)
    메모들.append(h)
    print(f"t={t}: 첫 문장의 메모 {[round(v, 3) for v in h[0].tolist()]}")

출력 = torch.stack(메모들, dim=1)          # 시점마다의 메모를 모으면 (2, 5, 4)
print("모든 시점의 메모:", tuple(출력.shape), "마지막 메모:", tuple(h.shape))
