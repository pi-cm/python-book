# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.8 양자화 다시 보기: 눈금, 영점, 정수 계산 · manuscript-vol2/chapters/19-onnx-quantization.md:820]
import torch

torch.manual_seed(0)
a = torch.rand(4, 64) * 3                         # 입력(활성값): 0 이상
w = torch.randn(64, 8) * 0.1                      # 가중치: 0 근처, 양수와 음수


def 양자화(x: torch.Tensor, 작은: int, 큰: int) -> tuple[torch.Tensor, float, int]:
    """x의 범위를 정수 작은~큰 눈금에 맞춘다 (19.8절의 비대칭 방식)."""
    lo, hi = min(x.min().item(), 0.0), max(x.max().item(), 0.0)
    배율 = (hi - lo) / (큰 - 작은)
    영점 = round(작은 - lo / 배율)
    return (x / 배율 + 영점).round().clamp(작은, 큰).to(torch.int32), 배율, 영점


qa, sa, za = 양자화(a, 0, 255)                     # 입력은 uint8
qw, sw, zw = 양자화(w, -128, 127)                  # 가중치는 int8
# 정수끼리 곱해 int32에 모으고, 마지막에 한 번만 배율을 곱해 실수로 되돌린다
정수_누적 = (qa - za) @ (qw - zw)                  # int32 행렬 곱
결과 = 정수_누적.float() * (sa * sw)

정답 = a @ w
print("정수 누적값의 자료형:", 정수_누적.dtype, "최댓값:", 정수_누적.abs().max().item())
print("실수 행렬 곱 :", 정답[0, :4])
print("정수 행렬 곱 :", 결과[0, :4])
print(f"상대 오차: {((결과 - 정답).norm() / 정답.norm()).item():.4f}")
