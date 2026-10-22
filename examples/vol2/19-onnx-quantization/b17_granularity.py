# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.8 양자화 다시 보기: 눈금, 영점, 정수 계산 · manuscript-vol2/chapters/19-onnx-quantization.md:864]
import torch

from 배포도구 import 불러오기, 옷CNN


def 왕복(w: torch.Tensor, 비트: int, 묶음: str) -> tuple[torch.Tensor, int]:
    """대칭 양자화했다가 되돌린 값과, 그때 쓴 배율의 개수."""
    최대 = 2 ** (비트 - 1) - 1
    if 묶음 == "텐서마다":
        조각 = w.reshape(1, -1)                     # 텐서 전체에 배율 하나
    elif 묶음 == "채널마다":
        조각 = w.reshape(w.shape[0], -1)            # 출력 채널(행)마다 하나
    else:
        조각 = w.reshape(-1, 32)                    # 숫자 32개마다 하나
    배율 = 조각.abs().amax(dim=1, keepdim=True) / 최대
    되돌림 = (조각 / 배율).round().clamp(-최대, 최대) * 배율
    return 되돌림.reshape(w.shape), 배율.numel()


모델 = 불러오기(옷CNN, "fashion_cnn.pt")
for 이름, w in [("합성곱 2층 (64, 32, 3, 3)", 모델.특징[3].weight.detach()),
                ("완전 연결 (128, 3136)", 모델.분류[1].weight.detach())]:
    print(이름)
    for 묶음 in ["텐서마다", "채널마다", "32개씩"]:
        오차 = []
        for 비트 in (8, 4):
            되돌림, 개수 = 왕복(w, 비트, 묶음)
            오차.append(((되돌림 - w).norm() / w.norm()).item())   # 상대 오차
        print(f"  {묶음:5} 배율 {개수:>6,}개   int8 오차 {오차[0]:.4f}   int4 오차 {오차[1]:.4f}")
