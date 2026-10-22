# Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기

> **학습 목표**  
> - 학습 중 GPU 메모리가 파라미터·기울기·옵티마이저 상태·활성화에 얼마씩 쓰이는지 재고 계산하기
> - 그래디언트 누적과 활성화 체크포인팅으로 GPU 하나에서 메모리 부족을 먼저 해결하기
> - 프로세스·rank·world size·all-reduce의 뜻을 알고 `torchrun`으로 여러 프로세스를 띄우기
> - `DistributedDataParallel`로 학습 코드를 여러 GPU용으로 바꾸고, 1 GPU와 같은 결과가 나오는지 확인하기
> - GPU 사이 통신 비용을 재고, 모델과 배치 크기에 따라 GPU를 늘린 이득이 달라지는 이유를 설명하기
> - FSDP·텐서 병렬·파이프라인 병렬이 무엇이고 언제 쓰는지 알고, 분산 학습의 흔한 오류를 피하기

---

## 들어가며: 이삿짐을 혼자 옮길까, 친구를 부를까?

이사 날을 떠올려 보세요. 짐이 많으면 방법은 두 가지입니다. 한 번에 드는 양을 줄여서 **여러 번 나르거나**, 친구를 불러 **여럿이 나눠 나르거나**요. 그런데 친구를 부르면 공짜로 빨라질까요? 아닙니다. 누가 어느 상자를 들지 정해야 하고, 다 나른 뒤에는 "다 옮겼어?" 하고 서로 확인해야 해요. 엘리베이터가 하나뿐인 아파트라면 친구가 셋이어도 엘리베이터 앞에서 줄을 서게 됩니다.

딥러닝 학습도 똑같습니다. 15장의 확산 모델처럼 모델이 조금만 커져도 GPU 메모리가 모자라거나 시간이 너무 오래 걸리죠. 16장에서 GPU 하나를 최대한 빠르게 쓰는 법을 봤다면, 이 장은 그다음 두 질문을 다룹니다.

- **GPU 메모리가 모자라면?** 먼저 GPU 하나에서 할 수 있는 일부터 합니다. 메모리가 어디에 쓰이는지 재 보고, 한 번에 드는 양을 줄여 여러 번 나르고(그래디언트 누적), 기억해 둘 것을 줄이고 필요할 때 다시 계산합니다(활성화 체크포인팅).
- **GPU를 여러 개 쓰면?** 친구를 부르는 방법입니다. 데이터를 나눠 맡기고(DDP), 그래도 모델이 안 들어가면 모델까지 나눠 맡깁니다(FSDP). 그리고 "서로 확인하는 시간", 즉 **통신 비용**이 얼마인지 직접 잽니다.

이 장의 예제는 지금까지와 달리 **NVIDIA GPU 두 장이 달린 리눅스 서버**에서 실행했습니다. RTX 4090(메모리 24GB) 두 장인데, 두 GPU를 잇는 전용 다리(NVLink)가 없어서 데이터를 주고받으려면 메인보드의 PCIe 통로와 CPU를 거쳐야 해요. 게다가 두 번째 GPU는 통로가 좁은 자리(PCIe 3세대 4차선)에 꽂혀 있습니다. 비싼 서버가 아니라 연구실이나 집에서 흔히 보는 구성이죠. 그래서 이 장의 숫자는 "GPU를 늘리면 무조건 빨라진다"는 기대가 어디서 깨지는지를 솔직하게 보여 줍니다.

> **Q. GPU가 없거나 하나뿐이면 이 장을 못 따라 하나요?**
> 반은 따라 할 수 있습니다. 17.2절의 누적이 큰 배치와 같은지 확인하는 예제와 17.5절의 첫 통신 예제, 17.12절의 멈춤 예제, 17.13절 실습은 CPU에서도 돌아가요. 이 책의 맥에서 확인해 보니 맥용 PyTorch에는 NVIDIA용 통신 라이브러리(NCCL)가 없지만, CPU끼리 통신하는 `gloo`로 프로세스 두 개를 띄워 DDP 학습까지 돌아갔습니다. 메모리를 재는 예제와 처리량 비교는 NVIDIA GPU가 있어야 하니, 숫자는 본문의 출력으로 읽어 주세요. GPU 한 장짜리 환경은 부록 A.5절의 Colab으로 빌릴 수 있습니다. 이 장의 예제는 파이썬 3.12, PyTorch 2.14.1(CUDA 12.6용 빌드), torchvision 0.29.1에서 실행해 확인했어요.

## 17.1 학습 중 GPU 메모리는 어디에 쓰일까

### 네 가지 손님

14장 14.6절에서 "모델이 내 노트북에 들어갈까?"를 계산했습니다. 파라미터 수 × 칸 크기였죠. 그런데 그건 **추론**, 즉 모델을 쓰기만 할 때의 이야기예요. 학습할 때는 GPU 메모리에 손님이 넷으로 늘어납니다.

- **파라미터**: 모델의 숫자 그 자체
- **기울기**: `backward()`가 파라미터마다 하나씩 만드는 `.grad` (5장)
- **옵티마이저 상태**: Adam이 파라미터마다 기억해 두는 값 (6장 6.6절)
- **활성화**: forward 동안 층마다 저장해 두는 중간 결과. backward가 기울기를 계산할 때 다시 꺼내 씁니다(5장 5.6절의 연쇄 법칙)

말로만 들으면 감이 안 오니, 선형층 8개짜리 모델로 학습 한 걸음 한 걸음마다 메모리를 재 보겠습니다. `torch.cuda.memory_allocated()`는 지금 텐서들이 차지한 GPU 메모리입니다. 메모리를 재는 도구 자체는 16장 16.4절에서 자세히 다뤘으니, 여기서는 **무엇이 메모리를 차지하는지**에 집중할게요.

```python
import torch
from torch import nn

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 있어야 합니다"
장치 = torch.device("cuda")
MB = 1024 ** 2


def 찍기(시점: str) -> None:
    """지금 텐서들이 차지한 GPU 메모리를 MB로 보여 준다."""
    print(f"{시점:>16}: {torch.cuda.memory_allocated() / MB:6,.0f} MB")


torch.manual_seed(0)
# 4096 → 4096 선형층 8개: 파라미터 약 1억 3천만 개
모델 = nn.Sequential(*[nn.Sequential(nn.Linear(4096, 4096), nn.ReLU()) for _ in range(8)]).to(장치)
개수 = sum(p.numel() for p in 모델.parameters())
print(f"파라미터 {개수:,}개 × 4바이트 = {개수 * 4 / MB:,.0f} MB")

옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-4)
x = torch.randn(2048, 4096, device=장치)          # 입력 2048개 묶음 (32MB)
찍기("모델·입력 올린 뒤")
for 번째 in (1, 2):
    torch.cuda.reset_peak_memory_stats()
    손실 = 모델(x).pow(2).mean()
    찍기(f"{번째}회 forward 뒤")       # 활성화가 쌓였다
    손실.backward()
    찍기(f"{번째}회 backward 뒤")      # 활성화는 풀리고 기울기가 생겼다
    옵티마이저.step()
    찍기(f"{번째}회 step 뒤")          # 첫 step에서 Adam 상태가 생긴다
    옵티마이저.zero_grad()
    찍기(f"{번째}회 zero_grad 뒤")     # 기울기를 None으로 비운다
    print(f"{f'{번째}회 중 최고':>16}: {torch.cuda.max_memory_allocated() / MB:6,.0f} MB")

상태 = 옵티마이저.state[모델[0][0].weight]
print("Adam이 가중치마다 기억하는 것:", [k for k, v in 상태.items() if v.numel() > 1])
```

```text
파라미터 134,250,496개 × 4바이트 = 512 MB
      모델·입력 올린 뒤:    544 MB
    1회 forward 뒤:    808 MB
   1회 backward 뒤:  1,073 MB
       1회 step 뒤:  2,097 MB
  1회 zero_grad 뒤:  1,585 MB
         1회 중 최고:  2,609 MB
    2회 forward 뒤:  1,841 MB
   2회 backward 뒤:  2,097 MB
       2회 step 뒤:  2,097 MB
  2회 zero_grad 뒤:  1,585 MB
         2회 중 최고:  2,609 MB
Adam이 가중치마다 기억하는 것: ['exp_avg', 'exp_avg_sq']
```

이 책의 실행 환경(RTX 4090)에서 잰 값입니다. 숫자를 위에서부터 따라가 보세요.

- **모델·입력 올린 뒤 544MB**: 파라미터 1억 3천만 개 × 4바이트 = 512MB에 입력 32MB를 더한 값입니다.
- **1회 forward 뒤 808MB**: 264MB가 늘었어요. 층마다 backward 때 쓸 중간 결과를 저장해 둔 **활성화**입니다. 입력 2048개 × 4096칸짜리 텐서(32MB)가 층마다 쌓인 거예요.
- **1회 backward 뒤 1,073MB**: 활성화는 다 쓰고 풀렸지만, 파라미터와 같은 크기의 **기울기** 512MB가 새로 생겼습니다.
- **1회 step 뒤 2,097MB**: 1,024MB가 늘었습니다. 마지막 줄에 보이는 `exp_avg`와 `exp_avg_sq`, 즉 Adam이 파라미터마다 기억하는 두 값(기울기의 이동 평균과 제곱의 이동 평균)이 **처음 step 할 때** 만들어졌어요. 파라미터 크기의 두 배입니다.
- **zero_grad 뒤 1,585MB**: `zero_grad()`는 기본으로 기울기를 0으로 채우는 대신 `None`으로 **버려서** 512MB를 돌려줍니다.

두 번째 걸음부터는 같은 일이 반복돼요. forward로 활성화가 쌓였다(1,841MB) 풀리고, 기울기가 생겼다(2,097MB) 버려집니다. 그리고 두 번 다 **최고 2,609MB**를 찍었는데, 이건 `step()` 안에서 Adam이 계산하느라 잠깐 쓰는 임시 공간까지 더한 값입니다. GPU 메모리가 모자라다는 오류는 평균이 아니라 이 **가장 높은 순간**에 납니다.

정리하면, Adam으로 학습할 때 활성화를 빼고도 **파라미터의 4배**(파라미터 1 + 기울기 1 + Adam 상태 2)가 늘 자리를 차지합니다. 512MB짜리 모델이 2GB를 쓰는 거예요.

### 7B 모델을 학습하려면

14장 14.6절의 표를 학습용으로 다시 계산해 보겠습니다. 파라미터 하나당 몇 바이트가 드는지만 바꾸면 됩니다.

```python
GB = 1024 ** 3
# 파라미터 하나당 바이트 수 (float32로 학습할 때)
내역 = {"파라미터": 4, "기울기": 4, "Adam 1차 모멘트": 4, "Adam 2차 모멘트": 4}
학습_바이트 = sum(내역.values())
print(" + ".join(f"{k} {v}" for k, v in 내역.items()), f"= 파라미터당 {학습_바이트}바이트")

for 이름, 개수 in [("0.5B", 494_032_768), ("1B", 1_000_000_000), ("7B", 7_000_000_000)]:
    print(f"{이름:>4}: 추론(bfloat16) {개수 * 2 / GB:5.1f}GB, "
          f"학습(float32+Adam) {개수 * 학습_바이트 / GB:6.1f}GB, "
          f"학습(float32+SGD) {개수 * 8 / GB:5.1f}GB")
print("활성화는 따로: 배치 크기와 입력 길이에 비례해서 더 든다")
```

```text
파라미터 4 + 기울기 4 + Adam 1차 모멘트 4 + Adam 2차 모멘트 4 = 파라미터당 16바이트
0.5B: 추론(bfloat16)   0.9GB, 학습(float32+Adam)    7.4GB, 학습(float32+SGD)   3.7GB
  1B: 추론(bfloat16)   1.9GB, 학습(float32+Adam)   14.9GB, 학습(float32+SGD)   7.5GB
  7B: 추론(bfloat16)  13.0GB, 학습(float32+Adam)  104.3GB, 학습(float32+SGD)  52.2GB
활성화는 따로: 배치 크기와 입력 길이에 비례해서 더 든다
```

`bfloat16`으로 쓰기만 하면 13GB인 7B 모델이, `float32`와 Adam으로 학습하려면 **104GB**가 필요합니다. 24GB짜리 GPU 네 장을 붙여도 활성화를 넣을 자리가 없어요. 모멘텀 없는 SGD라면 옵티마이저 상태가 없어서 절반인 52GB입니다. 옵티마이저 하나만 바꿔도 메모리가 두 배 차이 나는 셈이에요.

실제 대형 모델 학습은 16장 16.6절의 혼합 정밀도로 계산을 16비트로 하고, 이 장 뒤에서 볼 FSDP로 이 104GB를 여러 GPU에 나눠 담고, 14장의 LoRA처럼 고칠 파라미터 자체를 줄이는 방법을 함께 씁니다. 그 전에 먼저 GPU 하나에서 할 수 있는 일부터 보겠습니다.

## 17.2 그래디언트 누적: 큰 배치를 나눠 담기

### 장바구니에 담아 두었다가 한 번에 계산하기

마트에서 물건을 하나 집을 때마다 계산대로 가지는 않죠. 장바구니에 담아 두었다가 다 고른 뒤 한 번에 계산합니다. **그래디언트 누적(gradient accumulation)** 이 이 방법이에요. 배치 256장이 메모리에 안 들어가면 64장씩 네 번 forward와 backward를 하면서 기울기를 장바구니(`.grad`)에 쌓고, 네 번째가 끝난 뒤에 한 번만 `step()`으로 고칩니다.

5장 5.7절에서 `backward()`는 기울기를 덮어쓰지 않고 **더한다**고 했고, 그때 "이 성질 덕분에 그래디언트 누적이 가능하다"고 예고했어요. 정말 큰 배치와 같은 결과가 나오는지 숫자로 확인해 보겠습니다. 이 예제는 CPU에서 돌아가니 어떤 컴퓨터에서든 같은 결과를 볼 수 있어요.

```python
import torch
from torch import nn

torch.manual_seed(0)
X = torch.randn(64, 10)                 # 예제용으로 만든 데이터 64개
y = torch.randn(64, 1)
손실함수 = nn.MSELoss()


def 새_모델() -> nn.Module:
    """매번 똑같은 초깃값으로 시작하는 작은 모델."""
    torch.manual_seed(1)
    return nn.Sequential(nn.Linear(10, 32), nn.ReLU(), nn.Linear(32, 1))


def 기울기_모으기(모델: nn.Module, 단계: int, 나누기: bool = True) -> None:
    """64개를 단계 수만큼 나눠 forward/backward하고 기울기를 .grad에 쌓는다."""
    for xb, yb in zip(X.chunk(단계), y.chunk(단계)):
        손실 = 손실함수(모델(xb), yb)
        (손실 / 단계 if 나누기 else 손실).backward()


큰배치 = 새_모델()
기울기_모으기(큰배치, 단계=1)            # 64개를 한 번에
누적 = 새_모델()
기울기_모으기(누적, 단계=4)              # 16개씩 네 번
잊음 = 새_모델()
기울기_모으기(잊음, 단계=4, 나누기=False)  # 손실을 4로 나누는 것을 잊으면

차이 = max((a.grad - b.grad).abs().max().item()
         for a, b in zip(큰배치.parameters(), 누적.parameters()))
print(f"64개 한 번 vs 16개×4번 누적: 기울기 최대 차이 {차이:.1e}")
print(f"나누기를 잊으면 기울기가 {(잊음[0].weight.grad / 큰배치[0].weight.grad).mean():.2f}배")


def 학습(단계: int) -> list[float]:
    """같은 64개로 다섯 걸음 학습하고, 걸음마다 전체 손실을 기록한다."""
    모델 = 새_모델()
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.1)
    기록 = []
    for _ in range(5):
        옵티마이저.zero_grad()
        기울기_모으기(모델, 단계)
        옵티마이저.step()                   # 누적이 끝난 뒤에 한 번만 고친다
        with torch.no_grad():
            기록.append(round(손실함수(모델(X), y).item(), 6))
    return 기록


for 단계 in (1, 4, 8):
    print(f"{64 // 단계:2}개씩 {단계}번 누적:", 학습(단계))
```

```text
64개 한 번 vs 16개×4번 누적: 기울기 최대 차이 4.5e-08
나누기를 잊으면 기울기가 4.00배
64개씩 1번 누적: [1.152792, 1.109052, 1.072198, 1.040522, 1.012927]
16개씩 4번 누적: [1.152792, 1.109052, 1.072198, 1.040522, 1.012927]
 8개씩 8번 누적: [1.152792, 1.109052, 1.072198, 1.040522, 1.012927]
```

64개를 한 번에 넣은 기울기와 16개씩 네 번 나눠 쌓은 기울기의 차이가 4.5e-08, 즉 0.00000005 수준입니다. 4장 4.3절에서 본 `float32`의 끝자리 오차일 뿐 사실상 같아요. 다섯 걸음 학습한 손실도 64개씩, 16개씩 4번, 8개씩 8번 모두 소수점 여섯째 자리까지 똑같습니다.

핵심은 `손실 / 단계`입니다. `MSELoss`와 `CrossEntropyLoss`는 기본으로 배치의 **평균**을 내요. 16개짜리 평균 네 개를 그냥 더하면 64개짜리 평균의 4배가 되죠. 두 번째 줄처럼 나누기를 잊으면 기울기가 정확히 4.00배가 됩니다. 학습률을 4배로 올린 것과 같아서 학습이 불안정해져요. 누적할 때는 **손실을 누적 횟수로 나누고, step과 zero_grad는 누적이 끝난 뒤에 한 번만** 한다는 두 가지를 기억하세요.

> **Q. 누적하면 언제나 큰 배치와 똑같나요?**
> 아닙니다. 배치 안의 샘플끼리 섞이는 계산이 있으면 달라져요. 대표적인 것이 8장 8.4절의 **배치 정규화**입니다. 배치의 평균과 분산으로 표준화하니, 샘플 64개의 평균과 샘플 16개의 평균은 다르죠. 그래서 배치 정규화가 있는 모델에서 누적은 "큰 배치와 거의 비슷한" 결과를 냅니다. 또 8장 8.9절의 그래디언트 클리핑은 누적이 **끝난 뒤**, `step()` 바로 앞에서 해야 합니다. 중간에 자르면 일부 조각의 기울기만 잘려요.

### 메모리는 줄고, 시간은?

이번에는 GPU에서 실제로 메모리가 얼마나 줄고 시간은 얼마나 드는지 재 보겠습니다. 10장의 ResNet18에 224 × 224 사진 256장(예제용 난수 입력)을 넣고, 1번에서 16번까지 나눠 담아 봅니다.

```python
import statistics
import time

import torch
from torch import nn
from torchvision.models import resnet18

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 있어야 합니다"
장치 = torch.device("cuda")
GB = 1024 ** 3

torch.manual_seed(0)
모델 = resnet18(num_classes=10).to(장치)
옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.01, momentum=0.9)
손실함수 = nn.CrossEntropyLoss()
X = torch.randn(256, 3, 224, 224, device=장치)   # 예제용 입력: 224×224 사진 256장
y = torch.randint(0, 10, (256,), device=장치)


def 한_걸음(단계: int) -> None:
    """256장을 단계 수만큼 나눠 기울기를 누적한 뒤 한 번 고친다."""
    옵티마이저.zero_grad()
    for xb, yb in zip(X.chunk(단계), y.chunk(단계)):
        (손실함수(모델(xb), yb) / 단계).backward()
    옵티마이저.step()


for 단계 in (1, 2, 4, 8, 16):
    한_걸음(단계)                                 # 준비 운동
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    시간들 = []
    for _ in range(5):
        시작 = time.perf_counter()
        한_걸음(단계)
        torch.cuda.synchronize()                  # GPU 일이 끝날 때까지 기다린 뒤 잰다
        시간들.append(time.perf_counter() - 시작)
    print(f"{256 // 단계:3}장 × {단계:2}번: 최고 메모리 {torch.cuda.max_memory_allocated() / GB:5.2f} GB, "
          f"256장 한 걸음 {statistics.median(시간들) * 1000:5.0f} ms")
```

```text
256장 ×  1번: 최고 메모리  5.48 GB, 256장 한 걸음   108 ms
128장 ×  2번: 최고 메모리  2.92 GB, 256장 한 걸음   104 ms
 64장 ×  4번: 최고 메모리  1.61 GB, 256장 한 걸음    99 ms
 32장 ×  8번: 최고 메모리  0.96 GB, 256장 한 걸음    97 ms
 16장 × 16번: 최고 메모리  0.64 GB, 256장 한 걸음   101 ms
```

나누는 횟수를 두 배로 늘릴 때마다 최고 메모리가 거의 절반씩 줄어서, 한 번에 넣으면 5.48GB이던 것이 16번에 나누면 0.64GB가 됩니다. 메모리의 대부분이 배치 크기에 비례하는 **활성화**였다는 뜻이에요. 0.64GB 아래로는 잘 안 내려가는데, 그 바닥에는 세 가지가 남아 있어요. 조각 크기와 상관없이 GPU에 올려 둔 입력 256장(약 0.14GB), 파라미터·기울기·모멘텀(합쳐서 약 0.13GB), 그리고 16장짜리 조각 하나의 활성화(16장 16.4절에서 잰 대로 약 0.33GB)입니다. 바닥의 절반 넘게가 여전히 활성화라서, 조각을 더 잘게 나누면 조금 더 내려가지만 GPU가 노는 시간이 늘어나요.

시간은 어떨까요? 256장을 한 걸음 처리하는 데 97~108ms로 거의 그대로입니다. 이 책의 GPU에서는 ResNet18이 사진 16장만 받아도 GPU를 충분히 바쁘게 만들 만큼 계산이 크기 때문이에요. 모델이 작거나 나눈 조각이 너무 작으면 GPU가 놀아서 느려지니(16장 16.11절의 배치 크기와 처리량), "메모리에 들어가는 가장 큰 조각"으로 나누는 것이 요령입니다.

## 17.3 활성화 체크포인팅: 적어 두지 말고 다시 계산하기

### 시험 공부 노트 대신 풀이를 다시 하기

17.1절에서 활성화가 배치 크기에 비례해 커진다고 했습니다. 트랜스포머처럼 층이 깊고 입력이 길면 활성화가 파라미터보다 훨씬 커져요. 12장 12.9절에서 어텐션 가중치 표가 글자 수의 제곱으로 커지던 것 기억하시죠?

**활성화 체크포인팅(activation checkpointing)** 은 수학 문제를 풀 때 중간 계산을 모두 적어 두는 대신, 중요한 지점(층의 입력)만 적어 두고 나중에 필요해지면 그 지점부터 **다시 풀어 보는** 방법입니다. forward 때는 층의 입력만 저장하고 중간 결과는 버렸다가, backward가 그 층에 도착하면 forward를 한 번 더 해서 중간 결과를 되살려요. 메모리를 아끼는 대신 계산을 더 하는 거죠. 12장의 인코더 층을 12개 쌓은 모델로 재 보겠습니다.

```python
import statistics
import time

import torch
from torch import nn
from torch.utils.checkpoint import checkpoint

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 있어야 합니다"
장치 = torch.device("cuda")
GB = 1024 ** 3


class 트랜스포머(nn.Module):
    """12장의 인코더 층을 쌓은 모델. 체크포인트=True면 층마다 활성화를 버리고 다시 계산한다."""

    def __init__(self, 층수: int, 체크포인트: bool) -> None:
        super().__init__()
        self.층들 = nn.ModuleList(
            nn.TransformerEncoderLayer(1024, 16, 4096, dropout=0.1, batch_first=True)
            for _ in range(층수))
        self.체크포인트 = 체크포인트

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for 층 in self.층들:
            if self.체크포인트 and self.training:
                x = checkpoint(층, x, use_reentrant=False)   # 층의 중간 결과를 저장하지 않는다
            else:
                x = 층(x)
        return x


x = torch.randn(16, 512, 1024, device=장치)       # 예제용 입력: 16문장 × 512토큰
결과 = {}
for 체크포인트 in (False, True):
    torch.manual_seed(0)
    모델 = 트랜스포머(12, 체크포인트).to(장치)
    시간들 = []
    for 번째 in range(6):
        모델.zero_grad()
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        시작 = time.perf_counter()
        torch.manual_seed(번째)                       # 드롭아웃 난수를 두 방식에서 똑같이
        모델(x).pow(2).mean().backward()
        torch.cuda.synchronize()
        시간들.append(time.perf_counter() - 시작)
    결과[체크포인트] = [p.grad.clone() for p in 모델.parameters()]
    개수 = sum(p.numel() for p in 모델.parameters())
    print(f"체크포인팅 {'켬' if 체크포인트 else '끔'}: 최고 메모리 "
          f"{torch.cuda.max_memory_allocated() / GB:5.2f} GB, "
          f"forward+backward {statistics.median(시간들[1:]) * 1000:4.0f} ms")
    del 모델

print(f"파라미터 {개수:,}개 (float32로 {개수 * 4 / GB:.2f} GB)")
같은가 = all(torch.allclose(a, b, atol=1e-6) for a, b in zip(결과[False], 결과[True]))
print("두 방식의 기울기가 같은가:", 같은가)
```

```text
체크포인팅 끔: 최고 메모리  7.78 GB, forward+backward  241 ms
체크포인팅 켬: 최고 메모리  2.43 GB, forward+backward  322 ms
파라미터 151,154,688개 (float32로 0.56 GB)
두 방식의 기울기가 같은가: True
```

체크포인팅을 켜니 최고 메모리가 7.78GB에서 2.43GB로 3분의 1 아래로 줄었습니다. 대신 forward+backward 시간은 241ms에서 322ms로 약 34% 늘었어요. forward를 사실상 두 번 하니 그만큼 느려진 겁니다. 이 책의 실행 환경에서 잰 값이라 숫자는 조금씩 다를 수 있지만, "메모리를 크게 줄이고 시간을 조금 더 낸다"는 거래 관계는 어디서나 같습니다.

마지막 줄도 중요합니다. 두 방식의 기울기가 **같아요.** 드롭아웃처럼 난수를 쓰는 층이 있어도, `checkpoint`는 처음 forward 때의 난수 상태를 기억했다가 다시 계산할 때 되돌려 놓기 때문입니다. 결과는 그대로이고 메모리와 시간만 바꾼 거죠.

쓰는 법은 한 줄입니다. `x = 층(x)` 대신 `x = checkpoint(층, x, use_reentrant=False)`라고 쓰면 그 층이 체크포인트 구간이 돼요. `use_reentrant=False`는 PyTorch가 권하는 새 방식이라 명시해 두는 것이 좋습니다. Hugging Face 모델은 `model.gradient_checkpointing_enable()` 한 줄로 같은 일을 해 줍니다.

| 방법 | 줄어드는 것 | 대가 | 결과 |
|---|---|---|---|
| 그래디언트 누적 | 활성화 (배치를 나눠서) | 거의 없음 (조각이 너무 작으면 느려짐) | 큰 배치와 같음 (배치 정규화 제외) |
| 활성화 체크포인팅 | 활성화 (저장하지 않고 다시 계산) | forward 한 번 더 (이 예제에서 +34%) | 같음 |
| 옵티마이저 바꾸기 (Adam → SGD) | 옵티마이저 상태 | 학습이 느리거나 불안정할 수 있음 | 달라짐 |
| 16비트 계산 (16장 16.6절) | 활성화·계산 시간 | 정밀도 관리 | 거의 같음 |

## 17.4 여러 GPU에 일을 나누는 방법들

GPU 하나로 할 수 있는 일을 다 했는데도 모자라면 이제 친구를 부를 차례입니다. 나누는 방법은 크게 두 갈래예요. 식당 주방으로 비유해 보겠습니다.

- **데이터 병렬(data parallel)**: 같은 레시피를 가진 요리사 여럿이 **손님을 나눠 받습니다.** 요리사마다 모델 전체를 갖고 데이터만 나눠 맡아요. 각자 계산한 기울기를 마지막에 평균 내서 모두 같은 방향으로 고칩니다. 가장 쉽고 가장 많이 씁니다.
- **모델 병렬(model parallel)**: 요리 하나를 **공정별로 나눠** 맡습니다. 한 사람은 재료 손질, 한 사람은 굽기, 한 사람은 담기처럼요. 모델이 GPU 하나에 아예 안 들어갈 때 씁니다.

| 방법 | 나누는 것 | GPU마다 가진 것 | 언제 쓰나 |
|---|---|---|---|
| DDP (17.7절) | 데이터 | 모델 전체 | 모델이 GPU 하나에 들어갈 때. 가장 먼저 시도 |
| FSDP·ZeRO (17.11절) | 데이터 + 파라미터·기울기·옵티마이저 상태 | 모델의 일부 조각 | 학습 메모리(17.1절의 4배)가 GPU 하나를 넘을 때 |
| 텐서 병렬 | 층 안의 행렬을 쪼갬 | 행렬의 일부 | 아주 큰 층. GPU끼리 빠른 연결(NVLink)이 있을 때 |
| 파이프라인 병렬 | 층을 순서대로 나눔 | 앞쪽 층, 뒤쪽 층 | 아주 깊은 모델. 여러 서버에 걸칠 때 |

이 장에서는 DDP를 중심으로 직접 돌려 보고, FSDP는 짧게 맛만 봅니다. 텐서 병렬과 파이프라인 병렬은 수백 장의 GPU로 거대 모델을 학습하는 곳의 기술이라 개념만 알아 두면 충분해요.

## 17.5 분산의 기본 낱말: 프로세스, rank, all-reduce

### GPU마다 프로세스 하나

PyTorch의 분산 학습은 **GPU 하나에 프로세스(실행 중인 파이썬 프로그램) 하나**를 띄우는 방식입니다. 1권 17장에서 `ProcessPoolExecutor`로 계산을 여러 프로세스에 나눴던 것과 비슷해요. 다만 이번에는 프로세스들이 같은 코드를 동시에 실행하면서, 정해진 순간에 서로 숫자를 주고받습니다. 이때 쓰는 낱말 몇 개만 알면 됩니다.

| 낱말 | 뜻 | 이 장의 서버에서 |
|---|---|---|
| world size | 함께 일하는 프로세스의 수 | 2 |
| rank | 프로세스마다 붙은 번호 (0부터) | 0, 1 |
| local rank | 그 컴퓨터 안에서의 번호. 몇 번 GPU를 쓸지 정할 때 쓴다 | 0, 1 |
| 백엔드 | 통신을 맡는 라이브러리. NVIDIA GPU는 `nccl`, CPU는 `gloo` | `nccl` |
| all-reduce | 모두의 값을 모아 합(또는 평균)을 내서 **모두에게** 돌려주는 통신 | |

여기서 가장 중요한 것이 **all-reduce**입니다. 요리사 둘이 각자 맛을 본 점수를 불러 주고, 둘 다 합계를 받아 적는 것과 같아요. DDP가 기울기를 평균 낼 때 쓰는 통신이 바로 이것입니다. 직접 해 보겠습니다. 아래 코드를 `b06_첫_allreduce.py`로 저장하세요. 이 장의 분산 예제는 모두 이렇게 파일로 저장한 뒤, 아래 명령의 파일 이름만 바꿔서 실행합니다.

```python
import os
from datetime import timedelta

import torch
import torch.distributed as dist


def 분산_시작() -> torch.device:
    """torchrun이 넣어 준 환경 변수로 프로세스 그룹에 들어간다."""
    if torch.cuda.is_available():
        장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))  # 프로세스마다 GPU 하나
        torch.cuda.set_device(장치)
        dist.init_process_group("nccl", timeout=timedelta(seconds=60), device_id=장치)
    else:
        장치 = torch.device("cpu")                                  # GPU가 없으면 CPU끼리
        dist.init_process_group("gloo", timeout=timedelta(seconds=60))
    return 장치


def 차례로_말하기(말: str) -> None:
    """rank 0부터 차례로 한 줄씩 출력한다 (출력이 뒤섞이지 않게)."""
    for 차례 in range(dist.get_world_size()):
        if dist.get_rank() == 차례:
            print(말, flush=True)
        dist.barrier()                                              # 모두 여기까지 올 때까지 기다린다


장치 = 분산_시작()
rank, 전체 = dist.get_rank(), dist.get_world_size()
if rank == 0:
    print(f"백엔드 {dist.get_backend()}, 프로세스 {전체}개", flush=True)
dist.barrier()

x = torch.full((3,), float(rank + 1), device=장치)                  # rank 0은 1, rank 1은 2
차례로_말하기(f"[rank {rank}] 내 값        {x.tolist()} ({장치})")
dist.all_reduce(x, op=dist.ReduceOp.SUM)                            # 모두의 값을 더해 모두에게
차례로_말하기(f"[rank {rank}] all_reduce 뒤 {x.tolist()}")

평균 = torch.tensor([float(rank + 1)], device=장치)
dist.all_reduce(평균)                                               # 더한 뒤
평균 /= 전체                                                        # 프로세스 수로 나누면 평균
차례로_말하기(f"[rank {rank}] 평균          {평균.item()}")

dist.destroy_process_group()                                        # 끝낼 때 정리
```

이 파일은 `python`으로 바로 실행하지 않고 `torchrun`으로 띄웁니다. `torchrun`은 PyTorch와 함께 설치되는 명령이라, 지금까지 `uv run python`으로 실행했듯이 `uv run torchrun`으로 부릅니다. 터미널에서 이렇게 실행하세요.

```bash
# 이 컴퓨터(노드 하나)에서 프로세스 2개를 띄운다. GPU가 있으면 프로세스마다 GPU 하나씩
uv run torchrun --nproc_per_node=2 --master_addr=127.0.0.1 --master_port=29500 b06_첫_allreduce.py
```

```text
백엔드 nccl, 프로세스 2개
[rank 0] 내 값        [1.0, 1.0, 1.0] (cuda:0)
[rank 1] 내 값        [2.0, 2.0, 2.0] (cuda:1)
[rank 0] all_reduce 뒤 [3.0, 3.0, 3.0]
[rank 1] all_reduce 뒤 [3.0, 3.0, 3.0]
[rank 0] 평균          1.5
[rank 1] 평균          1.5
```

rank 0은 `[1, 1, 1]`, rank 1은 `[2, 2, 2]`를 갖고 있었는데, `all_reduce` 한 줄 뒤에 **둘 다** `[3, 3, 3]`이 됐습니다. 합을 프로세스 수로 나누면 평균 1.5고요. 이것이 DDP의 핵심 동작입니다. GPU마다 다른 데이터로 구한 기울기를 all-reduce로 더해 GPU 수로 나누면, 모든 GPU가 똑같은 평균 기울기를 갖게 되고, 똑같이 고쳐서 계속 같은 모델을 유지해요.

코드에서 볼 점은 이렇습니다.

- **`torchrun`이 하는 일**: `--nproc_per_node=2`만큼 프로세스를 띄우고, 프로세스마다 `RANK`, `LOCAL_RANK`, `WORLD_SIZE`와 서로 만날 주소(`MASTER_ADDR`, `MASTER_PORT`)를 환경 변수로 넣어 줍니다. `init_process_group`은 이 환경 변수를 읽어서 서로를 찾아요. 실행하면 `OMP_NUM_THREADS`를 1로 정했다는 경고가 나오는데, 프로세스 여럿이 CPU 스레드를 서로 다투지 않게 하려는 조치라 무시해도 됩니다(이 장의 출력에서는 뺐습니다).
- **`timeout`과 `device_id`**: 상대가 오지 않으면 영원히 기다리는 대신 정해진 시간 뒤에 오류를 냅니다. `device_id`는 이 프로세스가 쓸 GPU를 미리 알려 줘서 문제가 생겼을 때 멈추지 않고 오류로 끝나게 도와요. 17.12절에서 왜 중요한지 봅니다.
- **`barrier()`**: 모든 프로세스가 여기까지 올 때까지 기다리는 약속 장소입니다. `차례로_말하기`는 이걸로 rank 순서대로 한 줄씩 출력하게 했어요. 프로세스들은 동시에 달리기 때문에, 그냥 `print`하면 출력 순서가 실행할 때마다 뒤섞입니다.
- **`destroy_process_group()`**: 끝날 때 통신 자원을 정리합니다. 빼먹으면 종료할 때 경고가 나와요.

GPU가 없으면 `gloo` 백엔드로 CPU 프로세스끼리 통신합니다. 이 책의 맥에서 같은 명령을 실행하니 백엔드가 `gloo`, 장치가 `cpu`로 바뀌었을 뿐 숫자는 똑같았어요.

### 컴퓨터 여러 대로 넓히려면

지금은 컴퓨터 한 대 안의 GPU 두 장이지만, 같은 코드가 컴퓨터 여러 대로도 그대로 넓어집니다. 달라지는 것은 `torchrun`에 주는 값뿐이에요. `--nnodes`에 컴퓨터(노드) 수를, `--node_rank`에 이 컴퓨터의 번호를 주고, `--master_addr`에는 127.0.0.1 대신 0번 컴퓨터의 네트워크 주소를 줍니다. 그러면 `torchrun`이 컴퓨터마다 GPU 수만큼 프로세스를 띄우고, 전체 rank를 0부터 차례로 매겨요. 코드에서 `LOCAL_RANK`(이 컴퓨터 안의 번호)로 GPU를 고르고 `RANK`(전체 번호)로 rank 0을 가린 것도 이 때문입니다. 컴퓨터 한 대에서는 두 값이 같아서 구분이 안 되지만, 두 대째부터는 달라지거든요.

다만 컴퓨터 사이의 네트워크는 17.6절에서 볼 GPU 사이 연결보다 대개 더 느립니다. 그래서 여러 대로 넓히는 일은 전용 고속 네트워크가 깔린 GPU 클러스터에서 주로 하고, 이 책에서는 컴퓨터 한 대까지만 확인했습니다.

> **Q. 예전 코드에서 `nn.DataParallel`을 봤는데, 그건 뭔가요?**
> 프로세스 하나가 스레드로 여러 GPU를 부리는 예전 방식입니다. `model = nn.DataParallel(model)` 한 줄이면 돼서 간단해 보이지만, 매 걸음 입력을 GPU 0에서 나눠 보내고 결과를 다시 GPU 0으로 모으느라 GPU 0만 바쁘고, 1권 15장에서 본 GIL 때문에 파이썬 쪽도 막힙니다. PyTorch 문서도 컴퓨터 한 대에서 여러 GPU를 쓸 때조차 `DistributedDataParallel`을 쓰라고 권해요. 이 장에서 DDP만 다루는 이유입니다.

## 17.6 통신은 공짜가 아니다

친구를 불렀으면 "다 옮겼어?"를 주고받는 데 얼마나 걸리는지 알아야 합니다. 이 서버에서 all-reduce가 크기별로 얼마나 걸리는지 재 보겠습니다. 비교를 위해 같은 GPU 안에서 256MB를 복사하는 시간도 함께 쟀어요.

```python
import os
import statistics
import time
from datetime import timedelta

import torch
import torch.distributed as dist

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=60), device_id=장치)
rank = dist.get_rank()
MB = 1024 ** 2


def 재기(일, 횟수: int = 10) -> float:
    """준비 운동 3번 뒤 횟수만큼 재서 중앙값(초)을 돌려준다."""
    for _ in range(3):
        일()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(횟수):
        시작 = time.perf_counter()
        일()
        torch.cuda.synchronize()
        시간들.append(time.perf_counter() - 시작)
    return statistics.median(시간들)


if rank == 0:
    print(f"GPU {dist.get_world_size()}개: {torch.cuda.get_device_name(장치)}")
for 크기 in (1, 4, 16, 64, 256):
    x = torch.ones(크기 * MB // 4, device=장치)                  # float32 크기 MB짜리
    초 = 재기(lambda: dist.all_reduce(x))
    if rank == 0:
        print(f"all_reduce {크기:3} MB: {초 * 1000:7.2f} ms ({크기 / 1024 / 초:5.2f} GB/s)")

if rank == 0:                                                 # 비교: 같은 GPU 안에서 복사
    x = torch.ones(256 * MB // 4, device=장치)
    y = torch.empty_like(x)
    초 = 재기(lambda: y.copy_(x))
    print(f"GPU 안 복사 256 MB: {초 * 1000:7.2f} ms ({256 / 1024 / 초:5.0f} GB/s)")
dist.barrier()
dist.destroy_process_group()
```

```text
GPU 2개: NVIDIA GeForce RTX 4090
all_reduce   1 MB:    0.56 ms ( 1.74 GB/s)
all_reduce   4 MB:    2.10 ms ( 1.86 GB/s)
all_reduce  16 MB:    8.19 ms ( 1.91 GB/s)
all_reduce  64 MB:   32.46 ms ( 1.93 GB/s)
all_reduce 256 MB:  127.29 ms ( 1.96 GB/s)
GPU 안 복사 256 MB:    0.59 ms (  424 GB/s)
```

이 책의 실행 환경에서 잰 값입니다. all-reduce는 크기에 거의 정비례해서 1MB에 0.56ms, 256MB에 127ms가 걸렸고, 속도로 따지면 초당 2GB 남짓입니다. 같은 GPU 안에서 256MB를 복사하는 데는 0.59ms, 200배 넘게 빨라요. GPU 안의 메모리는 고속도로이고, GPU 사이는 좁은 골목길인 셈입니다.

왜 이렇게 느릴까요? 이 서버의 구성 때문입니다.

| 항목 | 이 책의 서버 |
|---|---|
| GPU | RTX 4090 24GB × 2 |
| GPU 0의 자리 | PCIe 4세대 8차선 |
| GPU 1의 자리 | PCIe 3세대 4차선 (이론상 한 방향 약 4GB/s) |
| GPU 사이 연결 | NVLink 없음. CPU(PCIe 호스트 브리지)를 거쳐 통신 (`nvidia-smi topo -m`에서 `PHB`) |

두 GPU가 주고받는 길이 좁은 쪽(GPU 1의 3세대 4차선)에 맞춰지니, 이론 한계도 초당 4GB 안팎이에요. 데이터센터용 GPU 서버는 GPU끼리 NVLink로 직접 이어서 이 길이 수십~수백 배 넓습니다. 여러분의 컴퓨터는 `nvidia-smi topo -m` 명령으로 GPU 사이 연결을 확인할 수 있어요.

이 숫자를 기억해 두세요. 10장에서 ResNet18의 파라미터가 44.6MB였죠(정답 10가지짜리로 바꾸면 42.7MB). DDP는 걸음마다 기울기 전체, 즉 이만큼을 all-reduce합니다. 이 서버에서는 약 20ms예요. 한 걸음의 계산이 20ms보다 훨씬 길면 통신 시간이 묻히고, 짧으면 통신이 발목을 잡습니다. 17.9절에서 실제로 확인합니다.

## 17.7 DistributedDataParallel로 학습하기

### 학습 코드에서 바뀌는 곳

이제 9장 9.5절의 옷 사진 CNN을 GPU 두 장으로 학습해 보겠습니다. 6장 6.11절의 학습 루프와 비교하면 바뀌는 곳이 다섯 군데뿐이에요.

```python
import os
import time
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision import datasets, transforms

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")


class 옷CNN(nn.Module):
    """9장 9.5절의 작은 CNN."""

    def __init__(self) -> None:
        super().__init__()
        self.특징 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.분류 = nn.Sequential(
            nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.분류(self.특징(x))


def 분산_시작() -> torch.device:
    """torchrun이 넣어 준 환경 변수로 프로세스 그룹에 들어간다."""
    if torch.cuda.is_available():
        장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
        torch.cuda.set_device(장치)
        dist.init_process_group("nccl", timeout=timedelta(seconds=120), device_id=장치)
    else:
        장치 = torch.device("cpu")
        dist.init_process_group("gloo", timeout=timedelta(seconds=120))
    return 장치


def 옷_데이터(학습: bool) -> datasets.FashionMNIST:
    return datasets.FashionMNIST(데이터_폴더, train=학습, download=True,
                                 transform=transforms.ToTensor())


def 정확도(모델: nn.Module, 장치: torch.device) -> float:
    """시험 데이터 1만 장의 정확도 (rank 0에서만 부른다)."""
    모델.eval()
    맞힘 = 0
    with torch.no_grad():
        for x, y in DataLoader(옷_데이터(False), batch_size=1000):
            맞힘 += (모델(x.to(장치)).argmax(1) == y.to(장치)).sum().item()
    return 맞힘 / 10_000


장치 = 분산_시작()
rank, 전체 = dist.get_rank(), dist.get_world_size()
if rank == 0:
    옷_데이터(True), 옷_데이터(False)          # 내려받기는 한 프로세스만
dist.barrier()                               # 다 받을 때까지 나머지는 기다린다

학습셋 = 옷_데이터(True)
샘플러 = DistributedSampler(학습셋, shuffle=True, seed=0)   # 데이터를 프로세스 수만큼 나눈다
로더 = DataLoader(학습셋, batch_size=128, sampler=샘플러)    # GPU마다 128장, 합쳐서 256장
for 차례 in range(전체):
    if rank == 차례:
        print(f"[rank {rank}] 맡은 샘플 {len(샘플러):,}개, 배치 {len(로더)}개, "
              f"앞 번호 {list(샘플러)[:4]}", flush=True)
    dist.barrier()

torch.manual_seed(0)                         # 모든 프로세스가 같은 초깃값으로 시작
모델 = DDP(옷CNN().to(장치))                  # 기울기를 all_reduce로 평균 내 주는 포장지
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
손실함수 = nn.CrossEntropyLoss()

for 에폭 in range(1, 4):
    샘플러.set_epoch(에폭)                    # 에폭마다 섞는 순서를 바꾼다
    모델.train()
    합계 = torch.zeros(2, device=장치)         # [손실 합, 개수]
    시작 = time.perf_counter()
    for x, y in 로더:
        x, y = x.to(장치), y.to(장치)
        옵티마이저.zero_grad()
        손실 = 손실함수(모델(x), y)
        손실.backward()                       # 여기서 GPU끼리 기울기를 평균 낸다
        옵티마이저.step()
        합계[0] += 손실.detach() * len(y)
        합계[1] += len(y)
    dist.all_reduce(합계)                     # 모든 프로세스의 손실을 모은다
    if rank == 0:
        print(f"에폭 {에폭}: 학습 손실 {합계[0] / 합계[1]:.4f} "
              f"({int(합계[1]):,}장, {time.perf_counter() - 시작:.1f}초)")

if rank == 0:                                # 저장과 평가는 한 프로세스만
    print(f"시험 정확도: {정확도(모델.module, 장치):.2%}")
    torch.save({"에폭": 3, "모델": 모델.module.state_dict(),
                "옵티마이저": 옵티마이저.state_dict()}, "ddp_옷CNN.pt")
    print("저장한 키:", list(torch.load("ddp_옷CNN.pt")["모델"])[:2], "...")
dist.barrier()
dist.destroy_process_group()
```

```text
[rank 0] 맡은 샘플 30,000개, 배치 235개, 앞 번호 [36044, 57327, 21567, 9481]
[rank 1] 맡은 샘플 30,000개, 배치 235개, 앞 번호 [10678, 55074, 15479, 43095]
에폭 1: 학습 손실 0.5870 (60,000장, 0.9초)
에폭 2: 학습 손실 0.3526 (60,000장, 0.8초)
에폭 3: 학습 손실 0.3029 (60,000장, 0.8초)
시험 정확도: 88.54%
저장한 키: ['특징.0.weight', '특징.0.bias'] ...
```

바뀐 곳을 차례로 보겠습니다.

1. **내려받기는 한 프로세스만**: 두 프로세스가 동시에 같은 파일을 내려받으면 서로 덮어써서 파일이 깨질 수 있습니다. rank 0만 받고, 나머지는 `barrier()`에서 기다렸다가 받아 둔 파일을 읽어요.
2. **`DistributedSampler`**: 데이터를 프로세스 수만큼 겹치지 않게 나눕니다. 출력을 보면 6만 장을 3만 장씩 나눠 맡았고, 두 rank의 앞 번호가 서로 다르죠. GPU마다 128장씩이니 한 걸음에 합쳐서 256장, 에폭마다 235걸음입니다. 샘플러를 줄 때는 `DataLoader`의 `shuffle`을 쓰지 않아요. 섞는 일도 샘플러가 합니다.
3. **`DDP(모델)`**: 모델을 DDP로 감쌉니다. 감쌀 때 rank 0의 파라미터를 모두에게 복사해서 출발점을 맞추고, `backward()` 도중에 기울기를 all-reduce로 평균 내 줘요. 학습 루프의 `zero_grad`, `backward`, `step`은 한 글자도 바뀌지 않았습니다.
4. **`set_epoch(에폭)`**: 샘플러는 에폭 번호를 씨앗에 섞어서 순서를 정합니다. 이걸 부르지 않으면 **매 에폭 같은 순서**로 데이터를 보게 돼요. 오류도 경고도 없이 조용히 학습이 조금 나빠지는 흔한 실수입니다.
5. **출력·평가·저장은 rank 0만**: 그냥 두면 모든 프로세스가 같은 줄을 출력하고 같은 파일에 동시에 씁니다. 손실은 GPU마다 다르니 `all_reduce`로 모은 뒤 rank 0이 출력했어요(6만 장이 모두 집계된 게 보이죠).

저장할 때는 `모델.module.state_dict()`처럼 DDP 포장지 안의 원래 모델을 꺼내서 저장했습니다. 그래야 키 이름이 `특징.0.weight`처럼 깔끔하게 나와서, DDP 없이 GPU 하나나 CPU에서 그대로 불러올 수 있어요. `모델.state_dict()`로 저장하면 키마다 `module.`이 붙어서 6장 방식으로 불러올 때 이름이 안 맞습니다. 다른 장치에서 불러올 때는 4장 4.9절의 `map_location`을 쓰고요.

> **Q. 이어서 학습하려면 체크포인트에 무엇을 더 넣어야 하나요?**
> 자세한 것은 다음 18장 18.3절에서 다룹니다. 요점은 모델·옵티마이저·스케줄러·난수 상태를 담고, 다시 시작할 때 **모든 rank가** 그 파일을 읽어 같은 상태에서 출발해야 해요. 분산이라서 더할 것은 둘입니다. 샘플러에 `set_epoch`로 이어 갈 에폭 번호를 주는 것, 그리고 rank 0이 저장을 마치기 전에 다른 rank가 파일을 읽지 않도록 저장 뒤에 `barrier()`를 두는 것이에요. 위 코드의 마지막 `dist.barrier()`가 그 자리입니다.

시험 정확도 88.54%는 9장의 작은 CNN을 3에폭 학습한 결과로 그럴듯합니다. 실행마다 끝자리가 조금씩 다를 수 있어요. GPU의 일부 계산은 순서가 매번 조금씩 달라지기 때문입니다(8장 8.10절).

## 17.8 1 GPU와 같은 결과일까

DDP로 학습한 모델은 GPU 하나로 학습한 것과 같은 모델일까요? 같은 데이터, 같은 초깃값, 같은 **전체 배치 크기**라면 같아야 합니다. GPU 두 장이 16개씩 맡는 것과 GPU 하나가 32개를 한 번에 받는 것을 비교해 보겠습니다.

```python
import os
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.distributed import DistributedSampler

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=60), device_id=장치)
rank, 전체 = dist.get_rank(), dist.get_world_size()

torch.manual_seed(0)
데이터 = TensorDataset(torch.randn(256, 20), torch.randn(256, 1))   # 예제용으로 만든 데이터
전체_배치 = 32


def 새_모델() -> nn.Module:
    torch.manual_seed(1)
    return nn.Sequential(nn.Linear(20, 64), nn.ReLU(), nn.Linear(64, 1)).to(장치)


def 학습(모델: nn.Module, 로더: DataLoader, 분산: bool) -> list[float]:
    """한 에폭 동안 걸음마다 (전체 배치의) 손실을 기록한다."""
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.1)
    기록 = []
    for x, y in 로더:
        옵티마이저.zero_grad()
        손실 = nn.functional.mse_loss(모델(x.to(장치)), y.to(장치))
        손실.backward()
        옵티마이저.step()
        손실 = 손실.detach()
        if 분산:
            dist.all_reduce(손실)          # 두 GPU의 손실 평균 = 전체 배치의 손실
            손실 /= 전체
        기록.append(round(손실.item(), 5))
    return 기록


# 2 GPU: GPU마다 16개씩, 합쳐서 32개
샘플러 = DistributedSampler(데이터, shuffle=False)
ddp = DDP(새_모델())
ddp_기록 = 학습(ddp, DataLoader(데이터, batch_size=전체_배치 // 전체, sampler=샘플러), 분산=True)

if rank == 0:                              # 비교용: 1 GPU에서 32개씩
    하나 = 새_모델()
    하나_기록 = 학습(하나, DataLoader(데이터, batch_size=전체_배치), 분산=False)
    print("2 GPU × 16개:", ddp_기록)
    print("1 GPU × 32개:", 하나_기록)
    차이 = max((a - b).abs().max().item()
             for a, b in zip(ddp.module.parameters(), 하나.parameters()))
    print(f"8걸음 뒤 파라미터 최대 차이: {차이:.1e}")
dist.barrier()
dist.destroy_process_group()
```

```text
2 GPU × 16개: [1.21992, 1.15777, 1.85537, 1.33644, 0.62719, 0.9723, 0.89722, 1.04313]
1 GPU × 32개: [1.21992, 1.15777, 1.85537, 1.33644, 0.62719, 0.9723, 0.89722, 1.04313]
8걸음 뒤 파라미터 최대 차이: 3.7e-08
```

여덟 걸음의 손실이 다섯째 자리까지 똑같고, 파라미터 차이는 3.7e-08로 `float32`의 끝자리 오차뿐입니다. 17.2절의 그래디언트 누적과 같은 원리예요. 16개짜리 평균 기울기 둘을 다시 평균 내면 32개짜리 평균 기울기가 되니까요. **DDP는 GPU 여러 장에 걸친 그래디언트 누적**이라고 생각해도 됩니다. 누적은 시간 순서로 나눠 담고, DDP는 GPU별로 나눠 담는 거죠.

샘플러에 `shuffle=False`를 줬기 때문에 비교가 정확히 맞아떨어졌습니다. `DistributedSampler`는 번호를 rank 0에 0, 2, 4, …, rank 1에 1, 3, 5, …처럼 번갈아 나눠 줘서, 첫 걸음에 두 GPU가 받은 32개가 GPU 하나가 받은 0~31번과 같은 묶음이 됐어요.

여기서 실무에서 자주 헷갈리는 점이 하나 나옵니다. 실습 코드를 GPU 하나에서 배치 32로 쓰다가 그대로 GPU 두 장에 올리면, GPU마다 32개씩 **전체 배치가 64**가 됩니다. 같은 에폭 동안 걸음 수는 절반이 되고 한 걸음의 평균 기울기는 더 매끈해져요. 그러면 같은 학습률로는 결과가 달라집니다. GPU를 늘릴 때는 둘 중 하나를 정하세요.

- **전체 배치를 유지한다**: GPU당 배치를 GPU 수로 나눈다. 결과가 GPU 하나와 같다(이 절과 17.13절 실습의 방식).
- **전체 배치를 키운다**: 처리량을 최대로 쓰는 대신 학습률을 다시 맞춘다. 배치가 k배면 학습률도 k배 가까이 키우고 처음 몇 걸음은 작게 시작하는(워밍업, 8장 8.7절의 스케줄러) 방식이 흔히 쓰이지만, 언제나 통하는 공식은 아니니 검증 성적으로 확인해야 해요.

## 17.9 GPU를 늘리면 몇 배 빨라질까

두 배일까요? 17.6절의 통신 비용을 생각하면 그렇지 않을 것 같습니다. 모델과 입력 크기를 바꿔 가며 GPU 하나와 두 장의 처리량(1초에 학습하는 사진 수)을 비교해 보겠습니다. GPU당 배치는 고정하고, 입력은 GPU 안에서 만든 난수라서 데이터 로더나 디스크는 끼어들지 않아요. 순수하게 계산과 통신만 재는 셈입니다.

```python
import os
import statistics
import time
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torchvision.models import resnet18, resnet50

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=300), device_id=장치)
rank = dist.get_rank()


class 작은CNN(nn.Module):
    """9장의 옷CNN과 같은 구조 (파라미터 42만 개)."""

    def __init__(self) -> None:
        super().__init__()
        self.층들 = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.층들(x)


def 초당_장수(모델: nn.Module, 배치: int, 크기: int, 채널: int) -> float:
    """GPU 하나가 1초에 학습하는 사진 수 (준비 운동 3걸음 뒤 10걸음의 중앙값)."""
    x = torch.randn(배치, 채널, 크기, 크기, device=장치)        # 예제용 입력
    y = torch.randint(0, 10, (배치,), device=장치)
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.01)
    시간들 = []
    for 걸음 in range(13):
        torch.cuda.synchronize()
        시작 = time.perf_counter()
        옵티마이저.zero_grad()
        nn.functional.cross_entropy(모델(x), y).backward()
        옵티마이저.step()
        torch.cuda.synchronize()
        if 걸음 >= 3:
            시간들.append(time.perf_counter() - 시작)
    return 배치 / statistics.median(시간들)


실험들 = [  # (이름, 모델 만들기, GPU당 배치, 사진 크기, 채널)
    ("작은CNN 28px", 작은CNN, 256, 28, 1),
    ("ResNet18 64px", lambda: resnet18(num_classes=10), 128, 64, 3),
    ("ResNet18 224px", lambda: resnet18(num_classes=10), 128, 224, 3),
    ("ResNet50 224px", lambda: resnet50(num_classes=10), 64, 224, 3),
]
if rank == 0:
    print(f"{'모델':14} {'기울기 MB':>8} {'1 GPU':>7} {'2 GPU':>7} {'배율':>5}")
for 이름, 만들기, 배치, 크기, 채널 in 실험들:
    torch.manual_seed(0)
    모델 = 만들기().to(장치)
    MB = sum(p.numel() for p in 모델.parameters()) * 4 / 1024 ** 2
    하나 = 초당_장수(모델, 배치, 크기, 채널) if rank == 0 else 0.0   # GPU 0 혼자
    dist.barrier()
    둘 = 초당_장수(DDP(모델), 배치, 크기, 채널) * dist.get_world_size()  # 두 GPU 합계
    if rank == 0:
        print(f"{이름:14} {MB:8.1f} {하나:7,.0f} {둘:7,.0f} {둘 / 하나:5.2f}")
dist.barrier()
dist.destroy_process_group()
```

```text
모델               기울기 MB   1 GPU   2 GPU    배율
작은CNN 28px          1.6 270,920 296,665  1.10
ResNet18 64px      42.7  17,768  10,517  0.59
ResNet18 224px     42.7   2,445   3,953  1.62
ResNet50 224px     89.8     790   1,195  1.51
```

이 책의 실행 환경에서 다른 프로그램이 GPU를 쓰지 않을 때 잰 값이고, 두 번 재서 거의 같은 값을 확인했습니다. 배율이 2배에 가까운 것이 하나도 없어요. 그리고 두 번째 줄은 GPU 두 장이 **오히려 0.59배, 더 느립니다.** 한 줄씩 해석해 보겠습니다.

- **작은CNN 28px (1.10배)**: 기울기가 1.6MB밖에 안 돼서 통신은 1ms 남짓입니다. 그런데 한 걸음의 계산도 1ms 정도로 아주 짧아요(256장 ÷ 초당 27만 장). 걸음마다 오가는 확인 절차가 계산만큼 길어서 이득이 거의 없습니다.
- **ResNet18 64px (0.59배)**: 기울기 42.7MB를 주고받는 데 이 서버에서 20ms 넘게 걸리는데, GPU 하나의 한 걸음 계산은 7ms 정도(128장 ÷ 초당 1만 7,768장)입니다. 7ms 일하고 20ms 기다리니 혼자 할 때보다 느려졌어요. 친구를 불렀더니 엘리베이터 앞 줄이 일하는 시간보다 길어진 겁니다.
- **ResNet18 224px (1.62배)**: 같은 모델, 같은 기울기 크기인데 사진이 커서 한 걸음 계산이 50ms 남짓으로 길어졌습니다. 통신 20ms가 상대적으로 작아지니 이득이 났어요.
- **ResNet50 224px (1.51배)**: 계산은 더 길지만 기울기도 89.8MB로 두 배라서 통신도 늘었습니다.

정리하면 GPU를 늘린 이득은 **"한 걸음의 계산 시간 대 통신 시간"** 의 비율로 정해집니다. 모델이 크고 입력이 크고 배치가 클수록 계산이 길어져 이득이 커지고, GPU 사이 길이 좁을수록 이득이 줄어요.

그런데 ResNet18 224px를 보면 계산 52ms에 통신 20ms를 더하면 72ms여야 하는데, 2 GPU의 한 걸음은 65ms 정도(256장 ÷ 초당 3,953장)입니다. 통신 일부가 계산 뒤에 숨은 거예요. DDP는 기울기를 25MB 안팎의 **버킷(bucket)** 으로 묶어 두고, backward가 뒤쪽 층의 기울기를 다 구하면 앞쪽 층을 계산하는 동안 그 버킷부터 미리 보냅니다. 앞 사람이 짐을 들고 계단을 오르는 동안 뒷사람이 다음 짐을 싸는 셈이죠. 그래서 계산이 길수록 통신이 더 많이 숨습니다.

> **Q. 그럼 이 서버에서는 2 GPU를 쓰지 말아야 하나요?**
> 모델에 따라 다릅니다. 위 표처럼 계산이 큰 학습에서는 1.5~1.6배 빨라지니 충분히 쓸 만해요. 계산이 작은 학습이라면 다음 절의 방법으로 통신 횟수를 줄이거나, 아예 GPU마다 **다른 실험**(예를 들어 학습률이 다른 두 실험)을 하나씩 돌리는 편이 낫습니다. 18장 18.5절의 하이퍼파라미터 탐색처럼 실험이 여러 개라면 이쪽이 통신 없이 정확히 2배예요.

## 17.10 no_sync: 누적과 DDP 합치기

ResNet18 64px처럼 통신이 병목일 때 쓸 수 있는 방법이 있습니다. 17.2절의 그래디언트 누적을 DDP와 합치는 거예요. 그런데 그냥 합치면 손해를 봅니다. DDP는 `backward()`를 부를 때마다 all-reduce를 하니까, 4번 누적하면 통신도 4번 하거든요. 사실 평균은 **누적이 끝난 뒤 한 번만** 내면 충분합니다. 장바구니를 다 채운 뒤 한 번만 계산대에 가면 되는 것처럼요. DDP의 `no_sync()` 안에서 부른 `backward()`는 기울기를 쌓기만 하고 통신을 건너뜁니다.

```python
import os
import statistics
import time
from contextlib import nullcontext
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torchvision.models import resnet18

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=300), device_id=장치)
rank, 전체 = dist.get_rank(), dist.get_world_size()

누적 = 4
torch.manual_seed(rank)                               # GPU마다 다른 예제용 입력
조각들 = [(torch.randn(128, 3, 64, 64, device=장치), torch.randint(0, 10, (128,), device=장치))
        for _ in range(누적)]


def 한_걸음(모델: DDP, 옵티마이저: torch.optim.Optimizer, no_sync: bool) -> None:
    """작은 배치 4개의 기울기를 모은 뒤 한 번 고친다."""
    옵티마이저.zero_grad()
    for i, (x, y) in enumerate(조각들):
        마지막 = i == 누적 - 1
        문맥 = 모델.no_sync() if no_sync and not 마지막 else nullcontext()
        with 문맥:                                    # no_sync 안에서는 all_reduce를 건너뛴다
            (nn.functional.cross_entropy(모델(x), y) / 누적).backward()
    옵티마이저.step()


def 새_모델() -> tuple[DDP, torch.optim.Optimizer]:
    torch.manual_seed(0)
    모델 = DDP(resnet18(num_classes=10).to(장치))
    return 모델, torch.optim.SGD(모델.parameters(), lr=0.01)


for no_sync in (False, True):
    모델, 옵티마이저 = 새_모델()
    시간들 = []
    for 걸음 in range(13):
        torch.cuda.synchronize()
        시작 = time.perf_counter()
        한_걸음(모델, 옵티마이저, no_sync)
        torch.cuda.synchronize()
        if 걸음 >= 3:
            시간들.append(time.perf_counter() - 시작)
    장수 = 128 * 누적 * 전체 / statistics.median(시간들)
    if rank == 0:
        print(f"누적 {누적}번, no_sync {'씀 ' if no_sync else '안 씀'}: "
              f"한 걸음 {statistics.median(시간들) * 1000:4.0f} ms, 두 GPU 합계 {장수:6,.0f}장/초")


def 한_걸음_뒤(no_sync: bool) -> list[torch.Tensor]:
    """새 모델로 한 걸음만 고친 뒤의 파라미터."""
    모델, 옵티마이저 = 새_모델()
    한_걸음(모델, 옵티마이저, no_sync)
    return [p.detach().clone() for p in 모델.parameters()]


def 최대_차이(a: list[torch.Tensor], b: list[torch.Tensor]) -> float:
    return max((x - y).abs().max().item() for x, y in zip(a, b))


기준, 다시, 건너뜀 = 한_걸음_뒤(False), 한_걸음_뒤(False), 한_걸음_뒤(True)
if rank == 0:
    print(f"한 걸음 뒤 파라미터 최대 차이: 같은 방식 두 번 {최대_차이(기준, 다시):.1e}, "
          f"no_sync 쓴 쪽과 {최대_차이(기준, 건너뜀):.1e}")
dist.destroy_process_group()
```

```text
누적 4번, no_sync 안 씀: 한 걸음  100 ms, 두 GPU 합계 10,284장/초
누적 4번, no_sync 씀 : 한 걸음   46 ms, 두 GPU 합계 22,033장/초
한 걸음 뒤 파라미터 최대 차이: 같은 방식 두 번 7.5e-09, no_sync 쓴 쪽과 7.5e-09
```

같은 누적 4번인데 `no_sync`를 쓰니 한 걸음이 100ms에서 46ms로 줄고, 처리량이 초당 1만 284장에서 2만 2,033장으로 두 배 넘게 늘었습니다. 통신을 4번에서 1번으로 줄인 덕분이에요. 17.9절에서 GPU 하나가 초당 1만 7,768장이었으니, 0.59배이던 2 GPU가 이제는 1.24배가 됐습니다. 전체 배치는 1,024장(128장 × 4번 × 2 GPU)으로 커졌으니 17.8절에서 말한 학습률 조정은 함께 생각해야 하고요.

결과도 확인했습니다. 한 걸음 고친 뒤의 파라미터 차이가 `no_sync`를 쓴 쪽과 7.5e-09로, 같은 방식을 두 번 돌렸을 때의 차이(7.5e-09)와 같아요. GPU 계산의 끝자리 흔들림 말고는 차이가 없다는 뜻입니다. 이렇게 "기준이 되는 흔들림"을 함께 재 두면, 차이가 버그 때문인지 실수 계산의 잡음인지 구분할 수 있습니다.

코드에서는 `no_sync()`를 **마지막 조각을 뺀** 나머지에만 씌운 것이 핵심입니다. 마지막 조각까지 씌우면 통신을 한 번도 안 해서 GPU마다 다른 기울기로 고치게 되고, 두 GPU의 모델이 조용히 갈라져요. `nullcontext()`는 "아무것도 하지 않는 `with`"라서, 조건에 따라 `with`를 쓰거나 안 쓰는 코드를 한 줄로 쓸 수 있게 해 줍니다.

## 17.11 FSDP: 모델까지 나눠 담기

### 모두가 같은 책을 들고 있을 필요는 없다

DDP는 GPU마다 모델 전체와 기울기 전체, 옵티마이저 상태 전체를 똑같이 들고 있습니다. 17.1절의 "파라미터의 4배"가 GPU마다 그대로 있는 거죠. 7B 모델이라면 GPU마다 104GB라서 DDP로는 아무리 GPU를 늘려도 학습할 수 없어요.

**FSDP(Fully Sharded Data Parallel)** 는 이 중복을 없앱니다. 두 사람이 백과사전 한 질을 나눠 들고 다니다가, 어떤 권이 필요한 순간에만 잠깐 빌려 보고 돌려주는 방식이에요. 평소에는 GPU마다 파라미터·기울기·옵티마이저 상태의 **1/GPU 수**만 갖고 있다가, 어떤 층을 계산할 차례가 되면 그 층의 파라미터를 모두에게서 모아(all-gather) 계산하고 바로 버립니다. 이 아이디어를 처음 널리 알린 것이 DeepSpeed라는 라이브러리의 **ZeRO**이고, 무엇까지 나누느냐에 따라 1단계(옵티마이저 상태), 2단계(+ 기울기), 3단계(+ 파라미터)로 부릅니다. FSDP는 3단계에 해당해요.

PyTorch 2.14의 `fully_shard`로 17.3절의 트랜스포머를 DDP와 FSDP로 각각 학습해 보겠습니다.

```python
import os
import statistics
import time
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.distributed.fsdp import fully_shard
from torch.nn.parallel import DistributedDataParallel as DDP

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 2개 있어야 합니다"
장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
torch.cuda.set_device(장치)
dist.init_process_group("nccl", timeout=timedelta(seconds=300), device_id=장치)
rank = dist.get_rank()
GB = 1024 ** 3


def 새_모델() -> nn.Sequential:
    """인코더 층 12개 (파라미터 약 1억 5천만 개). 두 방식이 같은 초깃값으로 시작한다."""
    torch.manual_seed(0)
    return nn.Sequential(*[nn.TransformerEncoderLayer(1024, 16, 4096, dropout=0.0, batch_first=True)
                           for _ in range(12)]).to(장치)


def 감싸기(방식: str) -> nn.Module:
    모델 = 새_모델()
    if 방식 == "DDP":
        return DDP(모델)                    # GPU마다 모델 전체를 복사해 둔다
    for 층 in 모델:
        fully_shard(층)                     # 층마다 파라미터를 GPU 수만큼 나눠 맡는다
    return fully_shard(모델)


torch.manual_seed(rank)
x = torch.randn(8, 256, 1024, device=장치)          # 예제용 입력, GPU마다 다르게
for 방식 in ("DDP", "FSDP"):
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    시작_메모리 = torch.cuda.memory_allocated()
    모델 = 감싸기(방식)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-4)
    손실들, 시간들 = [], []
    for _ in range(5):
        torch.cuda.synchronize()
        시작 = time.perf_counter()
        옵티마이저.zero_grad()
        손실 = 모델(x).pow(2).mean()
        손실.backward()
        옵티마이저.step()
        torch.cuda.synchronize()
        시간들.append(time.perf_counter() - 시작)
        손실 = 손실.detach()
        dist.all_reduce(손실)                          # 두 GPU 손실의 평균을 기록
        손실들.append(round(손실.item() / 2, 5))
    남은 = (torch.cuda.memory_allocated() - 시작_메모리) / GB   # 파라미터·기울기·Adam 상태
    if rank == 0:
        print(f"{방식:4}: GPU 하나에 남은 것 {남은:4.2f} GB, 최고 {torch.cuda.max_memory_allocated() / GB:4.2f} GB, "
              f"한 걸음 {statistics.median(시간들[1:]) * 1000:4.0f} ms")
        print(f"      손실 {손실들}")
    del 모델, 옵티마이저
dist.destroy_process_group()
```

```text
DDP : GPU 하나에 남은 것 2.83 GB, 최고 3.60 GB, 한 걸음  328 ms
      손실 [0.99999, 0.99971, 0.99929, 0.99889, 0.99851]
FSDP: GPU 하나에 남은 것 1.08 GB, 최고 2.28 GB, 한 걸음  580 ms
      손실 [0.99999, 0.99971, 0.99929, 0.99889, 0.99851]
```

학습이 끝난 뒤 GPU 하나에 남아 있는 것(파라미터·기울기·Adam 상태)이 DDP는 2.83GB, FSDP는 1.08GB입니다. 파라미터 1억 5천만 개 × 16바이트 = 2.25GB를 FSDP는 반으로 나눠 들었고, DDP는 그 2.25GB에 통신용 버킷(기울기 크기만큼, 약 0.56GB)까지 더 들고 있어요. 다섯 걸음의 손실이 두 방식에서 똑같으니, 같은 학습을 메모리만 덜 쓰고 한 겁니다.

대신 한 걸음이 328ms에서 580ms로 느려졌습니다. 층마다 파라미터를 모으고 기울기를 다시 나누느라 통신량이 DDP보다 많은데, 이 서버의 GPU 사이 길이 좁기 때문이에요. 그래서 FSDP는 **모델이 DDP로 안 들어갈 때** 꺼내는 도구입니다. 들어간다면 DDP가 더 빠르고 간단해요. GPU 사이 연결이 빠른 서버일수록 FSDP의 손해는 작아집니다.

FSDP로 저장할 때는 각 GPU가 조각만 갖고 있어서 `state_dict()`가 조각난 텐서(DTensor)로 나옵니다. 하나의 파일로 모으거나 조각별로 저장하는 방법은 PyTorch의 `torch.distributed.checkpoint` 문서를 따르세요. 이 장에서는 거기까지 확인하지 않았습니다.

### 직접 짜지 않는 방법들

실무에서는 지금까지의 코드를 대신 써 주는 도구를 많이 씁니다. Hugging Face의 **Accelerate**는 학습 루프를 거의 그대로 둔 채 `accelerate launch` 명령 하나로 DDP나 FSDP로 실행하게 해 주고, `transformers`의 `Trainer`도 `torchrun`으로 실행하면 알아서 DDP로 학습합니다. 그래도 이 장에서 본 rank·샘플러·all-reduce·`no_sync`의 원리를 알고 있어야, 도구가 이상하게 느리거나 멈출 때 어디를 볼지 알 수 있어요.

## 17.12 흔한 오류와 대처

### 한 프로세스만 통신을 부르면

분산 학습에서 가장 무서운 오류는 오류 메시지가 **안 나오는** 것입니다. 통신은 모든 프로세스가 같은 순서로 같은 함수를 불러야 이뤄지는데, 한 프로세스만 부르면 그 프로세스는 상대가 올 때까지 하염없이 기다려요. 일부러 일으켜 보겠습니다. CPU끼리 통신하는 `gloo`로 만들었으니 어느 컴퓨터에서나 실행할 수 있어요.

```python
import time
from datetime import timedelta

import torch
import torch.distributed as dist

# CPU끼리(gloo) 통신. 기다리는 한계를 5초로 짧게 잡는다
dist.init_process_group("gloo", timeout=timedelta(seconds=5))
rank = dist.get_rank()
x = torch.ones(1)

if rank == 0:                      # 실수: rank 0만 all_reduce를 부른다
    시작 = time.perf_counter()
    try:
        dist.all_reduce(x)
    except RuntimeError as e:
        print(f"[rank 0] {time.perf_counter() - 시작:.0f}초 만에 오류:", str(e).split("] ", 1)[-1])  # 파일 위치는 떼고
else:
    time.sleep(8)                  # rank 1은 다른 일을 하느라 통신에 오지 않는다
    print("[rank 1] 끝", flush=True)
```

```text
[rank 0] 5초 만에 오류: Timed out waiting 5000ms for recv operation to complete
[rank 1] 끝
```

rank 0만 `all_reduce`를 불렀고, rank 1은 오지 않았습니다. `timeout`을 5초로 정해 뒀기 때문에 rank 0은 5초 뒤 "받기를 기다리다 시간이 다 됐다"는 오류를 냈어요. 기본 시간 한계는 `nccl`이 10분, `gloo`가 30분이라서, `timeout`을 주지 않으면 이 프로그램은 오랫동안 아무 말 없이 멈춰 있습니다. GPU 사용률은 0%인데 프로세스는 살아 있는 상태요.

실제 코드에서는 이런 실수가 이렇게 생깁니다.

- `if rank == 0:` 안에서 평가하다가, 그 안에서 `all_reduce`나 DDP 모델의 forward처럼 **통신이 들어 있는 일**을 부른다. 평가는 `모델.module`처럼 DDP 포장지를 벗긴 모델로 한다(17.7절).
- 프로세스마다 배치 수가 다르다. `DistributedSampler`는 데이터 수가 나누어떨어지지 않으면 몇 개를 반복해서 배치 수를 맞춰 주지만, 직접 데이터를 나눴다면 한쪽이 먼저 끝나고 다른 쪽은 기다린다.
- 한 프로세스에서만 예외가 나서 죽었다. 남은 프로세스는 죽은 상대를 기다린다. `torchrun`은 한 프로세스가 죽으면 나머지도 정리하지만, 직접 띄운 프로세스라면 남아 있을 수 있다.

### 처음부터 서로를 못 찾을 때

이 장의 예제를 처음 이 서버에서 실행했을 때, 프로세스들이 서로를 찾지 못하고 멈췄습니다. 로그에는 이런 줄이 반복됐어요.

```text
[c10d] The server socket on [::ffff:0.0.15.250]:34045 has timed out, will retry.
```

`0.0.15.250`이라는 이상한 주소가 보이죠? 이 서버의 호스트 이름이 숫자 `4090`인데, 이걸 주소로 해석하는 과정에서 정수 4090이 IP 주소 0.0.15.250(15 × 256 + 250 = 4090)으로 바뀌어 버린 거예요. `torchrun`은 주소를 따로 주지 않으면 호스트 이름으로 서로를 찾습니다. 그래서 이 장의 모든 명령에 `--master_addr=127.0.0.1`(이 컴퓨터 자신)을 줬어요. 앞의 멈춤 예제를 이 서버에서 실행했을 때도 `gloo`가 "호스트 이름을 주소로 바꿀 수 없어서 루프백 주소(127.0.0.1)를 쓴다"는 경고를 냈는데, 같은 원인입니다. 컴퓨터 한 대에서만 돌린다면 `--master_addr=127.0.0.1`을 습관처럼 붙여 두면 이런 일을 피할 수 있어요.

### 그 밖의 흔한 문제

| 증상 | 원인 | 대처 |
|---|---|---|
| `Address already in use` | 같은 포트를 다른 실행(또는 죽지 않은 지난 실행)이 쓰는 중 | `--master_port`를 다른 번호로. 남은 프로세스 정리 |
| 출력이 두 번씩 나온다 | 모든 rank가 출력함 | `if rank == 0:` 안에서 출력 |
| 에폭마다 손실 곡선이 똑같은 모양 | `set_epoch`을 안 불러 순서가 매번 같음 | 에폭마다 `샘플러.set_epoch(에폭)` |
| 불러온 가중치의 키 이름이 안 맞음 | `module.`이 붙은 DDP 모델을 저장함 | `모델.module.state_dict()`로 저장 |
| 모든 프로세스가 GPU 0에 몰림 | `torch.cuda.set_device`를 안 함 | `LOCAL_RANK`로 장치를 정하고 `set_device` |
| `NVIDIA driver on your system is too old` | 설치한 PyTorch의 CUDA 버전을 드라이버가 지원하지 않음 | 드라이버가 지원하는 CUDA용 빌드로 다시 설치 (부록 A.4절) |
| 끝났는데 GPU 메모리가 차 있다 | 죽지 않은 프로세스가 남음 | `nvidia-smi`로 남은 프로세스 번호(PID)를 보고 종료 |

표의 여섯째 줄은 16장 첫머리에서 본, 이 서버에서 실제로 겪은 오류입니다. 새 서버에서는 학습 코드보다 `nvidia-smi`의 CUDA 버전과 `torch.version.cuda`부터 확인하세요.

## 17.13 실습: 옷 분류기를 세 가지 방법으로 학습하기

이 장에서 배운 것을 한 파일에 모아 보겠습니다. 9장의 옷 사진 CNN을 **한 걸음에 반영하는 사진 수를 256장으로 고정**한 채 세 가지 방법으로 학습하고, 정확도·시간·메모리를 비교합니다.

1. GPU 하나로 256장씩
2. GPU 하나로 64장씩 4번 누적
3. GPU 두 장으로 128장씩 (DDP)

같은 파일을 `python`으로 실행하면 프로세스 하나로, `torchrun`으로 실행하면 분산 학습으로 돌아가게 만들었습니다. `torchrun`이 넣어 주는 `RANK` 환경 변수가 있는지로 구분해요. 7장 7.10절에서 본 것처럼 프로세스를 여럿 띄우는 프로그램이니 `if __name__ == "__main__":` 아래에서 시작합니다. 아래 코드를 `b13_실습.py`로 저장하세요. 뒤에서 이 파일의 부품을 다시 가져다 쓰니 이름을 그대로 두는 것이 좋아요.

```python
"""17장 실습: 옷 사진 CNN을 1 GPU, 그래디언트 누적, DDP 2 GPU로 학습해 비교한다.

python으로 실행하면 프로세스 하나, torchrun으로 실행하면 분산 학습이 된다.
"""
import argparse
import os
import time
from contextlib import nullcontext
from datetime import timedelta

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision import datasets, transforms

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")
전체_배치 = 256                                      # 한 걸음에 반영하는 사진 수는 언제나 256장


class 옷CNN(nn.Module):
    """9장 9.5절의 작은 CNN."""

    def __init__(self) -> None:
        super().__init__()
        self.특징 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.분류 = nn.Sequential(
            nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.분류(self.특징(x))


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


def 준비() -> tuple[torch.device, bool]:
    """torchrun으로 실행됐으면 분산을 시작하고, 아니면 장치만 고른다."""
    if "RANK" not in os.environ:
        return 장치_고르기(), False
    if torch.cuda.is_available():
        장치 = torch.device("cuda", int(os.environ["LOCAL_RANK"]))
        torch.cuda.set_device(장치)
        dist.init_process_group("nccl", timeout=timedelta(seconds=120), device_id=장치)
    else:
        장치 = torch.device("cpu")
        dist.init_process_group("gloo", timeout=timedelta(seconds=120))
    return 장치, True


def 옷_데이터(학습: bool) -> datasets.FashionMNIST:
    return datasets.FashionMNIST(데이터_폴더, train=학습, download=True,
                                 transform=transforms.ToTensor())


def 정확도(모델: nn.Module, 장치: torch.device) -> float:
    모델.eval()
    맞힘 = 0
    with torch.no_grad():
        for x, y in DataLoader(옷_데이터(False), batch_size=1000):
            맞힘 += (모델(x.to(장치)).argmax(1) == y.to(장치)).sum().item()
    return 맞힘 / 10_000


def 한_에폭(모델: nn.Module, 로더: DataLoader, 옵티마이저: torch.optim.Optimizer,
           장치: torch.device, 누적: int, 분산: bool) -> torch.Tensor:
    """한 에폭 학습하고 [손실 합, 개수]를 돌려준다. 배치를 누적 횟수만큼 나눠 기울기를 모은다."""
    모델.train()
    합계 = torch.zeros(2, device=장치)
    for x, y in 로더:
        x, y = x.to(장치), y.to(장치)
        옵티마이저.zero_grad()
        for i, (xb, yb) in enumerate(zip(x.chunk(누적), y.chunk(누적))):
            건너뛰기 = 분산 and i < 누적 - 1                   # 마지막 조각에서만 통신
            with 모델.no_sync() if 건너뛰기 else nullcontext():
                손실 = nn.functional.cross_entropy(모델(xb), yb)
                (손실 / 누적).backward()
            합계[0] += 손실.detach() * len(yb)
            합계[1] += len(yb)
        옵티마이저.step()
    return 합계


def main() -> None:
    인자 = argparse.ArgumentParser()
    인자.add_argument("--누적", type=int, default=1)
    인자.add_argument("--에폭", type=int, default=5)
    설정 = 인자.parse_args()

    장치, 분산 = 준비()
    rank = dist.get_rank() if 분산 else 0
    전체 = dist.get_world_size() if 분산 else 1
    if rank == 0:
        옷_데이터(True), 옷_데이터(False)              # 내려받기는 한 프로세스만
    if 분산:
        dist.barrier()

    학습셋 = 옷_데이터(True)
    GPU당 = 전체_배치 // 전체
    if 분산:
        샘플러 = DistributedSampler(학습셋, shuffle=True, seed=0)
        로더 = DataLoader(학습셋, batch_size=GPU당, sampler=샘플러)
    else:
        샘플러 = None
        로더 = DataLoader(학습셋, batch_size=GPU당, shuffle=True,
                        generator=torch.Generator().manual_seed(0))

    torch.manual_seed(0)
    모델 = 옷CNN().to(장치)
    if 분산:
        모델 = DDP(모델)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    if 장치.type == "cuda":
        torch.cuda.reset_peak_memory_stats(장치)

    손실들 = []
    시작 = time.perf_counter()
    for 에폭 in range(설정.에폭):
        if 샘플러 is not None:
            샘플러.set_epoch(에폭)
        합계 = 한_에폭(모델, 로더, 옵티마이저, 장치, 설정.누적, 분산)
        if 분산:
            dist.all_reduce(합계)
        손실들.append(round((합계[0] / 합계[1]).item(), 4))
    걸린_시간 = time.perf_counter() - 시작

    if rank == 0:
        원본 = 모델.module if 분산 else 모델
        조각 = f" ({GPU당 // 설정.누적}장 × {설정.누적}번 누적)" if 설정.누적 > 1 else ""
        메모리 = (f"{torch.cuda.max_memory_allocated(장치) / 1024 ** 2:.0f} MB"
                if 장치.type == "cuda" else "-")
        print(f"[{장치.type} {전체}개 × {GPU당}장{조각}]")
        print(f"  에폭별 학습 손실 {손실들}")
        print(f"  시험 정확도 {정확도(원본, 장치):.2%}, 학습 {걸린_시간:.1f}초, GPU당 최고 메모리 {메모리}")
    if 분산:
        dist.destroy_process_group()


if __name__ == "__main__":
    main()
```

세 가지 방법으로 실행합니다. `--누적` 같은 명령줄 인자는 표준 라이브러리의 `argparse`로 받았어요. `add_argument`로 옵션 이름과 자료형, 기본값을 정해 두면 `parse_args()`가 명령줄을 읽어 `설정.누적`처럼 꺼내 쓰게 해 줍니다. 설정을 명령줄로 바꾸는 방법은 다음 18장 18.2절에서 자세히 다뤄요.

```bash
uv run python b13_실습.py          # 1) GPU 하나, 256장씩
uv run python b13_실습.py --누적 4  # 2) GPU 하나, 64장씩 4번 누적
uv run torchrun --nproc_per_node=2 --master_addr=127.0.0.1 --master_port=29500 b13_실습.py   # 3) GPU 2개 × 128장
```

```text
[cuda 1개 × 256장]
  에폭별 학습 손실 [0.5886, 0.3498, 0.2963, 0.2714, 0.2485]
  시험 정확도 89.43%, 학습 6.5초, GPU당 최고 메모리 104 MB
[cuda 1개 × 256장 (64장 × 4번 누적)]
  에폭별 학습 손실 [0.5891, 0.3505, 0.297, 0.2718, 0.2486]
  시험 정확도 89.56%, 학습 8.8초, GPU당 최고 메모리 45 MB
[cuda 2개 × 128장]
  에폭별 학습 손실 [0.5912, 0.3494, 0.3027, 0.2752, 0.2531]
  시험 정확도 89.76%, 학습 4.0초, GPU당 최고 메모리 66 MB
```

이 책의 실행 환경(RTX 4090 두 장)에서 잰 값입니다. 표로 정리하면 이렇습니다.

| 방법 | 시험 정확도 | 학습 시간 (5에폭) | GPU당 최고 메모리 |
|---|---|---|---|
| GPU 1개 × 256장 | 89.43% | 6.5초 | 104MB |
| GPU 1개 × (64장 × 4번 누적) | 89.56% | 8.8초 | 45MB |
| GPU 2개 × 128장 | 89.76% | 4.0초 | 66MB |

- **정확도**: 세 방법 모두 89%대로 비슷합니다. 1번과 2번은 같은 순서로 같은 256장을 봤으니 에폭별 손실이 0.5886과 0.5891, 0.2485와 0.2486처럼 거의 같아요. 17.2절에서는 CPU라 끝자리까지 같았는데, 여기서는 GPU 계산의 끝자리 흔들림이 다섯 에폭 동안 조금 쌓였습니다. 3번은 `DistributedSampler`가 데이터를 섞는 순서가 달라서 손실이 조금 다르게 흘렀지만 같은 수준에 도착했어요.
- **메모리**: 누적한 2번이 104MB에서 45MB로 가장 적습니다. 한 번에 64장만 올리니까요. DDP는 GPU마다 128장이라 그 중간이고요.
- **시간**: 누적은 6.5초에서 8.8초로 느려졌습니다. 이 작은 CNN에게 64장은 GPU를 바쁘게 만들기에 너무 적어서, 17.2절의 ResNet18과 달리 조각을 나눈 만큼 손해를 봤어요. DDP는 4.0초로 1.6배 빨라졌는데, 17.9절에서 작은CNN의 순수 계산은 1.1배밖에 안 빨라졌던 것과 다르죠? 이 실습은 GPU 안의 난수가 아니라 `DataLoader`가 CPU에서 사진을 꺼내 오는데, 프로세스가 둘이면 **데이터를 꺼내는 일도 둘이 나눠** 하기 때문입니다.

사진도 모델도 작아서, 이 실습에서는 GPU 계산보다 데이터를 꺼내는 쪽이 시간을 더 잡아먹고 있을 것 같아요. 짐작으로 끝내지 말고 재 보겠습니다. 실습의 부품을 그대로 가져와, 한 걸음을 "배치를 기다린 시간"과 "GPU로 옮겨 계산·통신을 끝낸 시간"으로 나눠 재는 코드입니다. `b13_실습.py`와 같은 폴더에 `b16_시간_나누기.py`로 저장하고, GPU 하나는 `uv run python b16_시간_나누기.py`, 두 개는 위의 3번과 같은 `uv run torchrun` 명령으로 실행했어요. GPU가 없으면 동기화를 건너뛰고 CPU나 MPS에서도 돌아갑니다.

```python
"""b13 실습의 한 걸음을 '데이터 기다림'과 'GPU 계산·통신'으로 나눠 잰다."""
import time

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler

from b13_실습 import 옷_데이터, 옷CNN, 전체_배치, 준비      # 실습의 부품을 그대로 쓴다

에폭_수 = 5


def main() -> None:
    장치, 분산 = 준비()
    rank = dist.get_rank() if 분산 else 0
    전체 = dist.get_world_size() if 분산 else 1
    if rank == 0:
        옷_데이터(True)
    if 분산:
        dist.barrier()
    학습셋 = 옷_데이터(True)
    GPU당 = 전체_배치 // 전체
    샘플러 = DistributedSampler(학습셋, shuffle=True, seed=0) if 분산 else None
    로더 = DataLoader(학습셋, batch_size=GPU당, sampler=샘플러, shuffle=샘플러 is None)
    torch.manual_seed(0)
    모델 = 옷CNN().to(장치)
    if 분산:
        모델 = DDP(모델)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    손실_함수 = nn.CrossEntropyLoss()
    데이터_시간 = 계산_시간 = 0.0
    걸음 = 0
    시작 = time.perf_counter()
    for 에폭 in range(에폭_수):
        if 샘플러 is not None:
            샘플러.set_epoch(에폭)
        t0 = time.perf_counter()
        for x, y in 로더:
            t1 = time.perf_counter()                  # 여기까지가 배치를 기다린 시간
            x, y = x.to(장치), y.to(장치)
            옵티마이저.zero_grad()
            손실_함수(모델(x), y).backward()
            옵티마이저.step()
            if 장치.type == "cuda":                  # GPU 일이 정말 끝날 때까지 (16장 16.2절)
                torch.cuda.synchronize()
            elif 장치.type == "mps":
                torch.mps.synchronize()
            t2 = time.perf_counter()                  # 여기까지가 계산과 통신 시간
            데이터_시간 += t1 - t0
            계산_시간 += t2 - t1
            걸음 += 1
            t0 = time.perf_counter()
    전체_시간 = time.perf_counter() - 시작
    if rank == 0:
        print(f"[GPU {전체}개 × {GPU당}장] 걸음 {걸음}번, 전체 {전체_시간:.1f}초 = "
              f"데이터 기다림 {데이터_시간:.1f}초 + GPU 계산·통신 {계산_시간:.1f}초 "
              f"(걸음당 데이터 {데이터_시간 / 걸음 * 1000:.1f}ms, 계산 {계산_시간 / 걸음 * 1000:.1f}ms)")
    if 분산:
        dist.destroy_process_group()


if __name__ == "__main__":
    main()
```

```text
[GPU 1개 × 256장] 걸음 1175번, 전체 6.8초 = 데이터 기다림 5.4초 + GPU 계산·통신 1.5초 (걸음당 데이터 4.6ms, 계산 1.3ms)
[GPU 2개 × 128장] 걸음 1175번, 전체 4.9초 = 데이터 기다림 2.7초 + GPU 계산·통신 2.2초 (걸음당 데이터 2.3ms, 계산 1.9ms)
```

짐작이 맞았습니다. GPU 하나일 때 6.8초 중 5.4초, 거의 4분의 3이 **배치를 기다린 시간**이에요. GPU는 걸음마다 1.3ms만 일하고 4.6ms를 놀았습니다. 프로세스가 둘이 되자 각자 절반의 사진만 꺼내니 기다림이 2.7초로 절반이 됐고, 대신 계산·통신 시간은 1.5초에서 2.2초로 늘었어요. 17.6절의 통신 비용이 걸음마다 붙었기 때문입니다. 늘어난 0.7초보다 줄어든 2.7초가 커서 전체로는 빨라진 거예요. 걸음마다 `synchronize`로 기다리게 해서 위 표보다 조금씩 느리게 나오지만, 무엇이 시간을 잡아먹는지는 분명하죠. 그렇다면 GPU를 늘리기 전에 GPU 하나에서 7장 7.10절의 `num_workers`부터 늘려 보는 게 순서입니다. 16장 16.13절 실습에서 일꾼 8명으로 5.2배 빨라진 것과 같은 이야기예요.

이렇게 숫자를 나란히 놓고 보면 "GPU를 늘리면 빨라진다", "누적하면 느려진다" 같은 한 줄 요약이 모두 반쯤만 맞는다는 걸 알 수 있습니다. 어디가 병목인지(계산, 통신, 데이터)를 재 보고 고르는 것이 이 장에서 가져갈 가장 중요한 습관이에요.

## 17.14 정리와 다음 장 미리보기

이 장에서는 GPU 메모리를 아끼는 법과 GPU를 늘리는 법을 직접 재 가며 익혔습니다.

- **학습 메모리의 내역**: 파라미터 + 기울기 + 옵티마이저 상태 + 활성화. Adam이면 활성화를 빼고도 파라미터의 4배(float32 기준 파라미터당 16바이트). 메모리 오류는 가장 높은 순간에 난다
- **그래디언트 누적**: 손실을 누적 횟수로 나누고, step·zero_grad는 누적이 끝난 뒤 한 번. 큰 배치와 같은 기울기(배치 정규화 제외), 활성화 메모리가 조각 크기만큼 준다
- **활성화 체크포인팅**: 층의 입력만 저장하고 backward 때 다시 계산. 이 장의 트랜스포머에서 메모리 7.78GB → 2.43GB, 시간 +34%, 기울기는 같다
- **분산의 낱말**: GPU마다 프로세스 하나, rank·world size, 백엔드(`nccl`/`gloo`), all-reduce, barrier. `uv run torchrun --nproc_per_node=N --master_addr=127.0.0.1`
- **DDP**: `DistributedSampler`와 `set_epoch`, `DDP(모델)`, 출력·평가·저장은 rank 0만, 저장은 `모델.module.state_dict()`. 같은 전체 배치면 1 GPU와 같은 결과
- **통신 비용**: 이 책의 서버(NVLink 없음, PCIe 3세대 4차선)에서 all-reduce는 초당 약 2GB. 이득은 계산 시간 대 통신 시간으로 정해져서, 작은 계산에서는 2 GPU가 오히려 느렸다(0.59배). DDP는 버킷으로 통신을 계산 뒤에 숨긴다
- **no_sync**: 누적과 DDP를 합칠 때 마지막 조각에서만 통신. 이 장에서 처리량이 두 배 넘게 늘었다
- **FSDP·ZeRO**: 파라미터·기울기·옵티마이저 상태까지 나눠 담아 GPU당 메모리를 줄이고, 그 대가로 통신이 늘어난다. 텐서 병렬·파이프라인 병렬은 거대 모델용
- **흔한 오류**: 한 프로세스만 통신을 부르면 멈춘다(`timeout`으로 오류로 바꾸기), 호스트 이름 문제는 `--master_addr`, 드라이버와 CUDA 빌드 맞추기

GPU를 여러 장 쓰기 시작하면 실험 하나하나가 비싸집니다. 몇 시간짜리 학습이 중간에 끊기기도 하고, 같은 설정을 GPU 개수만 바꿔 다시 돌리기도 하죠. 그럴수록 "그 결과가 어떤 설정, 어떤 코드, 어떤 환경에서 나왔는지"를 남겨 두는 일이 중요해집니다. 다음 18장에서는 설정을 코드 밖으로 빼고, 체크포인트에서 똑같이 이어 가고, 실험 기록을 남기고 비교하는 **실험 관리와 재현성**을 다룹니다.
