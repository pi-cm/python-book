import torch

torch.manual_seed(0)
# ReLU를 지난 값: 0 이상만 있다 (예제용으로 만든 0~6 사이 값)
활성값 = torch.rand(10_000) ** 2 * 6


def 대칭_int8(x: torch.Tensor) -> tuple[torch.Tensor, float]:
    """14장 14.6절 방식: 0을 가운데 두고 -127~127 눈금."""
    배율 = x.abs().max().item() / 127
    return (x / 배율).round().clamp(-127, 127), 배율


def 비대칭_uint8(x: torch.Tensor) -> tuple[torch.Tensor, float, int]:
    """최솟값~최댓값을 0~255 눈금에 맞추고, 실수 0이 놓일 눈금(영점)을 기억한다."""
    작은, 큰 = min(x.min().item(), 0.0), max(x.max().item(), 0.0)   # 실수 0은 꼭 범위 안에
    배율 = (큰 - 작은) / 255
    영점 = round(-작은 / 배율)
    return (x / 배율 + 영점).round().clamp(0, 255), 배율, 영점


정수, 배율 = 대칭_int8(활성값)
print(f"대칭 int8   : 배율 {배율:.5f}, 쓰인 눈금 {정수.unique().numel():3}개, "
      f"평균 오차 {(정수 * 배율 - 활성값).abs().mean():.5f}")
정수, 배율, 영점 = 비대칭_uint8(활성값)
print(f"비대칭 uint8: 배율 {배율:.5f}, 쓰인 눈금 {정수.unique().numel():3}개, "
      f"평균 오차 {((정수 - 영점) * 배율 - 활성값).abs().mean():.5f}, 영점 {영점}")

# 음수도 있는 값이라면 영점이 가운데쯤으로 온다
_, 배율, 영점 = 비대칭_uint8(torch.tensor([-1.0, 0.0, 3.0]))
print(f"-1~3 범위: 배율 {배율:.5f}, 영점 {영점} (실수 0 → 정수 {영점})")
