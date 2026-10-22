import torch
import torch.nn.functional as F
from torch.autograd import DeviceType
from torch.profiler import ProfilerActivity, profile, record_function
from torchvision.models import resnet18

torch.manual_seed(0)
모델 = resnet18(num_classes=10).to("cuda")
옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.01)
x = torch.randn(64, 3, 224, 224, device="cuda")
y = torch.randint(0, 10, (64,), device="cuda")


def 한_걸음() -> None:
    with record_function("순전파"):                    # 프로파일 기록에 이름표를 붙인다
        손실 = F.cross_entropy(모델(x), y)
    with record_function("역전파"):
        옵티마이저.zero_grad(set_to_none=True)
        손실.backward()
    with record_function("갱신"):
        옵티마이저.step()


for _ in range(3):                                     # 준비 운동은 기록하지 않는다
    한_걸음()
torch.cuda.synchronize()

with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as 기록:
    for _ in range(5):
        한_걸음()
    torch.cuda.synchronize()

이름표 = ("순전파", "역전파", "갱신")
# PyTorch 연산(aten::...)마다, 그 연산이 GPU에 맡긴 일의 시간을 모은다 (이름표 구간은 따로)
통계 = [e for e in 기록.key_averages() if e.device_type == DeviceType.CPU and e.key not in 이름표]
GPU_전체 = sum(e.self_device_time_total for e in 통계) / 1000
print(f"5걸음 동안 GPU가 일한 시간: {GPU_전체:.1f} ms")
for e in sorted(통계, key=lambda e: e.self_device_time_total, reverse=True)[:8]:
    ms = e.self_device_time_total / 1000
    print(f"{ms:7.2f} ms {ms / GPU_전체:6.1%} {e.count:4}번  {e.key[:48]}")
for e in 기록.key_averages():
    if e.key in 이름표 and e.device_type == DeviceType.CPU:    # 파이썬 쪽에서 걸린 시간
        print(f"이름표 '{e.key}': CPU에서 {e.cpu_time_total / 1000:5.1f} ms")
