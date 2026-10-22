# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.4 GPU 메모리 들여다보기 · manuscript-vol2/chapters/16-gpu-performance.md:403]
import torch
import torch.nn.functional as F
from torchvision.models import resnet18

GB = 1024 ** 3
모델 = resnet18(num_classes=10).to("cuda")


def 한_걸음(배치: int) -> None:
    """배치 크기만큼 가짜 사진을 만들어 순전파·역전파를 한 번 한다."""
    x = torch.randn(배치, 3, 224, 224, device="cuda")
    y = torch.randint(0, 10, (배치,), device="cuda")
    F.cross_entropy(모델(x), y).backward()
    모델.zero_grad(set_to_none=True)


배치, 성공한_배치 = 64, None
while True:
    try:
        torch.cuda.reset_peak_memory_stats()
        한_걸음(배치)
        print(f"배치 {배치:>5}: 성공, 최고 {torch.cuda.max_memory_allocated() / GB:5.1f} GB")
        성공한_배치 = 배치
        배치 *= 2
    except torch.OutOfMemoryError as 오류:              # GPU 메모리가 모자랄 때 나는 오류
        print(f"배치 {배치:>5}: 메모리 부족!")
        print("   ", ". ".join(str(오류).split(". ")[:3]) + ".")   # 메시지의 앞 세 문장
        break

torch.cuda.empty_cache()                                # 실패한 걸음이 잡아 둔 자리 정리
print(f"예약 메모리 정리 뒤: {torch.cuda.memory_reserved() / GB:.1f} GB")
한_걸음(성공한_배치)                                    # 정리하고 나면 다시 계속할 수 있다
print(f"배치 {성공한_배치}로 다시 학습: 문제없음")
