# Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게

> **학습 목표**  
> - GPU가 빠른 이유와, GPU가 오히려 느린 경우를 설명하기
> - 비동기 실행을 이해하고 GPU 시간을 올바르게 재기(동기화, 준비 운동, CUDA 이벤트)
> - GPU 메모리를 들여다보고, 메모리 부족(OOM) 오류를 재현하고 대처하기
> - 고정 메모리와 `non_blocking`으로 CPU와 GPU 사이 복사 비용 줄이기
> - 혼합 정밀도(`autocast`, `bfloat16`, `float16`과 `GradScaler`)와 TF32로 학습을 빠르게 하기
> - `torch.compile`의 준비 시간과 이득, 그래프 끊김을 이해하기
> - `scaled_dot_product_attention`과 프로파일러로 시간이 새는 곳을 찾아 고치기

---

## 들어가며: 같은 요리, 다른 주방

15장의 확산 모델을 학습시키면서 몇 분씩 기다렸던 것 기억나세요? 모델을 조금만 키워도 기다리는 시간은 금방 몇 배가 됩니다. 이럴 때 가장 먼저 떠오르는 생각은 "더 좋은 GPU를 사야 하나?"예요. 그런데 같은 GPU, 같은 모델로도 **몇 배씩 빨라지는 경우가 아주 흔합니다.** 느렸던 이유가 GPU가 아니라 다른 곳에 있었던 거죠.

식당 주방을 떠올려 보세요. 화구가 아무리 좋아도 재료 손질하는 사람이 한 명뿐이면 화구는 대부분 꺼져 있고, 볶음밥 한 그릇마다 불을 켰다 껐다 하면 시간이 다 갑니다. 딥러닝 학습도 똑같아요. 데이터를 준비하는 쪽, GPU에 일을 맡기는 방식, 숫자를 담는 칸의 크기, 계산을 묶는 방식이 모두 속도를 좌우합니다.

이 장에서는 이 모든 것을 **직접 재 보면서** 하나씩 고칩니다. 그래서 이 장의 예제는 지금까지와 달리 NVIDIA GPU가 달린 서버에서 실행했어요. 이 책의 실행 환경은 이렇습니다.

```python
import torch

print("PyTorch    :", torch.__version__)
print("CUDA 빌드  :", torch.version.cuda)
print("GPU 개수   :", torch.cuda.device_count())
속성 = torch.cuda.get_device_properties(0)
print("GPU 이름   :", 속성.name)
print(f"GPU 메모리 : {속성.total_memory / 1024**3:.1f} GB")
print("SM 개수    :", 속성.multi_processor_count)
print("계산 능력  :", f"{속성.major}.{속성.minor}")
print("bfloat16   :", torch.cuda.is_bf16_supported())
```

```text
PyTorch    : 2.14.1+cu126
CUDA 빌드  : 12.6
GPU 개수   : 2
GPU 이름   : NVIDIA GeForce RTX 4090
GPU 메모리 : 23.6 GB
SM 개수    : 128
계산 능력  : 8.9
bfloat16   : True
```

RTX 4090 두 장이 달린 리눅스 서버이고, 이 장에서는 그중 한 장(0번)만 씁니다. 두 장을 함께 쓰는 법은 17장의 주제예요. `계산 능력 8.9`는 NVIDIA가 GPU 세대마다 붙인 번호로, 8.0 이상이면 이 장에서 다룰 `bfloat16`과 TF32를 하드웨어가 직접 지원합니다.

`CUDA 빌드: 12.6`도 눈여겨보세요. 처음에는 `uv add torch`가 기본으로 설치하는 CUDA 13용 PyTorch를 썼는데, `NVIDIA driver on your system is too old`라는 오류가 나며 GPU를 찾지 못했습니다. 이 서버의 드라이버가 CUDA 12.4까지만 지원했기 때문이에요. 그래서 부록 A.4절의 방법대로 PyTorch 인덱스를 CUDA 12.6용(`cu126`)으로 지정해 설치했습니다. "드라이버가 지원하는 CUDA 버전에 맞는 빌드를 고른다"는 말이 실제로 이런 뜻입니다.

> **Q. NVIDIA GPU가 없으면 이 장은 어떻게 따라 하나요?**
> 이 장의 예제는 대부분 `cuda` 장치를 직접 씁니다. GPU 메모리 통계, 고정 메모리, `GradScaler`, 플래시 어텐션처럼 NVIDIA GPU에서만 의미가 있는 기능을 재 보는 장이라서요. 가장 쉬운 방법은 부록 A.5절의 Colab에서 무료 GPU를 빌려 실행하는 것입니다. 다만 Colab에서 흔히 받는 T4는 계산 능력이 7.5라서, 이 장의 기능 몇 가지는 하드웨어가 지원하지 않아요. 절마다 어디서 돌아가는지 정리하면 이렇습니다("그대로는 안 됨"은 코드가 `cuda`를 직접 써서 고치지 않으면 멈춘다는 뜻이에요).
>
> | 절 | Colab T4 | 맥(MPS) | CPU만 |
> |---|---|---|---|
> | 16.1~16.5 시간 재기, 메모리, 고정 메모리 | 돌아감 | 그대로는 안 됨 | 그대로는 안 됨 |
> | 16.6 자료형 범위, `autocast` 예제 | 돌아감 | 돌아감 | 돌아감(`bfloat16`으로) |
> | 16.6 `GradScaler`, 세 방식 비교 | 돌아감. `bfloat16`은 하드웨어 지원이 없어 빨라지지 않음 | 그대로는 안 됨 | 그대로는 안 됨 |
> | 16.7 TF32 | 돌아가지만 빨라지지 않음(계산 능력 8.0 미만) | 그대로는 안 됨 | 그대로는 안 됨 |
> | 16.8 `torch.compile` 앞의 두 예제 | 돌아감 | `"cuda"`를 `"mps"`로, `torch.cuda.synchronize`를 `torch.mps.synchronize`로 바꾸면 돌아감 | 장치를 `"cpu"`로 바꾸면 돌아가지만 아주 느림 |
> | 16.9 SDPA | 플래시만 빼고 돌아감(계산 능력 8.0 이상이 필요해서 코드가 알아서 뺌) | 그대로는 안 됨 | 그대로는 안 됨 |
> | 16.10~16.13 프로파일러, 데이터 로더, 실습 | 돌아감. CPU 코어가 적으니 `num_workers`는 `os.cpu_count()`보다 크게 잡지 않기 | 그대로는 안 됨 | 그대로는 안 됨 |
>
> 맥과 CPU 칸은 이 책의 맥(M4 Max)에서 직접 돌려 확인했고, Colab 칸은 T4의 계산 능력과 PyTorch가 지원하는 범위로 정리했습니다. GPU 종류가 다르니 숫자는 다르게 나오지만, 무엇이 왜 빨라지는지는 같은 방법으로 확인할 수 있어요.

## 16.1 GPU는 왜 빠를까요

### 교수 한 명과 학생 만 명

수학 교수 한 명과 초등학생 만 명이 계산 시합을 한다고 해 봅시다. 문제가 "숫자 1억 개에 각각 2를 곱하고 1을 더하라"라면 누가 이길까요? 학생들입니다. 문제 하나하나는 쉽고, 서로 상관이 없으니 만 명이 나눠서 동시에 풀면 끝나거든요. 하지만 문제가 "앞의 답을 받아서 다음 계산을 하라"처럼 줄줄이 이어진다면 어떨까요? 한 번에 한 명밖에 일할 수 없으니, 학생 만 명이 있어도 소용이 없고 똑똑한 교수 한 명이 훨씬 빠릅니다.

CPU는 교수, GPU는 학생 만 명입니다. CPU에는 복잡한 일을 아주 빨리 처리하는 코어가 수십 개, GPU에는 단순한 계산을 하는 작은 코어가 수천~수만 개 있어요. 앞에서 본 `SM 개수 128`이 GPU 안의 작은 공장 수이고, 공장마다 계산 일꾼이 수십 명씩 있습니다. 딥러닝 계산은 대부분 "숫자 수백만 개에 같은 계산을 한꺼번에"라 GPU와 궁합이 좋아요. 두 종류의 일을 시켜 보겠습니다.

```python
import time

import torch


def 평균_시간(함수, 반복: int = 10) -> float:
    """준비 운동 한 번 뒤 여러 번 돌려, 한 번에 걸린 평균 시간(ms)을 잰다."""
    함수()
    torch.cuda.synchronize()                  # GPU 일이 끝날 때까지 기다린다 (16.2절)
    시작 = time.perf_counter()
    for _ in range(반복):
        함수()
    torch.cuda.synchronize()
    return (time.perf_counter() - 시작) / 반복 * 1000


def 작은_일_천_번(x: torch.Tensor) -> torch.Tensor:
    """앞의 결과가 있어야 다음을 할 수 있는 작은 계산을 1,000번."""
    for _ in range(1000):
        x = (x * 2 + 1).sqrt()
    return x


큰_cpu = torch.rand(100_000_000)              # 숫자 1억 개
큰_gpu = 큰_cpu.to("cuda")
작은_cpu = torch.rand(10)                     # 숫자 10개
작은_gpu = 작은_cpu.to("cuda")

print(f"큰 일 한 번   (1억 개)   CPU {평균_시간(lambda: (큰_cpu * 2 + 1).sqrt()):7.2f} ms"
      f" | GPU {평균_시간(lambda: (큰_gpu * 2 + 1).sqrt()):7.2f} ms")
print(f"작은 일 천 번 (10개씩)   CPU {평균_시간(lambda: 작은_일_천_번(작은_cpu)):7.2f} ms"
      f" | GPU {평균_시간(lambda: 작은_일_천_번(작은_gpu)):7.2f} ms")
```

```text
큰 일 한 번   (1억 개)   CPU   60.69 ms | GPU    2.61 ms
작은 일 천 번 (10개씩)   CPU    3.78 ms | GPU    7.73 ms
```

숫자 1억 개에 같은 계산을 하는 **큰 일 한 번**은 CPU가 60ms, GPU가 2.6ms로 GPU가 20배 넘게 빠릅니다. 그런데 숫자 10개짜리 계산을 앞의 결과를 받아 1,000번 이어 하는 **작은 일 천 번**은 CPU가 3.8ms, GPU가 7.7ms로 오히려 GPU가 두 배쯤 느려요.

GPU가 느린 이유는 계산 때문이 아닙니다. 파이썬이 GPU에 "이 계산을 해라"라고 일감을 하나 맡길 때마다 몇 마이크로초(µs)의 준비 비용이 들어요. 계산 한 줄(`x * 2`, `+ 1`, `.sqrt()`)이 일감 하나이니 1,000번 반복하면 일감이 3,000개, 7.7ms를 3,000으로 나누면 일감 하나에 약 2.6µs입니다. 숫자 10개 계산은 GPU에게 눈 깜짝할 일이라, 시간이 거의 전부 **일감을 맡기는 비용**으로 나간 거예요. 이 비용을 **커널 실행 비용(kernel launch overhead)** 이라고 부릅니다. GPU에서 실행되는 계산 하나를 **커널(kernel)** 이라고 하거든요.

여기서 이 장 전체를 꿰뚫는 두 가지 교훈이 나옵니다.

- **GPU에는 큰 일을 한꺼번에 맡겨야 합니다.** 배치를 키우고(16.11절), 작은 계산 여러 개를 하나로 합치는 것(16.8절)이 모두 이 원칙에서 나와요.
- **GPU가 쉬지 않게 해야 합니다.** 일감을 맡기는 쪽(파이썬, 데이터 준비)이 느리면 GPU는 기다립니다(16.10절).

`평균_시간` 함수 안의 `torch.cuda.synchronize()`가 궁금했을 텐데, 이것 없이 재면 숫자가 엉터리가 됩니다. 바로 다음 절에서 그 이유를 봐요.

## 16.2 GPU 시간 제대로 재기

### 맡기고 돌아오는 파이썬

4장 4.8절에서 "GPU 일이 끝날 때까지 기다린 뒤 재야 한다"고 했습니다. 왜 그래야 하는지 이번에는 일부러 틀리게 재서 확인해 보겠습니다. 8192 × 8192 행렬 곱을 다섯 가지 방법으로 쟀어요.

```python
import time

import torch

a = torch.randn(8192, 8192, device="cuda")
b = torch.randn(8192, 8192, device="cuda")

시작 = time.perf_counter()
c = a @ b                                     # 이 크기의 행렬 곱은 처음
torch.cuda.synchronize()
print(f"① 첫 호출 (준비 포함)   : {(time.perf_counter() - 시작) * 1000:8.2f} ms")

시작 = time.perf_counter()
c = a @ b
print(f"② 기다리지 않고 잼      : {(time.perf_counter() - 시작) * 1000:8.2f} ms")
torch.cuda.synchronize()

시작 = time.perf_counter()
c = a @ b
torch.cuda.synchronize()                      # GPU가 다 끝낼 때까지 기다린 뒤 잰다
print(f"③ synchronize 후 잼     : {(time.perf_counter() - 시작) * 1000:8.2f} ms")

# ④ CUDA 이벤트: GPU의 작업 줄에 시작·끝 표시를 끼워 넣는다
시작_표시 = torch.cuda.Event(enable_timing=True)
끝_표시 = torch.cuda.Event(enable_timing=True)
시작_표시.record()
c = a @ b
끝_표시.record()
끝_표시.synchronize()                         # 끝 표시까지 지나갈 때까지 기다린다
print(f"④ CUDA 이벤트           : {시작_표시.elapsed_time(끝_표시):8.2f} ms")

# ⑤ 결과를 CPU로 꺼내는 순간(.item(), print, .cpu()) 저절로 기다리게 된다
시작 = time.perf_counter()
c = a @ b
합계 = c.sum().item()
print(f"⑤ .item()까지 잼        : {(time.perf_counter() - 시작) * 1000:8.2f} ms")
```

```text
① 첫 호출 (준비 포함)   :    49.09 ms
② 기다리지 않고 잼      :     0.16 ms
③ synchronize 후 잼     :    19.67 ms
④ CUDA 이벤트           :    20.69 ms
⑤ .item()까지 잼        :    27.38 ms
```

같은 행렬 곱인데 0.16ms부터 49ms까지 숫자가 300배 넘게 차이 납니다. 하나씩 보죠.

- **② 기다리지 않고 잼: 0.16ms.** 곱셈과 덧셈이 1조 번 넘게 필요한 계산이 0.16ms에 끝났다면 초당 7,000조 번 계산한 셈이니 말이 안 되죠. 파이썬은 GPU에 일을 **맡기기만 하고 바로 돌아와서** 시계를 멈춰 버렸습니다. 이것을 **비동기 실행**이라고 해요. 주문서를 주방에 넣는 시간만 재고 "요리 0.2초 만에 완성!"이라고 하는 셈입니다.
- **③ synchronize 후 잼: 19.7ms.** `torch.cuda.synchronize()`는 "GPU가 맡은 일을 모두 끝낼 때까지 기다려라"라는 뜻입니다. 이렇게 재야 진짜 계산 시간이에요.
- **① 첫 호출: 49ms.** 처음 계산할 때는 행렬 곱을 담당하는 라이브러리(cuBLAS)가 준비 작업을 하고, 이 크기에 맞는 계산 방법을 고르느라 시간이 더 듭니다. 그래서 측정 전에 몇 번 미리 돌려 두는 **준비 운동(warm-up)** 이 필요해요.
- **④ CUDA 이벤트: 20.7ms.** GPU의 작업 줄 사이에 "여기서 시작", "여기서 끝"이라는 표시를 끼워 넣고, GPU가 그 표시를 지나간 시각의 차이를 잽니다. 파이썬 시계를 쓰지 않으니 GPU 안에서 걸린 시간만 정확히 나와요.
- **⑤ `.item()`까지 잼: 27.4ms.** 결과를 CPU로 꺼내는 순간에는 파이썬이 저절로 기다립니다. 값이 있어야 꺼낼 수 있으니까요. `.item()`, `.cpu()`, `print(텐서)`가 모두 그렇습니다. ③보다 7ms쯤 더 걸렸는데, 숫자 6,700만 개의 합계는 1ms도 안 걸리니 대부분은 합계 때문이 아니에요. 한 번만 잰 값이라 그때그때의 GPU 상태에 따라 흔들린 것으로 보여요. 그래서 바로 다음에 만들 측정 도구는 여러 번 재서 중앙값을 씁니다.

⑤는 학습 코드에도 중요합니다. 반복문 안에서 `손실.item()`을 매 걸음 부르면 그때마다 CPU가 GPU를 기다려서, 다음 일감을 미리 맡겨 둘 기회가 사라져요. 손실은 몇 걸음에 한 번만 꺼내면 됩니다.

### 재기 도구 만들기

그럼 이 장에서 쓸 측정 함수를 하나 만들어 두겠습니다. 준비 운동을 몇 번 하고, 매번 동기화하며 여러 번 잰 뒤 **중앙값**을 돌려줍니다. 평균 대신 중앙값을 쓰는 이유는, 다른 프로그램이 잠깐 끼어들어 한 번 크게 튄 값이 결과를 흔들지 않게 하기 위해서예요. PyTorch에 들어 있는 측정 도구 `torch.utils.benchmark`와도 비교해 봅니다.

```python
import statistics
import time

import torch
from torch.utils import benchmark


def 재기(함수, 반복: int = 50, 준비: int = 5) -> float:
    """준비 운동 뒤 한 번씩 동기화하며 재고, 중앙값(ms)을 돌려준다."""
    for _ in range(준비):
        함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


n = 4096
a = torch.randn(n, n, device="cuda")
b = torch.randn(n, n, device="cuda")

직접 = 재기(lambda: a @ b)
타이머 = benchmark.Timer(stmt="a @ b", globals={"a": a, "b": b})
측정 = 타이머.blocked_autorange(min_run_time=1.0)   # 1초 이상 알아서 반복해 잰다

print(f"직접 만든 재기()   : 중앙값 {직접:.3f} ms")
print(f"benchmark.Timer    : 중앙값 {측정.median * 1000:.3f} ms ({측정.number_per_run}번씩 {len(측정.times)}묶음)")
연산수 = 2 * n ** 3                                 # 곱하기와 더하기 각각 n³번
print(f"초당 {연산수 / (직접 / 1000) / 1e12:.1f}조 번 계산 (TFLOPS)")
```

```text
직접 만든 재기()   : 중앙값 2.588 ms
benchmark.Timer    : 중앙값 2.601 ms (10번씩 39묶음)
초당 53.1조 번 계산 (TFLOPS)
```

직접 만든 `재기()`와 `benchmark.Timer`가 2.59ms, 2.60ms로 거의 같습니다. `blocked_autorange`는 몇 번씩 몇 묶음을 잴지를 정해진 시간(여기서는 1초) 안에서 알아서 정하고 동기화도 해 줘요.

마지막 줄은 행렬 곱의 계산 횟수를 시간으로 나눈 값입니다. n × n 행렬 두 개를 곱하면 곱셈과 덧셈이 각각 n³번이라 모두 2n³번이에요. 이걸 초당으로 바꾸면 이 GPU가 `float32`로 초당 53조 번(53 TFLOPS) 계산했다는 뜻입니다. **TFLOPS**(테라플롭스)는 "초당 1조 번의 실수 계산"이라는 단위로, GPU 성능을 비교할 때 자주 써요. 16.7절에서 같은 행렬 곱이 이보다 세 배 넘게 빨라지는 것을 보게 됩니다.

> **Q. 4장에서는 `torch.mps.synchronize()`를 썼는데, 맥에서도 같은 원리인가요?**
> 네, 같습니다. Apple MPS도 일을 맡기고 바로 돌아오는 비동기 방식이라 `torch.mps.synchronize()`로 기다린 뒤 재야 해요. 장치에 상관없이 쓰고 싶다면 `if 장치.type == "cuda": torch.cuda.synchronize()`처럼 장치 종류에 따라 골라 부르는 작은 함수를 만들어 두면 됩니다. CPU 계산은 처음부터 끝날 때까지 기다리므로 동기화가 필요 없어요.

## 16.3 CPU와 GPU, 언제 GPU가 이길까요

4장 4.8절 끝에서 "행렬이 작으면 오히려 CPU가 빠를 수도 있다. 16장에서 더 정확히 재 본다"고 약속했습니다. 이제 그 약속을 지킬 차례예요. 행렬 크기를 16부터 4096까지 바꿔 가며 세 가지를 쟀습니다. CPU로 곱하기, 이미 GPU에 있는 행렬을 GPU로 곱하기(계산만), 그리고 CPU에 있는 행렬을 GPU로 옮겨서 곱하고 결과를 다시 CPU로 가져오기(왕복)입니다.

```python
import statistics
import time

import torch


def 재기(함수, 반복: int = 30) -> float:
    """준비 운동 뒤 동기화하며 재고 중앙값(ms)을 돌려준다."""
    for _ in range(5):
        함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


print(f"CPU 스레드 {torch.get_num_threads()}개")
for n in [16, 64, 256, 1024, 4096]:
    a, b = torch.randn(n, n), torch.randn(n, n)
    ga, gb = a.to("cuda"), b.to("cuda")
    cpu = 재기(lambda: a @ b)
    gpu = 재기(lambda: ga @ gb)
    왕복 = 재기(lambda: (a.to("cuda") @ b.to("cuda")).cpu())   # 옮기고, 곱하고, 되가져오기
    print(f"{n:>4}×{n:<4} CPU {cpu:7.3f} | GPU 계산만 {gpu:6.3f} | GPU 왕복 {왕복:6.3f} ms"
          f" → GPU가 {cpu / gpu:4.1f}배 / {cpu / 왕복:3.1f}배")
```

```text
CPU 스레드 24개
  16×16   CPU   0.004 | GPU 계산만  0.007 | GPU 왕복  0.024 ms → GPU가  0.5배 / 0.1배
  64×64   CPU   0.007 | GPU 계산만  0.024 | GPU 왕복  0.074 ms → GPU가  0.3배 / 0.1배
 256×256  CPU   0.049 | GPU 계산만  0.024 | GPU 왕복  0.176 ms → GPU가  2.0배 / 0.3배
1024×1024 CPU   1.748 | GPU 계산만  0.049 | GPU 왕복  1.151 ms → GPU가 35.8배 / 1.5배
4096×4096 CPU 105.370 | GPU 계산만  2.506 | GPU 왕복 30.134 ms → GPU가 42.0배 / 3.5배
```

맨 오른쪽의 두 숫자는 "GPU가 CPU보다 몇 배 빠른가"를 계산만 했을 때와 왕복까지 했을 때로 나눈 것입니다. 1보다 작으면 CPU가 빠르다는 뜻이에요. 이 서버의 CPU는 스레드 24개로 행렬 곱을 나눠 계산합니다(1권 17장에서 본 스레드와 같은 뜻이에요).

- **16 × 16, 64 × 64**: GPU가 계산만 해도 CPU보다 느립니다. 숫자가 몇천 개뿐이라 CPU는 순식간에 끝내는데, GPU는 16.1절의 일감 맡기는 비용만으로 수~수십 µs가 들어요.
- **256 × 256**: 계산만 보면 GPU가 2배 빨라지기 시작합니다. 이 근처가 교차점이에요. 하지만 왕복까지 하면 여전히 CPU가 3배쯤 빠릅니다.
- **1024 × 1024**: 계산만은 36배 빠른데, 왕복까지 하면 1.5배밖에 안 됩니다. 1.15ms 중 대부분이 행렬을 옮기는 시간이라는 뜻이에요.
- **4096 × 4096**: 계산만 하면 CPU 105ms 대 GPU 2.5ms로 42배. 왕복해도 3.5배 빠릅니다.

이 표에서 기억할 것은 숫자 자체보다 **모양**입니다. 작은 계산은 CPU가 빠르고, 클수록 GPU가 압도적이며, 그 사이에는 **옮기는 비용**이 이득을 갉아먹는 구간이 있어요. 그래서 실무에서 지키는 원칙이 두 가지 나옵니다.

1. **한 번 GPU에 올린 것은 GPU에 둡니다.** 모델은 학습 시작 전에 한 번만 옮기고, 중간 결과를 CPU로 가져왔다 다시 보내는 왕복을 만들지 않아요.
2. **옮겨야 한다면 한꺼번에, 그리고 숨겨서 옮깁니다.** 데이터는 배치 단위로 묶어 옮기고, GPU가 계산하는 동안 다음 배치를 옮겨 둡니다. 16.5절의 고정 메모리와 `non_blocking`이 그 방법이에요.

그래서 특성 몇 개짜리 표 데이터를 다루는 아주 작은 신경망은 GPU 서버에서도 CPU가 더 빠를 수 있습니다. 직접 재 보고 고르세요.

## 16.4 GPU 메모리 들여다보기

### 할당과 예약: PyTorch의 메모리 창고

GPU로 학습하다 가장 자주 만나는 오류는 "메모리가 부족하다"는 오류입니다. 메모리를 다루려면 먼저 PyTorch가 GPU 메모리를 어떻게 관리하는지 알아야 해요. 텐서를 만들고 지우면서 두 가지 숫자를 찍어 보겠습니다.

```python
import torch

MB = 1024 ** 2


def 보기(때: str) -> None:
    """지금 할당된 메모리와, PyTorch가 GPU에서 맡아 둔(예약한) 메모리를 보여 준다."""
    print(f"할당 {torch.cuda.memory_allocated() / MB:6.1f} MB | "
          f"예약 {torch.cuda.memory_reserved() / MB:6.1f} MB  ← {때}")


보기("처음")
x = torch.zeros(256, 1024, 1024, device="cuda")      # 2억 6천만 칸 × 4바이트 = 1GB
보기("1GB 텐서를 만든 뒤")
y = x + 1
보기("계산 결과까지")
del x, y
보기("del 한 뒤")
z = torch.zeros(128, 1024, 1024, device="cuda")      # 0.5GB: 맡아 둔 자리를 다시 쓴다
보기("0.5GB를 다시 만든 뒤")
del z
torch.cuda.empty_cache()                              # 맡아 둔 자리를 GPU에 돌려준다
보기("empty_cache 뒤")
print(f"지금까지의 최고 할당: {torch.cuda.max_memory_allocated() / MB:.1f} MB")
```

```text
할당    0.0 MB | 예약    0.0 MB  ← 처음
할당 1024.0 MB | 예약 1024.0 MB  ← 1GB 텐서를 만든 뒤
할당 2048.0 MB | 예약 2048.0 MB  ← 계산 결과까지
할당    0.0 MB | 예약 2048.0 MB  ← del 한 뒤
할당  512.0 MB | 예약 2048.0 MB  ← 0.5GB를 다시 만든 뒤
할당    0.0 MB | 예약    0.0 MB  ← empty_cache 뒤
지금까지의 최고 할당: 2048.0 MB
```

`memory_allocated()`는 지금 **텐서들이 실제로 쓰고 있는** 메모리, `memory_reserved()`는 PyTorch가 GPU에서 **받아 두고 관리하는** 메모리입니다.

1GB 텐서를 만들면 둘 다 1GB가 되고, `x + 1`의 결과까지 만들면 2GB가 됩니다. 4장 4.3절의 계산 그대로예요. 칸 2억 6천만 개(256 × 1024 × 1024) × 4바이트 = 1GB입니다. 그런데 `del`로 지운 뒤를 보세요. 할당은 0인데 예약은 2GB 그대로입니다. 그다음 0.5GB를 만들어도 예약은 늘지 않았어요.

이것이 PyTorch의 **캐싱 할당자(caching allocator)** 입니다. GPU에서 메모리를 받았다 돌려주는 일은 느려서, PyTorch는 다 쓴 메모리를 자기 창고에 두었다가 다음 텐서에 다시 내줘요. 학습은 같은 크기의 텐서를 매 걸음 만들고 버리니, 두 번째 걸음부터는 메모리를 새로 받을 일이 거의 없습니다. `torch.cuda.empty_cache()`는 창고의 빈자리를 GPU에 돌려주는데, 속도에는 도움이 안 되고 다른 프로그램에 자리를 내줄 때나 씁니다.

마지막 줄의 `max_memory_allocated()`는 지금까지 **가장 많이 쓴 순간**의 할당량입니다. 배치를 얼마나 키울 수 있을지는 이 값으로 판단해요. `reset_peak_memory_stats()`로 기록을 지우고 다시 잴 수 있습니다.

> **Q. `nvidia-smi`에 보이는 사용량은 `memory_allocated()`보다 훨씬 큰데요?**
> `nvidia-smi`는 GPU 입장에서 본 사용량이라, PyTorch가 창고에 받아 둔 예약 메모리 전체에 더해 CUDA 자체가 쓰는 기본 메모리(보통 수백 MB)까지 보여 줍니다. 텐서를 다 지웠는데도 `nvidia-smi` 숫자가 줄지 않는 건 대개 캐싱 할당자 때문이니 걱정하지 않아도 돼요. 내 텐서가 실제로 얼마를 쓰는지는 `memory_allocated()`, 창고까지 포함하면 `memory_reserved()`를 보세요.

### 학습 한 걸음은 메모리를 얼마나 쓸까

이제 진짜 모델로 재 보겠습니다. 10장에서 전이 학습에 썼던 ResNet18을 224 × 224 크기의 가짜 사진으로 학습시키며, 배치 크기에 따라 메모리가 어떻게 변하는지 봅니다. 배치 크기와 상관없이 쓰는 파라미터 메모리는 14장 14.6절의 계산법(파라미터 수 × 칸 크기)으로 먼저 구했어요.

```python
import torch
import torch.nn.functional as F
from torchvision.models import resnet18

MB = 1024 ** 2
모델 = resnet18(num_classes=10).to("cuda")
개수 = sum(p.numel() for p in 모델.parameters())
print(f"파라미터 {개수:,}개 × 4바이트 = {개수 * 4 / MB:.1f} MB (14장 14.6절의 계산)")
print(f"모델을 올린 뒤 실제 할당   = {torch.cuda.memory_allocated() / MB:.1f} MB")

for 배치 in [16, 32, 64, 128]:
    x = torch.randn(배치, 3, 224, 224, device="cuda")
    y = torch.randint(0, 10, (배치,), device="cuda")
    전 = torch.cuda.memory_allocated()
    torch.cuda.reset_peak_memory_stats()             # 최고 기록을 지금부터 다시 잰다
    손실 = F.cross_entropy(모델(x), y)
    순전파_뒤 = torch.cuda.memory_allocated()       # backward를 위해 기억해 둔 중간값(활성화)
    손실.backward()
    최고 = torch.cuda.max_memory_allocated()
    모델.zero_grad(set_to_none=True)
    print(f"배치 {배치:>3}: 순전파가 남긴 것 {(순전파_뒤 - 전) / MB:7.1f} MB, "
          f"이 걸음의 최고 {최고 / MB:7.1f} MB")
    del x, y, 손실
```

```text
파라미터 11,181,642개 × 4바이트 = 42.7 MB (14장 14.6절의 계산)
모델을 올린 뒤 실제 할당   = 42.7 MB
배치  16: 순전파가 남긴 것   341.0 MB, 이 걸음의 최고   439.9 MB
배치  32: 순전파가 남긴 것   662.5 MB, 이 걸음의 최고   812.4 MB
배치  64: 순전파가 남긴 것  1321.0 MB, 이 걸음의 최고  1453.0 MB
배치 128: 순전파가 남긴 것  2638.0 MB, 이 걸음의 최고  2828.5 MB
```

파라미터 1,118만 개 × 4바이트 = 42.7MB라는 계산이 실제 할당량과 정확히 맞습니다. 그런데 배치 16장을 순전파하자 메모리가 341MB나 더 늘었어요. 모델 크기의 8배입니다.

5장 5.5절에서 계산 그래프는 backward 때 쓰려고 **순전파의 중간 결과를 기억해 둔다**고 했습니다. 이 중간값을 **활성화(activation)** 라고 불러요. ResNet18은 224 × 224 사진 한 장을 지나가며 층마다 큰 특징 맵을 만들고, 이걸 전부 기억하니 사진 한 장에 20MB쯤 듭니다. 그래서 배치를 두 배로 늘릴 때마다 341 → 663 → 1,321 → 2,638MB로 활성화 메모리도 정확히 두 배씩 늘어요. 최고 메모리는 여기에 backward에서 만드는 기울기와 임시 텐서가 더해진 값입니다.

이 결과가 알려 주는 것은 분명합니다. **학습할 때 메모리를 가장 많이 먹는 것은 모델이 아니라 활성화이고, 활성화는 배치 크기에 비례합니다.** 학습 중 메모리가 파라미터, 기울기, 옵티마이저 상태, 활성화로 어떻게 나뉘는지, 그리고 활성화를 줄이는 방법(활성화 체크포인팅)은 17장에서 자세히 다룹니다.

### 메모리 부족 오류 재현하고 대처하기

그럼 배치를 계속 키우면 어떻게 될까요? 두 배씩 키우다가 메모리 부족 오류(**OOM**, Out Of Memory)가 나면 잡아서 멈추는 코드입니다.

```python
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
```

```text
배치    64: 성공, 최고   1.4 GB
배치   128: 성공, 최고   2.8 GB
배치   256: 성공, 최고   5.4 GB
배치   512: 성공, 최고  10.8 GB
배치  1024: 성공, 최고  21.5 GB
배치  2048: 메모리 부족!
    CUDA out of memory. Tried to allocate 1.53 GiB. GPU 0 has a total capacity of 23.64 GiB of which 1.46 GiB is free.
예약 메모리 정리 뒤: 0.1 GB
배치 1024로 다시 학습: 문제없음
```

배치 1,024까지는 21.5GB로 버텼고, 2,048에서 메모리가 모자랐습니다. 오류 메시지는 "1.53GiB를 받으려 했는데 전체 23.64GiB 중 1.46GiB만 비어 있다"는 뜻이에요. 4장 4.10절의 요령대로 숫자부터, **받으려던 양**과 **남은 양**을 보면 됩니다. 메시지 뒷부분에는 PyTorch가 쓰는 양과 메모리 조각 문제를 줄이는 설정(`PYTORCH_CUDA_ALLOC_CONF`) 안내가 이어져요.

`torch.OutOfMemoryError`는 다른 오류처럼 `try`/`except`로 잡을 수 있습니다(1권 12장). 잡은 뒤 `empty_cache()`로 실패한 걸음이 잡아 둔 자리를 정리하면 예약 메모리가 0.1GB로 돌아오고, 배치 1,024로 학습을 다시 이어 갈 수 있었어요. 다만 실제 학습 코드에서 OOM을 잡아 넘기는 일은 드뭅니다. 보통은 OOM이 나면 멈추고 다음 순서로 대처해요.

1. **배치를 줄입니다.** 가장 확실한 방법입니다. 위 결과처럼 메모리는 배치에 거의 비례하니, 절반으로 줄이면 대개 들어갑니다.
2. **16비트로 계산합니다.** 다음 16.6절의 혼합 정밀도는 활성화를 절반 크기로 저장해서 메모리를 크게 줄여 줘요.
3. **큰 배치의 효과는 나눠서 냅니다.** 작은 배치 여러 개의 기울기를 쌓아 큰 배치처럼 쓰는 그래디언트 누적(5장에서 예고한 기법)과, 활성화를 덜 저장하는 활성화 체크포인팅은 17장에서 다룹니다.
4. **평가 때는 `torch.no_grad()`를 씁니다.** 5장 5.8절의 기록 끄기를 하면 활성화를 저장하지 않아서 메모리가 크게 줄어요.

## 16.5 데이터 옮기는 비용: 고정 메모리와 non_blocking

### 고정 메모리는 왜 빠를까

16.3절에서 옮기는 비용이 GPU의 이득을 갉아먹는 것을 봤습니다. 7장 7.10절에서는 `DataLoader`의 `pin_memory=True`를 "배치를 GPU로 옮기기 좋은 특별한 메모리 영역에 담아 두는 옵션"이라고만 소개하고 넘어갔죠. 이제 정말 그런지 재 보겠습니다.

운영체제는 메모리가 모자라면 오래 안 쓴 내용을 디스크로 잠시 내보내기 때문에, 보통 메모리는 내용이 **어디에 있을지 장담할 수 없습니다.** 그래서 GPU로 보낼 때는 움직이지 않는 임시 공간에 한 번 복사한 뒤 보내요. **고정 메모리(pinned memory)** 는 처음부터 "이 자리에서 움직이지 않는다"고 못 박아 둔 메모리라 이 중간 복사가 필요 없습니다. 택배로 치면 물건을 이미 출고장에 내놓은 것이에요.

```python
import time

import torch

GB = 1024 ** 3
일반 = torch.randn(64, 1024, 1024)                 # 256MB, 보통의 CPU 메모리
고정 = 일반.pin_memory()                           # 같은 내용을 고정(pinned) 메모리에
gpu_텐서 = 일반.to("cuda")
고정_받을_곳 = torch.empty_like(일반).pin_memory()  # GPU에서 받아 올 고정 메모리 자리


def 초당_GB(옮기기, 반복: int = 10) -> float:
    """옮기기를 여러 번 해 보고 초당 몇 GB를 옮겼는지 잰다."""
    옮기기()
    torch.cuda.synchronize()
    시작 = time.perf_counter()
    for _ in range(반복):
        옮기기()
    torch.cuda.synchronize()
    return 일반.numel() * 일반.element_size() * 반복 / (time.perf_counter() - 시작) / GB


print(f"CPU(일반) → GPU: {초당_GB(lambda: 일반.to('cuda')):5.1f} GB/s")
print(f"CPU(고정) → GPU: {초당_GB(lambda: 고정.to('cuda')):5.1f} GB/s")
print(f"GPU → CPU(일반): {초당_GB(lambda: gpu_텐서.to('cpu')):5.1f} GB/s")
print(f"GPU → CPU(고정): {초당_GB(lambda: 고정_받을_곳.copy_(gpu_텐서)):5.1f} GB/s")

# non_blocking=True: 옮기라고 맡기고 기다리지 않고 바로 다음 줄로 간다
for 이름, 원본 in [("일반", 일반), ("고정", 고정)]:
    torch.cuda.synchronize()
    시작 = time.perf_counter()
    도착 = 원본.to("cuda", non_blocking=True)
    맡긴_시간 = (time.perf_counter() - 시작) * 1000
    torch.cuda.synchronize()
    끝난_시간 = (time.perf_counter() - 시작) * 1000
    print(f"{이름} 메모리 + non_blocking: 맡기고 돌아오기까지 {맡긴_시간:6.2f} ms, "
          f"다 옮기기까지 {끝난_시간:6.2f} ms")
```

```text
CPU(일반) → GPU:  11.5 GB/s
CPU(고정) → GPU:  12.2 GB/s
GPU → CPU(일반):   3.7 GB/s
GPU → CPU(고정):  12.3 GB/s
일반 메모리 + non_blocking: 맡기고 돌아오기까지  21.54 ms, 다 옮기기까지  21.65 ms
고정 메모리 + non_blocking: 맡기고 돌아오기까지   0.15 ms, 다 옮기기까지  20.61 ms
```

256MB를 옮겨 본 결과입니다. CPU에서 GPU로 갈 때는 보통 메모리 11.5GB/s, 고정 메모리 12.2GB/s로 차이가 크지 않았어요. 이 방향은 중간 복사가 옮기는 일과 겹쳐 진행되면서 비용이 꽤 가려지는 것으로 보여요. 반대 방향은 달랐습니다. GPU에서 보통 메모리로 받아 올 때는 3.7GB/s, 고정 메모리로 받아 오면 12.3GB/s로 세 배 넘게 빨라요.

12GB/s 근처라는 숫자에도 이유가 있습니다. 이 서버에서 GPU 0번은 CPU와 **PCIe 4.0 x8** 통로로 연결되어 있는데, 이 통로의 이론상 최고 속도가 약 16GB/s예요. 실제로는 그 75% 정도가 나온 것입니다. GPU 안에서 메모리를 읽고 쓰는 속도(메모리 대역폭)는 1,000GB/s 수준이니(16.8절), **GPU 밖으로 나가는 길은 GPU 안보다 수십 배 좁습니다.** 16.3절에서 왕복이 그렇게 비쌌던 이유예요. 17장에서 GPU 두 장이 서로 기울기를 주고받을 때도 이 좁은 길이 다시 문제가 됩니다.

### non_blocking: 맡기고 다른 일 하기

마지막 두 줄이 이 절의 핵심입니다. `.to("cuda", non_blocking=True)`는 "옮기라고 맡기고 기다리지 말고 돌아와라"는 뜻이에요. 그런데 보통 메모리에서는 맡기고 돌아오기까지 21.5ms, 즉 다 옮길 때까지 그대로 기다렸습니다. 중간 복사를 CPU가 직접 해야 하니 비동기로 할 수가 없거든요. 고정 메모리에서는 0.15ms 만에 돌아왔고, 실제 복사는 그 뒤 20ms 동안 GPU 쪽에서 따로 진행됐습니다. **`non_blocking`은 고정 메모리와 함께 써야 효과가 있습니다.**

CPU가 0.15ms 만에 풀려나면 무엇이 좋을까요? 그동안 다음 배치를 준비하거나 GPU에 다음 계산을 맡겨 둘 수 있습니다. 그래서 GPU 학습 코드는 흔히 이렇게 씁니다.

```python
로더 = DataLoader(데이터셋, batch_size=256, shuffle=True,
                  num_workers=8, pin_memory=True)      # 일꾼이 배치를 고정 메모리에 담아 준다
for x, y in 로더:
    x = x.to(장치, non_blocking=True)                   # 맡기고 바로 다음 줄로
    y = y.to(장치, non_blocking=True)
    ...
```

`pin_memory=True`를 주면 DataLoader가 배치를 고정 메모리에 담아서 건네주고, 우리는 `non_blocking=True`로 옮기기만 하면 됩니다. 같은 GPU 작업 줄 안에서는 순서가 지켜지므로, 복사가 끝나기 전에 모델 계산이 그 텐서를 읽는 일은 없어요. 반대 방향(GPU → CPU)에 `non_blocking=True`를 쓰면 복사가 끝나기 전에 값을 읽을 위험이 있으니, 결과를 가져올 때는 그냥 `.cpu()`나 `.item()`을 쓰세요.

> **Q. 그럼 모든 텐서를 고정 메모리에 두면 더 빠르지 않나요?**
> 고정 메모리는 운영체제가 디스크로 내보낼 수 없는 메모리라, 많이 잡으면 컴퓨터 전체의 다른 프로그램이 쓸 메모리가 줄어듭니다. 그래서 데이터셋 전체가 아니라 **GPU로 보낼 배치만** 고정 메모리에 두는 것이 원칙이고, `pin_memory=True`가 바로 그렇게 해 줘요. 7장 7.10절에서 말했듯 Apple MPS에서는 고정 메모리가 지원되지 않아 경고만 나오니 맥에서는 이 옵션을 빼세요.

## 16.6 혼합 정밀도: 16비트로 계산하기

### 16비트 두 가지: float16과 bfloat16

4장 4.3절에서 딥러닝의 기본이 32비트인 이유를 이야기하면서 "요즘은 16비트까지 내려서 속도를 더 얻는다, 16장에서 이어진다"고 했습니다. 칸이 절반이면 메모리도 절반, 옮기는 시간도 절반이고, 무엇보다 요즘 GPU에는 16비트 행렬 곱만 전담하는 **텐서 코어(Tensor Core)** 라는 계산 장치가 따로 있어서 계산 자체가 몇 배 빨라집니다.

그런데 16비트 실수에는 두 종류가 있어요. 칸 16개를 어떻게 나눠 쓰느냐가 다릅니다. 실수는 "몇 자리 숫자(가수)를 10의 몇 제곱(지수)만큼 키운다"는 식으로 저장하는데, `float16`은 가수에 칸을 많이 주고, `bfloat16`은 지수에 칸을 많이 줍니다. 각각이 담을 수 있는 수의 범위를 보죠.

```python
import torch

for 자료형 in [torch.float32, torch.float16, torch.bfloat16]:
    정보 = torch.finfo(자료형)                       # 자료형이 담을 수 있는 수의 범위
    print(f"{str(자료형):<15} 최대 {정보.max:8.2e} | 가장 작은 정규 수 {정보.tiny:8.2e}"
          f" | 1 옆의 간격 {정보.eps:8.2e}")

값 = torch.tensor([70000.0, 0.00000001, 1.001, 0.1])
for 자료형 in [torch.float32, torch.float16, torch.bfloat16]:
    바꾼_값 = 값.to(자료형).tolist()
    print(f"{str(자료형):<15}", " ".join(f"{v:>13.7g}" for v in 바꾼_값))
```

```text
torch.float32   최대 3.40e+38 | 가장 작은 정규 수 1.18e-38 | 1 옆의 간격 1.19e-07
torch.float16   최대 6.55e+04 | 가장 작은 정규 수 6.10e-05 | 1 옆의 간격 9.77e-04
torch.bfloat16  최대 3.39e+38 | 가장 작은 정규 수 1.18e-38 | 1 옆의 간격 7.81e-03
torch.float32           70000         1e-08         1.001           0.1
torch.float16             inf             0      1.000977    0.09997559
torch.bfloat16          70144  1.001172e-08             1     0.1000977
```

위의 세 줄은 `torch.finfo`로 자료형마다 담을 수 있는 가장 큰 수, 가장 작은 (정규) 수, 그리고 1 바로 옆의 수와의 간격을 본 것입니다. 아래 세 줄은 같은 네 숫자 70000, 0.00000001, 1.001, 0.1을 각 자료형으로 바꿔 본 결과예요.

- **`float16`**: 가장 큰 수가 65,504라서 **70000은 `inf`(무한대)가 됩니다.** 아주 작은 수 쪽도 좁아서 0.00000001은 0이 돼 버렸어요. 대신 1 옆의 간격이 0.001이라 1.001을 1.000977로 꽤 가깝게 담았습니다.
- **`bfloat16`**: 가장 큰 수와 가장 작은 수가 `float32`와 같습니다. 70000도, 0.00000001도 담겼어요. 대신 1 옆의 간격이 0.0078이라 거칩니다. 1.001은 그냥 1이 되고, 70000은 70144가 됐어요.

정리하면 `float16`은 **범위가 좁고 촘촘한** 자, `bfloat16`은 **범위가 넓고 성긴** 자입니다. 딥러닝에서는 대부분 범위가 더 중요해요. 4장에서 말했듯 끝자리의 작은 오차는 학습에 큰 영향이 없지만, 값이 `inf`가 되거나 0이 되어 사라지면 학습이 망가지거든요. 그래서 `bfloat16`을 지원하는 GPU(NVIDIA는 계산 능력 8.0 이상, 앞에서 본 `is_bf16_supported()`)라면 `bfloat16`을 먼저 고르는 것이 요즘의 관례입니다. 14장 14.6절에서 LLM을 `bfloat16`으로 올린 것도 같은 이유예요.

### autocast: 알아서 골라 주는 16비트

그럼 모델 전체를 `.half()`로 바꾸면 될까요? 그러면 손실이나 소프트맥스처럼 작은 값을 많이 더하는 계산에서 오차가 크게 쌓입니다. 그래서 **계산마다 알맞은 자료형을 골라 쓰는** 방법을 써요. 이것이 **혼합 정밀도(mixed precision)** 이고, `torch.autocast`가 그 고르기를 대신해 줍니다.

```python
import torch
import torch.nn.functional as F
from torch import nn


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


장치 = 장치_고르기()
반정밀도 = torch.bfloat16 if 장치.type == "cpu" else torch.float16
torch.manual_seed(0)
모델 = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10)).to(장치)
x = torch.randn(8, 64, device=장치)
y = torch.randint(0, 10, (8,), device=장치)

with torch.autocast(device_type=장치.type, dtype=반정밀도):   # 이 안에서만 16비트로
    은닉 = 모델[0](x)
    점수 = 모델(x)
    확률 = 점수.softmax(dim=1)
    손실 = F.cross_entropy(점수, y)
print("입력:", x.dtype, "| Linear 출력:", 은닉.dtype, "| 점수:", 점수.dtype)
print("softmax:", 확률.dtype, "| 손실:", 손실.dtype)

손실.backward()                                                # backward는 with 밖에서
print("가중치:", 모델[0].weight.dtype, "| 기울기:", 모델[0].weight.grad.dtype)
print("autocast 밖의 Linear 출력:", 모델[0](x).dtype)
```

```text
입력: torch.float32 | Linear 출력: torch.float16 | 점수: torch.float16
softmax: torch.float32 | 손실: torch.float32
가중치: torch.float32 | 기울기: torch.float32
autocast 밖의 Linear 출력: torch.float32
```

`with torch.autocast(...)` 블록 안에서 일어난 일을 보세요.

- 입력은 `float32`인데 **`Linear`의 출력은 `float16`** 입니다. 행렬 곱은 16비트로 해도 안전하고, 텐서 코어 덕분에 가장 많이 빨라지는 계산이라 autocast가 16비트를 골랐어요.
- **`softmax`와 손실은 `float32`** 입니다. 지수 함수와 큰 합계가 들어가 16비트에서 오차가 크게 나는 계산이라, 입력이 16비트여도 autocast가 32비트로 올려서 계산했습니다.
- **가중치와 기울기는 여전히 `float32`** 입니다. 모델 안의 진짜 숫자는 32비트로 보관하고, 계산할 때만 16비트 사본을 만들어 쓰는 거예요. 이렇게 해야 학습률 × 기울기처럼 아주 작은 변화도 가중치에 제대로 더해집니다.
- autocast 블록 **밖**에서는 같은 `Linear`가 다시 `float32`를 냅니다. 모델을 바꾼 게 아니라 블록 안에서만 계산 방식을 바꾼 거죠.

`backward()`는 블록 밖에서 부릅니다. 역전파는 순전파 때 정해진 자료형을 그대로 따라가요. 이 코드는 `장치_고르기()`를 쓰므로 이 책의 맥(MPS)에서도 똑같은 자료형이 나왔고, CPU에서는 `bfloat16`을 쓰도록 했습니다.

### GradScaler: float16의 사라지는 기울기 지키기

`float16`에는 한 가지 문제가 더 있습니다. 학습 막바지에는 손실이 작아지고 기울기도 아주 작아지는데, `float16`은 위 표의 가장 작은 정규 수(6 × 10⁻⁵)보다 작아지면 정밀도를 잃기 시작하고, 6 × 10⁻⁸보다 작으면 아예 0이 되어 버려요(위에서 0.00000001이 0이 된 것처럼). 이것을 **언더플로(underflow)** 라고 합니다. 기울기가 0이면 학습이 멈추겠죠.

해결법은 간단합니다. backward 하기 전에 손실에 큰 수(예: 65,536)를 곱해 기울기를 통째로 키워서 계산하고, 가중치를 고치기 직전에 같은 수로 다시 나누는 거예요. 아주 작은 글씨를 확대 복사했다가 읽은 뒤 원래 크기로 되돌리는 셈입니다. 정말 효과가 있는지 일부러 아주 작은 손실을 만들어 확인해 보겠습니다.

```python
import math

import torch
from torch import nn

torch.manual_seed(0)
모델 = nn.Linear(1024, 1024).to("cuda")
x = torch.randn(256, 1024, device="cuda")


def 기울기_구하기(배율: float) -> torch.Tensor:
    """float16 autocast로 계산하고, 손실에 배율을 곱해 backward한 뒤 배율로 다시 나눈다."""
    모델.zero_grad()
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        출력 = 모델(x)
    손실 = 출력.float().pow(2).mean() * 1e-3        # 학습 막바지처럼 아주 작은 손실
    (손실 * 배율).backward()
    return 모델.weight.grad / 배율


# 기준: autocast 없이 float32로만 계산한 기울기
모델.zero_grad()
(모델(x).pow(2).mean() * 1e-3).backward()
기준 = 모델.weight.grad.clone()

for 배율 in [1.0, 2.0 ** 16]:
    기울기 = 기울기_구하기(배율)
    print(f"배율 {배율:>7.0f}: 0이 된 기울기 {(기울기 == 0).float().mean():6.1%}, "
          f"float32 기준과의 상대 오차 {((기울기 - 기준).norm() / 기준.norm()).item():.4f}")

# 실제 학습에서는 GradScaler가 배율을 알아서 관리한다
옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.1)
스케일러 = torch.amp.GradScaler("cuda", init_scale=2.0 ** 40)   # 일부러 너무 큰 배율로 시작
걸음, 갱신_횟수 = 0, 0
while 갱신_횟수 < 2:                                # 가중치를 두 번 갱신할 때까지
    옵티마이저.zero_grad()
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        손실 = 모델(x).float().pow(2).mean() * 1e-3
    스케일러.scale(손실).backward()                 # 손실에 배율을 곱해 backward
    배율 = 스케일러.get_scale()
    스케일러.step(옵티마이저)                       # 기울기를 배율로 나누고, inf가 있으면 건너뛴다
    스케일러.update()                               # inf가 있었으면 배율을 반으로
    결과 = "inf 발견, 이번 걸음은 건너뜀" if 스케일러.get_scale() < 배율 else "정상, 가중치 갱신"
    print(f"걸음 {걸음}: 배율 2^{math.log2(배율):.0f} → {결과}")
    갱신_횟수 += 결과.startswith("정상")
    걸음 += 1
```

```text
배율       1: 0이 된 기울기 100.0%, float32 기준과의 상대 오차 1.0000
배율   65536: 0이 된 기울기   0.0%, float32 기준과의 상대 오차 0.0005
걸음 0: 배율 2^40 → inf 발견, 이번 걸음은 건너뜀
걸음 1: 배율 2^39 → inf 발견, 이번 걸음은 건너뜀
걸음 2: 배율 2^38 → inf 발견, 이번 걸음은 건너뜀
걸음 3: 배율 2^37 → 정상, 가중치 갱신
걸음 4: 배율 2^37 → 정상, 가중치 갱신
```

배율 없이 `float16`으로 계산하자 가중치 기울기가 **100% 0이 됐습니다.** `float32` 기준과의 상대 오차 1.0은 "완전히 틀렸다"는 뜻이에요. 배율 65,536을 곱했더니 0이 된 기울기가 하나도 없고, 오차도 0.0005로 `float32`와 거의 같아졌습니다.

배율이 너무 크면 이번에는 반대로 기울기가 65,504를 넘어 `inf`가 됩니다. 그래서 적당한 배율을 사람이 정하기는 어려워요. **`torch.amp.GradScaler`** 가 이 일을 자동으로 해 줍니다. 위 결과에서는 일부러 2⁴⁰이라는 너무 큰 배율로 시작했어요. `GradScaler`는 기울기에서 `inf`를 발견하면 **그 걸음은 가중치를 고치지 않고 건너뛰고** 배율을 절반으로 줄입니다. 2⁴⁰, 2³⁹, 2³⁸에서 세 번 건너뛰고 2³⁷에서 정상으로 갱신하기 시작했죠. 반대로 오랫동안(기본 2,000걸음) `inf`가 안 나오면 배율을 두 배로 키워서, 언제나 넘치지 않는 선에서 가장 큰 배율을 유지합니다.

쓰는 법은 학습 루프에서 세 줄만 바꾸면 됩니다.

- `손실.backward()` → `스케일러.scale(손실).backward()`
- `옵티마이저.step()` → `스케일러.step(옵티마이저)`
- 그 뒤에 `스케일러.update()` 한 줄 추가

8장 8.9절의 그래디언트 클리핑과 함께 쓸 때는 주의할 점이 하나 있습니다. 기울기가 배율만큼 커져 있는 상태에서 자르면 엉뚱한 기준으로 자르게 되니, 자르기 전에 `스케일러.unscale_(옵티마이저)`로 배율을 먼저 나눠 줘야 해요. 그리고 **`bfloat16`은 범위가 `float32`와 같아서 `GradScaler`가 필요 없습니다.** 이것도 `bfloat16`을 먼저 고르는 이유예요.

### 속도, 메모리, 정확도 비교

이제 진짜 학습에서 비교해 보겠습니다. 12장에서 만든 작은 GPT와 같은 모양의 모델(층 6개, 차원 512, 헤드 8개)을 PyTorch의 `nn.TransformerEncoder` 부품으로 짧게 다시 만들었어요. 12장에서 한 줄 한 줄 만든 블록과 같은 구조를 PyTorch가 미리 만들어 둔 것입니다. 학습 데이터는 예제용으로 만든 규칙 데이터예요. 줄마다 시작 번호와 간격을 무작위로 정해서 7, 19, 31, 43, ...처럼 일정하게 늘어나는 번호(1,000에서 넘치면 0으로 돌아감)를 만들었으니, 모델은 앞의 번호들을 보고 간격을 알아내야 다음 번호를 맞힐 수 있습니다.

```python
import statistics
import time

import torch
import torch.nn.functional as F
from torch import nn

어휘, 길이, 배치 = 1000, 256, 32


class 작은_GPT(nn.Module):
    """12장의 작은 GPT와 같은 모양을 PyTorch 부품(nn.TransformerEncoder)으로 짧게 쓴 것."""

    def __init__(self, 차원: int = 512, 층: int = 6, 헤드: int = 8) -> None:
        super().__init__()
        self.글자 = nn.Embedding(어휘, 차원)
        self.위치 = nn.Embedding(길이, 차원)
        블록 = nn.TransformerEncoderLayer(차원, 헤드, 4 * 차원, dropout=0.0,
                                          batch_first=True, norm_first=True)
        self.몸통 = nn.TransformerEncoder(블록, 층, enable_nested_tensor=False)
        self.머리 = nn.Linear(차원, 어휘)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        T = x.shape[1]
        h = self.글자(x) + self.위치(torch.arange(T, device=x.device))
        마스크 = nn.Transformer.generate_square_subsequent_mask(T, device=x.device)
        return self.머리(self.몸통(h, mask=마스크, is_causal=True))


def 배치_만들기() -> torch.Tensor:
    """예제용으로 만든 규칙 데이터: 줄마다 시작 글자와 간격을 정해 일정하게 늘어나는 번호."""
    시작 = torch.randint(0, 어휘, (배치, 1), device="cuda")
    간격 = torch.randint(1, 20, (배치, 1), device="cuda")
    return (시작 + 간격 * torch.arange(길이 + 1, device="cuda")) % 어휘


def 학습(방식: str, 걸음_수: int = 200) -> tuple[float, float, float]:
    """방식대로 학습하고 (걸음당 ms, 최고 메모리 GB, 마지막 20걸음 평균 손실)을 돌려준다."""
    torch.manual_seed(0)
    모델 = 작은_GPT().to("cuda")
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=3e-4)
    자료형 = {"float32": None, "float16": torch.float16, "bfloat16": torch.bfloat16}[방식]
    스케일러 = torch.amp.GradScaler("cuda", enabled=(방식 == "float16"))  # float16일 때만 켠다
    torch.cuda.reset_peak_memory_stats()
    시간들, 손실들 = [], []
    for _ in range(걸음_수):
        시작 = time.perf_counter()
        데이터 = 배치_만들기()
        x, y = 데이터[:, :-1], 데이터[:, 1:]
        with torch.autocast("cuda", dtype=자료형, enabled=자료형 is not None):
            손실 = F.cross_entropy(모델(x).flatten(0, 1), y.flatten())
        옵티마이저.zero_grad(set_to_none=True)
        스케일러.scale(손실).backward()
        스케일러.step(옵티마이저)
        스케일러.update()
        손실들.append(손실.item())                   # .item()이 GPU를 기다려 준다
        시간들.append((time.perf_counter() - 시작) * 1000)
    return (statistics.median(시간들[10:]), torch.cuda.max_memory_allocated() / 1024 ** 3,
            statistics.mean(손실들[-20:]))


for 방식 in ["float32", "float16", "bfloat16"]:
    ms, 메모리, 손실 = 학습(방식)
    print(f"{방식:<9} 걸음당 {ms:5.1f} ms | 최고 메모리 {메모리:5.2f} GB | 마지막 손실 {손실:.4f}")
```

```text
float32   걸음당  36.1 ms | 최고 메모리  1.62 GB | 마지막 손실 1.1455
float16   걸음당  14.7 ms | 최고 메모리  1.09 GB | 마지막 손실 1.1615
bfloat16  걸음당  14.4 ms | 최고 메모리  1.09 GB | 마지막 손실 1.1410
```

`float32`로 한 걸음에 36.1ms 걸리던 학습이 `float16`과 `bfloat16`에서는 14.7ms, 14.4ms로 **2.5배 빨라졌습니다.** 최고 메모리도 1.62GB에서 1.09GB로 줄었어요. 활성화를 16비트로 저장하니 그만큼 줄어든 것입니다. 가중치와 옵티마이저 상태는 `float32` 그대로라 정확히 절반까지 줄지는 않았어요.

200걸음 뒤의 손실도 1.1455, 1.1615, 1.1410으로 거의 같습니다. 16비트의 작은 오차가 학습 결과를 바꾸지 않았어요(실행마다 끝자리는 조금 달라질 수 있습니다). `GradScaler`와 `autocast`는 `enabled=`로 끄고 켤 수 있어서, 학습 함수 하나로 세 방식을 모두 돌렸습니다. 학습 함수에서 걸음마다 `손실.item()`을 부른 것은 16.2절에서 피하라고 한 일이지만, 여기서는 걸음마다 시간을 재려고 일부러 GPU를 기다리게 한 거예요.

> **Q. float16과 bfloat16 중 무엇을 써야 하나요?**
> GPU가 지원한다면 `bfloat16`을 권합니다. 위 결과처럼 속도는 거의 같은데, `GradScaler`가 필요 없고 값이 넘칠 걱정도 적어요. NVIDIA GPU 중에서는 A100(계산 능력 8.0)과 RTX 30 시리즈(8.6) 이후부터 하드웨어가 직접 지원합니다. Colab의 T4(계산 능력 7.5)처럼 그보다 오래된 GPU에서는 `bfloat16` 계산이 느리니 `float16` + `GradScaler`를 쓰세요. 확인할 때는 `torch.cuda.is_bf16_supported(including_emulation=False)`처럼 **흉내 내기를 빼고** 물어야 합니다. 그냥 `is_bf16_supported()`라고 부르면 하드웨어가 지원하지 않아도 흉내 내서 계산할 수 있으면 `True`를 돌려줘서, T4에서도 `True`가 나와요.

## 16.7 TF32: float32 행렬 곱을 빠르게

혼합 정밀도는 코드를 조금 고쳐야 합니다. 코드를 한 줄도 안 고치고 빨라지는 방법은 없을까요? 텐서 코어에는 **TF32**라는 계산 방식이 하나 더 있습니다. 입력과 출력은 `float32` 그대로 두고, 텐서 코어 안에서 곱할 때만 가수를 `bfloat16`보다 조금 긴 10비트로 줄여서 계산해요. 범위는 `float32`와 같고 정밀도만 조금 낮춘 셈입니다. `torch.set_float32_matmul_precision`으로 켜고 끕니다. 같은 행렬 곱을 네 가지 방식으로 비교하고, `float64`로 구한 답과의 오차도 쟀어요.

```python
import statistics
import time

import torch


def 재기(함수, 반복: int = 20) -> float:
    """준비 운동 뒤 동기화하며 재고 중앙값(ms)을 돌려준다."""
    for _ in range(3):
        함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


n = 8192
torch.manual_seed(0)
a64 = torch.randn(n, n, device="cuda", dtype=torch.float64)
b64 = torch.randn(n, n, device="cuda", dtype=torch.float64)
정답 = a64 @ b64                                         # float64로 구한 기준 답

for 이름, 자료형, 정밀도 in [("float32 (highest)", torch.float32, "highest"),
                             ("float32 + TF32 (high)", torch.float32, "high"),
                             ("bfloat16", torch.bfloat16, "highest"),
                             ("float16", torch.float16, "highest")]:
    torch.set_float32_matmul_precision(정밀도)          # float32 행렬 곱에 TF32를 쓸지
    a, b = a64.to(자료형), b64.to(자료형)
    ms = 재기(lambda: a @ b)
    오차 = ((a @ b).double() - 정답).norm() / 정답.norm()
    print(f"{이름:<22} {ms:6.2f} ms | {2 * n ** 3 / ms / 1e9:5.1f} TFLOPS | 상대 오차 {오차.item():.1e}")
torch.set_float32_matmul_precision("highest")           # 기본값으로 되돌리기
```

```text
float32 (highest)       20.22 ms |  54.4 TFLOPS | 상대 오차 1.6e-06
float32 + TF32 (high)   13.00 ms |  84.6 TFLOPS | 상대 오차 2.9e-04
bfloat16                 6.63 ms | 165.8 TFLOPS | 상대 오차 3.1e-03
float16                  6.76 ms | 162.6 TFLOPS | 상대 오차 3.6e-04
```

- **`float32 (highest)`**: PyTorch의 기본값입니다. 20.2ms, 54 TFLOPS이고 오차는 1.6 × 10⁻⁶으로 가장 정확해요.
- **`float32 + TF32 (high)`**: 한 줄 바꿨을 뿐인데 13.0ms로 1.6배 빨라졌습니다. 오차는 2.9 × 10⁻⁴로 커졌지만, 딥러닝 학습에는 충분한 정밀도예요.
- **`bfloat16`, `float16`**: 6.6~6.8ms, 160 TFLOPS를 넘습니다. `float32`보다 3배 빨라요. 정밀도는 `float16`(3.6 × 10⁻⁴)이 `bfloat16`(3.1 × 10⁻³)보다 열 배쯤 좋습니다. 16.6절에서 본 "촘촘한 자와 성긴 자"의 차이가 그대로 나타났죠.

그래서 NVIDIA GPU로 학습하는 코드 맨 위에 다음 한 줄을 넣는 경우가 많습니다.

```python
torch.set_float32_matmul_precision("high")   # float32 행렬 곱에 TF32 허용
```

TF32는 계산 능력 8.0 이상의 NVIDIA GPU에서만 효과가 있고, autocast로 이미 16비트로 계산하는 부분에는 영향이 없습니다. autocast가 32비트로 남겨 둔 행렬 곱이나 autocast를 쓰지 않는 코드가 빨라져요. 정밀도가 정말 중요한 과학 계산이라면 켜지 않는 것이 맞고, 켜고 끄면 결과의 끝자리가 달라진다는 점도 기억해 두세요(8장 8.10절).

## 16.8 torch.compile: 모델을 미리 번역해 두기

### 첫 실행은 느리고, 그다음부터 빠르다

지금까지 PyTorch는 코드를 **한 줄씩 읽고 바로 실행**했어요. 이것을 **즉시 실행(eager) 모드**라고 하고, 중간에 `print`를 넣어 들여다보기 쉬워서 배우고 실험하기에 좋습니다.

그런데 레시피를 한 줄 읽고 재료 하나 넣는 요리사는 빠르지 않습니다. 레시피 전체를 미리 읽으면 "이 두 소스는 섞어서 한 번에 끓이기"처럼 순서를 다듬을 수 있죠. `torch.compile`이 그 일을 합니다. 처음 실행할 때 계산 전체를 **그래프**로 따 두고, 합칠 수 있는 계산을 합쳐 GPU용 코드를 새로 만들어요. 16.6절의 작은 GPT로 재 보겠습니다.

```python
import statistics
import time

import torch
import torch.nn.functional as F
from torch import nn

어휘, 길이, 배치 = 1000, 256, 32


class 작은_GPT(nn.Module):
    """16.6절과 같은 작은 GPT."""

    def __init__(self, 차원: int = 512, 층: int = 6, 헤드: int = 8) -> None:
        super().__init__()
        self.글자 = nn.Embedding(어휘, 차원)
        self.위치 = nn.Embedding(길이, 차원)
        블록 = nn.TransformerEncoderLayer(차원, 헤드, 4 * 차원, dropout=0.0,
                                          batch_first=True, norm_first=True)
        self.몸통 = nn.TransformerEncoder(블록, 층, enable_nested_tensor=False)
        self.머리 = nn.Linear(차원, 어휘)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        T = x.shape[1]
        h = self.글자(x) + self.위치(torch.arange(T, device=x.device))
        마스크 = nn.Transformer.generate_square_subsequent_mask(T, device=x.device)
        return self.머리(self.몸통(h, mask=마스크, is_causal=True))


def 걸음_시간들(모델: nn.Module, 걸음_수: int = 60) -> list[float]:
    """bfloat16 autocast로 학습 걸음을 밟으며 걸음마다 걸린 시간(ms)을 모은다."""
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=3e-4)
    생성기 = torch.Generator(device="cuda").manual_seed(0)
    시간들 = []
    for _ in range(걸음_수):
        시작 = time.perf_counter()
        데이터 = torch.randint(0, 어휘, (배치, 길이 + 1), device="cuda", generator=생성기)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            손실 = F.cross_entropy(모델(데이터[:, :-1]).flatten(0, 1), 데이터[:, 1:].flatten())
        옵티마이저.zero_grad(set_to_none=True)
        손실.backward()
        옵티마이저.step()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return 시간들


torch.manual_seed(0)
보통 = 걸음_시간들(작은_GPT().to("cuda"))
torch.manual_seed(0)
컴파일 = 걸음_시간들(torch.compile(작은_GPT().to("cuda")))   # 모델을 감싸기만 하면 된다

print(f"보통(eager) : 첫 걸음 {보통[0] / 1000:5.1f}초, 이후 걸음당 {statistics.median(보통[10:]):5.1f} ms")
print(f"compile     : 첫 걸음 {컴파일[0] / 1000:5.1f}초, 이후 걸음당 {statistics.median(컴파일[10:]):5.1f} ms")
print(f"걸음당 {statistics.median(보통[10:]) / statistics.median(컴파일[10:]):.2f}배 빨라짐")
```

```text
보통(eager) : 첫 걸음   0.2초, 이후 걸음당  14.2 ms
compile     : 첫 걸음   6.6초, 이후 걸음당  12.5 ms
걸음당 1.14배 빨라짐
```

쓰는 법은 정말 간단해서, 모델을 `torch.compile()`로 감싸기만 했습니다. 결과를 보면 두 가지가 눈에 띕니다.

- **첫 걸음이 6.6초**나 걸렸습니다. 보통 실행은 0.2초였어요. 이 시간 동안 모델을 그래프로 따고, 계산을 합치고, GPU 코드를 만들어 컴파일했습니다. 이 시간을 **컴파일 시간**이라고 해요.
- **그다음부터는 걸음당 14.2ms → 12.5ms로 1.14배 빨라졌습니다.**

1.14배는 생각보다 작죠? 이 모델은 시간 대부분이 큰 행렬 곱이고, 행렬 곱은 이미 cuBLAS가 가장 빠른 방법으로 하고 있어서 합칠 것이 많지 않았기 때문이에요. `nn.TransformerEncoder`는 어텐션에도 이미 빠른 함수(16.9절)를 쓰고 있고요. 그럼 `torch.compile`은 어디서 빛날까요?

### 계산 합치기의 힘

16.1절에서 계산 한 줄이 커널 하나라고 했습니다. 원소별 계산(곱하기, 더하기, tanh 같은)이 여러 줄 이어지면, 커널마다 **메모리에서 숫자를 읽어 와 계산하고 다시 메모리에 써 둡니다.** 숫자 6,700만 개짜리 텐서라면 한 줄마다 256MB를 읽고 256MB를 쓰는 거예요. 정작 계산은 금방 끝나는데 읽고 쓰는 데 시간이 다 갑니다. 이 계산들을 **커널 하나로 합치면** 한 번 읽어서 모든 계산을 다 하고 한 번만 쓰면 되죠. 이것을 **커널 융합(kernel fusion)** 이라고 합니다. GELU 활성화 함수의 근사식을 손으로 써서 확인해 보겠습니다.

```python
import statistics
import time

import torch


def 재기(함수, 반복: int = 30) -> float:
    """준비 운동 뒤 동기화하며 재고 중앙값(ms)을 돌려준다."""
    for _ in range(3):
        함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


def 손으로_쓴_GELU(x: torch.Tensor) -> torch.Tensor:
    """GELU 근사식: 곱하기·더하기·tanh가 여러 번 이어지는 원소별 계산."""
    return 0.5 * x * (1 + torch.tanh(0.7978845608 * (x + 0.044715 * x ** 3)))


x = torch.randn(64 * 1024 * 1024, device="cuda")       # 숫자 6,700만 개 (256MB)
합친_GELU = torch.compile(손으로_쓴_GELU)
print("결과 같음:", torch.allclose(손으로_쓴_GELU(x), 합친_GELU(x), atol=1e-6))

보통 = 재기(lambda: 손으로_쓴_GELU(x))
합침 = 재기(lambda: 합친_GELU(x))
내장 = 재기(lambda: torch.nn.functional.gelu(x, approximate="tanh"))
print(f"보통(eager)   : {보통:6.2f} ms")
print(f"torch.compile : {합침:6.2f} ms ({보통 / 합침:.1f}배)")
print(f"내장 F.gelu   : {내장:6.2f} ms")
대역폭 = 1008e9                                         # RTX 4090 메모리 대역폭 사양: 초당 1008GB
print(f"256MB를 한 번 읽고 한 번 쓰는 최소 시간: {2 * x.numel() * 4 / 대역폭 * 1000:.2f} ms")
```

```text
결과 같음: True
보통(eager)   :   5.25 ms
torch.compile :   0.60 ms (8.8배)
내장 F.gelu   :   0.59 ms
256MB를 한 번 읽고 한 번 쓰는 최소 시간: 0.53 ms
```

손으로 쓴 GELU는 5.25ms, `torch.compile`로 합친 것은 0.60ms로 **8.8배 빨라졌습니다.** 결과도 같아요. 마지막 줄은 이 GPU의 메모리 대역폭(제조사 사양 1,008GB/s)으로 256MB를 한 번 읽고 한 번 쓰는 데 필요한 최소 시간인데, 0.53ms입니다. 합친 버전(0.60ms)이 이 한계에 거의 붙었어요. 원소별 계산은 계산보다 **메모리를 읽고 쓰는 시간이 병목**이라, 읽고 쓰는 횟수를 줄이는 것이 곧 속도입니다. PyTorch에 들어 있는 `F.gelu`(0.59ms)도 사람이 미리 하나의 커널로 짜 둔 것이라 같은 속도가 나왔어요.

그러니 `torch.compile`은 **원소별 계산이 많은 모델**, 그리고 내장 함수 대신 직접 쓴 수식이 많은 모델에서 효과가 큽니다. 연구 코드에서 새로운 활성화 함수나 정규화를 직접 만들었다면 `torch.compile` 한 줄로 내장 함수 수준의 속도를 얻을 수 있다는 뜻이에요.

### 모드: 일감 맡기는 비용까지 줄이기

`torch.compile`에는 `mode=`로 고를 수 있는 방식이 몇 가지 있습니다. 16.1절의 "작은 일 천 번"처럼 일감 맡기는 비용이 큰 경우를 보기 위해, 작은 층 24개(Linear, LayerNorm, GELU 8번 반복)에 작은 배치 16개를 넣어 비교했어요.

```python
import statistics
import time

import torch
from torch import nn


def 재기(함수, 반복: int = 200) -> float:
    """준비 운동 뒤 동기화하며 재고 중앙값(ms)을 돌려준다."""
    for _ in range(10):
        함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


# 작은 모델, 작은 배치: 계산보다 "GPU에 일을 맡기는 비용"이 큰 경우
torch.manual_seed(0)
층들 = []
for _ in range(8):
    층들 += [nn.Linear(256, 256), nn.LayerNorm(256), nn.GELU()]
모델 = nn.Sequential(*층들).to("cuda").eval()
x = torch.randn(16, 256, device="cuda")

for 모드 in [None, "default", "reduce-overhead"]:
    torch.compiler.reset()                             # 앞에서 컴파일한 것을 지운다
    실행 = 모델 if 모드 is None else torch.compile(모델, mode=모드)
    with torch.no_grad():
        시작 = time.perf_counter()
        실행(x)
        torch.cuda.synchronize()
        준비 = time.perf_counter() - 시작
        ms = 재기(lambda: 실행(x))
    print(f"{모드 or 'eager':<16} 첫 호출 {준비:5.2f}초 | 그다음부터 한 번에 {ms:6.3f} ms")
```

```text
eager            첫 호출  0.04초 | 그다음부터 한 번에  0.116 ms
default          첫 호출  0.83초 | 그다음부터 한 번에  0.081 ms
reduce-overhead  첫 호출  0.08초 | 그다음부터 한 번에  0.067 ms
```

- **eager**: 0.115ms. 커널 수십 개를 하나씩 맡기는 비용이 대부분입니다.
- **`default`**: 기본 모드입니다. 커널을 합쳐서 수를 줄이니 0.080ms가 됐어요.
- **`reduce-overhead`**: 0.068ms로 가장 빠릅니다. **CUDA 그래프**라는 기능으로, GPU에 맡길 일감 전체를 한 번 녹화해 두었다가 다음부터는 "녹화한 것 다시 재생"이라는 일감 하나만 맡겨요. 일감 맡기는 비용이 사실상 사라집니다. 작은 모델의 추론이나 작은 배치 학습에 효과가 크지만, 입력 모양이 바뀌면 다시 녹화해야 하고 메모리를 조금 더 씁니다.

가장 빠른 계산 방법을 직접 실험해서 고르는 `max-autotune` 모드도 있지만, 컴파일에 몇 분씩 걸릴 수 있어 이 장에서는 재지 않았습니다.

첫 호출 시간을 보면 `default`가 0.83초, `reduce-overhead`가 0.08초였습니다. `reduce-overhead`가 더 빨리 준비된 것은, 앞에서 같은 모델을 컴파일하며 만든 결과물 일부를 PyTorch가 디스크에 **캐시**해 두었다가 다시 쓸 수 있었기 때문으로 보여요. PyTorch는 컴파일 결과를 디스크에 저장해 두기 때문에, 같은 모델을 다시 실행할 때는 컴파일 시간이 크게 줄어듭니다.

### 그래프가 끊기는 곳

`torch.compile`은 파이썬 코드를 읽어서 그래프로 바꾸는데, 그래프로 바꿀 수 없는 코드를 만나면 거기서 그래프를 **끊고** 그 부분은 보통 파이썬으로 실행한 뒤 다시 그래프를 시작합니다. 이것을 **그래프 끊김(graph break)** 이라고 해요. 끊긴 곳이 많으면 합칠 기회가 줄어서 빨라지지 않습니다. 어디서 끊기는지 `torch._dynamo.explain`으로 들여다볼 수 있어요. 이름에 밑줄이 붙은 `_dynamo`는 PyTorch 내부 도구라 버전에 따라 바뀔 수 있습니다. 앞에서 컴파일한 것을 지우는 일은 공개된 `torch.compiler.reset()`으로 했어요.

```python
import torch


def 깐깐한_함수(x: torch.Tensor) -> torch.Tensor:
    y = x.sin() * 2
    print("중간 점검")                 # 파이썬의 부수 효과
    if y.sum() > 0:                    # 텐서 값을 보고 갈림길을 고른다
        return y.cos()
    return y + 1


설명 = torch._dynamo.explain(깐깐한_함수)(torch.randn(8))     # 내부 도구(_dynamo)라 버전마다 바뀔 수 있다
print("그래프 수:", 설명.graph_count, "| 끊긴 곳:", 설명.graph_break_count)
for 이유 in 설명.break_reasons:
    print(" -", 이유.reason.splitlines()[0][:70])

torch.compiler.reset()
try:
    torch.compile(깐깐한_함수, fullgraph=True)(torch.randn(8))   # 끊기면 오류를 내라
except Exception as 오류:
    print("fullgraph=True:", type(오류).__name__)
```

```text
중간 점검
그래프 수: 3 | 끊긴 곳: 2
 - Failed to trace builtin operator
 - generic_jump TensorVariable()
fullgraph=True: Unsupported
```

작은 함수 하나가 그래프 3개로 쪼개졌고 끊긴 곳이 2군데입니다. 이유도 알려 줘요.

- **`Failed to trace builtin operator`**: `print`처럼 화면에 무언가를 하는 파이썬 내장 함수는 그래프에 담을 수 없습니다. 그래프는 "텐서 계산의 흐름"만 담는 그림이니까요.
- **`generic_jump TensorVariable()`**: `if y.sum() > 0:`처럼 **텐서의 값**을 보고 갈림길을 고르는 코드입니다. 그래프를 따는 시점에는 값을 모르니 어느 길로 갈지 정할 수가 없어요.

`fullgraph=True`를 주면 그래프가 끊길 때 조용히 넘어가지 않고 오류(`Unsupported`)를 냅니다. 모델 전체가 그래프 하나로 따지는지 확인하고 싶을 때 써요. 그래프 끊김을 줄이려면 학습 걸음 안에서 `print`나 `.item()`을 빼고, 텐서 값에 따른 `if`는 `torch.where`(4장 4.4절)처럼 텐서 계산으로 바꾸면 됩니다. 실무에서는 우선 모델 전체를 `torch.compile`로 감싸 보고, 기대만큼 빨라지지 않을 때 `explain`으로 끊긴 곳을 찾는 순서가 좋아요.

입력 모양이 바뀌어도 다시 컴파일이 일어납니다. 7장 7.7절처럼 문장 길이가 배치마다 다르면 처음 몇 번은 컴파일하느라 느려질 수 있으니, 길이를 몇 가지로 맞춰 채우는 것이 좋아요.

> **Q. 그럼 언제나 torch.compile을 켜는 게 좋나요?**
> 오래 돌릴 학습이라면 대개 켜는 것이 이득입니다. 몇 초에서 몇십 초의 컴파일 시간은 수천 걸음에 나눠지니까요. 반대로 코드를 자주 고치며 실험하는 단계, 몇 걸음만 돌려 보는 디버깅, 모델 안을 `print`로 들여다볼 때는 끄는 편이 편합니다. 오류 메시지도 eager 모드 쪽이 훨씬 읽기 쉬워요. "먼저 eager로 맞게 만들고, 다 되면 compile로 빠르게"가 좋은 순서입니다.

## 16.9 어텐션은 scaled_dot_product_attention으로

12장 12.5절에서 `F.scaled_dot_product_attention`(줄여서 SDPA)이 직접 쓴 어텐션과 같은 답을 낸다는 것을 확인하고, "장치에 따라 훨씬 빠르고 메모리를 덜 쓰는 계산법(예: FlashAttention)을 알아서 골라 준다, 실제로 학습시킬 때는 이 함수로 바꾸길 권한다(16장)"고 했습니다. 12.9절에서는 어텐션 점수 표가 글자 수의 제곱으로 커지는 것을 계산으로 봤고요. 이제 실제로 얼마나 다른지 재 보겠습니다.

SDPA 안에는 계산법(**백엔드**)이 여러 개 들어 있습니다. `sdpa_kernel()`로 하나를 골라 쓰게 할 수 있어요.

- **수학(MATH)**: 12장에서 직접 쓴 것과 같은 방법을 PyTorch 코드로 한 것. 어디서나 돌아가는 기본 방법입니다.
- **메모리 효율(EFFICIENT_ATTENTION)**: 점수 표를 통째로 만들지 않고 조각조각 계산하는 방법입니다.
- **플래시(FLASH_ATTENTION)**: 같은 생각을 GPU 구조에 맞춰 더 다듬은 FlashAttention 방법입니다. 16비트 입력이 필요하고, 계산 능력 8.0 이상의 GPU에서만 돌아요. 그래서 아래 코드는 Colab의 T4처럼 그보다 오래된 GPU에서는 플래시를 빼고 잽니다.

```python
import math
import statistics
import time

import torch
import torch.nn.functional as F
from torch.nn.attention import SDPBackend, sdpa_kernel


def 재기(함수, 반복: int = 10) -> float:
    """준비 운동 뒤 동기화하며 재고 중앙값(ms)을 돌려준다."""
    함수()
    torch.cuda.synchronize()
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        torch.cuda.synchronize()
        시간들.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(시간들)


def 직접_어텐션(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    """12장에서 직접 쓴 인과 어텐션: 점수 표를 통째로 만든다."""
    점수 = q @ k.transpose(-2, -1) / math.sqrt(q.shape[-1])
    T = q.shape[-2]
    미래 = torch.ones(T, T, dtype=torch.bool, device=q.device).triu(1)
    return 점수.masked_fill(미래, float("-inf")).softmax(dim=-1) @ v


def SDPA(백엔드: SDPBackend):
    """계산법(백엔드)을 하나로 정해서 scaled_dot_product_attention을 부르는 함수."""
    def 실행(q, k, v):
        with sdpa_kernel(백엔드):
            return F.scaled_dot_product_attention(q, k, v, is_causal=True)
    return 실행


방법들 = {"직접 계산": 직접_어텐션, "SDPA 수학": SDPA(SDPBackend.MATH),
          "SDPA 메모리 효율": SDPA(SDPBackend.EFFICIENT_ATTENTION),
          "SDPA 플래시": SDPA(SDPBackend.FLASH_ATTENTION)}
if torch.cuda.get_device_capability() < (8, 0):     # 플래시는 계산 능력 8.0 이상에서만 돈다
    del 방법들["SDPA 플래시"]                         # (Colab의 T4 같은 GPU에서는 빼고 잰다)
GB = 1024 ** 3
torch.manual_seed(0)
for T in [1024, 4096]:
    q, k, v = (torch.randn(8, 16, T, 64, device="cuda", dtype=torch.float16) for _ in range(3))
    기준 = 직접_어텐션(q, k, v)
    print(f"[글자 {T}개] 배치 8, 헤드 16, 헤드 크기 64, float16")
    for 이름, 함수 in 방법들.items():
        torch.cuda.reset_peak_memory_stats()
        전 = torch.cuda.memory_allocated()
        ms = 재기(lambda: 함수(q, k, v))
        추가 = (torch.cuda.max_memory_allocated() - 전) / GB
        같은가 = torch.allclose(함수(q, k, v), 기준, atol=1e-2)
        print(f"  {ms:7.2f} ms | 추가 메모리 {추가:5.2f} GB | 결과 같음 {같은가} ← {이름}")
```

```text
[글자 1024개] 배치 8, 헤드 16, 헤드 크기 64, float16
     3.07 ms | 추가 메모리  0.75 GB | 결과 같음 True ← 직접 계산
     7.05 ms | 추가 메모리  1.25 GB | 결과 같음 True ← SDPA 수학
     0.19 ms | 추가 메모리  0.02 GB | 결과 같음 True ← SDPA 메모리 효율
     0.17 ms | 추가 메모리  0.02 GB | 결과 같음 True ← SDPA 플래시
[글자 4096개] 배치 8, 헤드 16, 헤드 크기 64, float16
    48.13 ms | 추가 메모리 12.02 GB | 결과 같음 True ← 직접 계산
   114.60 ms | 추가 메모리 18.56 GB | 결과 같음 True ← SDPA 수학
     2.28 ms | 추가 메모리  0.06 GB | 결과 같음 True ← SDPA 메모리 효율
     1.91 ms | 추가 메모리  0.06 GB | 결과 같음 True ← SDPA 플래시
```

글자 1,024개에서도 차이가 큽니다. 직접 계산은 3.07ms에 메모리 0.75GB를 더 썼는데, 플래시는 0.17ms에 0.02GB로 **18배 빠르고 메모리는 수십 분의 일**이에요. 글자 4,096개가 되자 차이가 더 벌어집니다. 직접 계산은 48ms에 메모리를 12GB나 썼고, 플래시는 1.91ms에 0.06GB입니다. 25배 빠르고, 메모리는 200분의 1이에요. 네 방법 모두 결과는 같았습니다.

12.9절의 계산을 떠올려 보세요. 배치 8 × 헤드 16 × 4,096 × 4,096칸 × 2바이트면 점수 표 하나가 4GB입니다. 직접 계산은 점수 표, 마스크를 씌운 표, 소프트맥스를 거친 표를 차례로 만드니 12GB가 들었어요. 플래시와 메모리 효율 방법은 이 표를 **한 번도 통째로 만들지 않습니다.** 작은 조각을 GPU 안의 아주 빠른 메모리에 올려 계산을 끝내고 결과만 내보내요. 16.8절에서 본 "메모리를 읽고 쓰는 횟수가 곧 속도"라는 원리가 여기서도 그대로입니다.

`SDPA 수학`은 직접 계산보다도 느리고 메모리를 더 썼습니다(4,096글자에서 18.6GB). 수학 백엔드는 정확도를 지키려고 `float16` 입력을 안에서 `float32`로 올려 계산하기 때문이에요(`torch.backends.cuda.fp16_bf16_reduction_math_sdp_allowed()`가 기본값 `False`). 점수 표 한 칸이 2바이트가 아니라 4바이트가 되니 메모리도 시간도 더 듭니다. 속도보다 어디서나 정확히 돌아가는 것을 우선한, 다른 방법을 쓸 수 없을 때를 위한 대비책이에요. 백엔드를 고르지 않으면 SDPA는 입력의 모양, 자료형, 장치를 보고 쓸 수 있는 것 중 가장 빠른 것을 알아서 고르니, 보통은 `sdpa_kernel` 없이 그냥 부르면 됩니다. 이 표의 교훈은 "어텐션을 직접 쓰지 말고 SDPA를 부르자"예요. 16.6절의 `nn.TransformerEncoder`도 안에서 SDPA를 씁니다.

> **Q. FlashAttention을 쓰려면 따로 설치해야 하나요?**
> 이 장의 결과는 PyTorch만 설치해서 얻은 것입니다. PyTorch에 FlashAttention 계열의 계산법이 들어 있어서 SDPA가 알아서 골라 써요. 다만 플래시 방법은 지원하는 GPU 세대, 자료형(16비트), 헤드 크기에 조건이 있어서, 조건이 안 맞으면 SDPA가 다른 방법을 고릅니다. 최신 버전의 FlashAttention을 쓰려고 별도 패키지를 설치하는 경우도 있지만, 대부분은 SDPA로 충분합니다.

## 16.10 프로파일러로 시간 새는 곳 찾기

### 어디서 시간이 드는지 표로 보기

지금까지는 "이걸 바꾸면 빨라질까?"를 하나씩 재 봤습니다. 그런데 처음 보는 학습 코드가 느리다면 어디부터 고쳐야 할까요? 짐작으로 고치기 전에 **프로파일러(profiler)** 로 시간이 어디서 드는지부터 봐야 합니다. 건강 검진을 받고 나서 처방을 내리는 것과 같아요. ResNet18 학습 다섯 걸음을 `torch.profiler`로 기록해 보겠습니다.

```python
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
```

```text
5걸음 동안 GPU가 일한 시간: 125.8 ms
  55.98 ms  44.5%  100번  aten::convolution_backward
  23.27 ms  18.5%  100번  aten::cudnn_convolution
  15.85 ms  12.6%  100번  aten::cudnn_batch_norm_backward
   7.83 ms   6.2%   85번  aten::threshold_backward
   7.53 ms   6.0%  100번  aten::cudnn_batch_norm
   5.19 ms   4.1%  180번  aten::add_
   3.63 ms   2.9%   85번  aten::clamp_min_
   2.76 ms   2.2%    5번  aten::max_pool2d_with_indices_backward
이름표 '순전파': CPU에서  11.1 ms
이름표 '역전파': CPU에서  43.7 ms
이름표 '갱신': CPU에서   0.5 ms
```

`with profile(...) as 기록:` 블록 안에서 일어난 일이 모두 기록됩니다. `activities`에 `CPU`와 `CUDA`를 주면 파이썬 쪽 PyTorch 연산과 GPU 쪽 커널을 함께 기록해요. `기록.key_averages()`는 같은 이름끼리 묶어서 시간을 합친 표인데, 여기서는 PyTorch 연산(`aten::`으로 시작하는 이름)마다 **그 연산이 GPU에 맡긴 일의 시간**을 골라 큰 순서로 찍었습니다. `aten`은 PyTorch 안쪽의 C++ 연산 모음 이름이에요.

5걸음 동안 GPU가 일한 125.8ms 중 **합성곱의 역전파(`convolution_backward`)가 44.5%, 순전파(`cudnn_convolution`)가 18.5%**, 합성곱 둘만 63%입니다. 그다음이 배치 정규화(12.6% + 6.0%)이고, ReLU의 역전파(`threshold_backward`)와 순전파(`clamp_min_`), 잔차 연결의 덧셈(`add_`)이 뒤를 잇습니다. 그러니 이 모델은 합성곱을 빠르게 하는 방법(16비트로 텐서 코어 쓰기)이 가장 효과가 크고, ReLU를 바꾸는 고민은 많아야 몇 %의 이득이에요.

`record_function("순전파")`처럼 내 코드의 구간에 이름표를 붙일 수도 있습니다. 마지막 세 줄은 이름표마다 **CPU에서 걸린 시간**인데, 순전파가 11.1ms, 역전파가 43.7ms, 갱신이 0.5ms예요. GPU가 125ms 동안 일하는 사이에 파이썬은 훨씬 짧은 시간 만에 일감을 다 맡겼다는 뜻입니다. 16.2절의 비동기 실행을 프로파일러로 다시 확인한 셈이에요. CPU 시간이 GPU 시간보다 길어지면 그때는 일감 맡기는 쪽이 병목이라는 신호입니다.

`기록.key_averages().table(...)`은 PyTorch가 만들어 주는 자세한 표를, `기록.export_chrome_trace("기록.json")`은 웹 브라우저의 추적 도구(Perfetto 등)에서 CPU와 GPU의 시간 줄을 그림으로 볼 수 있는 파일을 만들어 줍니다. GPU 줄에 빈틈이 많으면 GPU가 놀고 있다는 뜻이에요.

### 데이터 로더 병목 잡기

7장 7.10절에서 일꾼 수에 따라 데이터 대기 시간이 어떻게 바뀌는지 `time.sleep`으로 흉내 냈고, "GPU가 일을 제대로 하는지 들여다보는 프로파일러는 16장에서"라고 했습니다. 이번에는 진짜 GPU와 진짜 데이터로 확인해요. 9장의 FashionMNIST(7만 장, 처음 한 번 `data/` 폴더에 내려받음)에 7장 7.6절의 증강을 걸고, 작은 CNN을 100걸음 학습하면서 **벽시계 시간**과 **그동안 GPU가 실제로 일한 시간**을 비교합니다. 둘을 나누면 GPU가 시간의 몇 %를 일했는지 알 수 있어요.

```python
import os
import time

import torch
import torch.nn.functional as F
from torch import nn
from torch.autograd import DeviceType
from torch.profiler import ProfilerActivity, profile
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import v2

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")


def 작은_CNN() -> nn.Sequential:
    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Linear(64 * 7 * 7, 10))


def 재기(일꾼: int, 걸음_수: int = 100) -> tuple[float, float]:
    """걸음_수만큼 학습하며 (벽시계 시간, 그동안 GPU가 실제로 일한 시간)을 초로 잰다."""
    증강 = v2.Compose([v2.ToImage(), v2.RandomCrop(28, padding=2), v2.RandomHorizontalFlip(),
                       v2.ToDtype(torch.float32, scale=True)])
    데이터 = datasets.FashionMNIST(데이터_폴더, train=True, download=True, transform=증강)
    로더 = DataLoader(데이터, batch_size=256, shuffle=True, num_workers=일꾼,
                      pin_memory=True, persistent_workers=일꾼 > 0)
    모델 = 작은_CNN().to("cuda")
    옵티마이저 = torch.optim.Adam(모델.parameters())
    반복자 = iter(로더)
    next(반복자)                                         # 일꾼을 띄우는 시간은 빼고 잰다
    with profile(activities=[ProfilerActivity.CUDA]) as 기록:
        시작 = time.perf_counter()
        for _ in range(걸음_수):
            x, y = next(반복자)
            x, y = x.to("cuda", non_blocking=True), y.to("cuda", non_blocking=True)
            손실 = F.cross_entropy(모델(x), y)
            옵티마이저.zero_grad(set_to_none=True)
            손실.backward()
            옵티마이저.step()
        torch.cuda.synchronize()
        전체 = time.perf_counter() - 시작
    GPU_시간 = sum(e.self_device_time_total for e in 기록.key_averages()
                  if e.device_type == DeviceType.CUDA) / 1e6        # GPU에서 실제로 돈 시간
    return 전체, GPU_시간


if __name__ == "__main__":
    for 일꾼 in [0, 8]:
        전체, GPU = 재기(일꾼)
        print(f"num_workers={일꾼}: 100걸음 {전체:5.2f}초, GPU가 일한 시간 {GPU:4.2f}초 "
              f"→ GPU 사용률 {GPU / 전체:5.1%}")
```

```text
num_workers=0: 100걸음  2.49초, GPU가 일한 시간 0.09초 → GPU 사용률  3.4%
num_workers=8: 100걸음  0.31초, GPU가 일한 시간 0.09초 → GPU 사용률 27.9%
```

일꾼 없이(`num_workers=0`) 학습하면 100걸음에 2.49초가 걸리는데, GPU가 실제로 일한 시간은 0.09초뿐입니다. **GPU 사용률 3.4%**, 시간의 97%를 놀았어요. 사진 25,600장을 하나씩 꺼내 자르고 뒤집는 일을 파이썬 프로세스 하나가 다 하는 동안 GPU는 기다린 거죠. 일꾼 8명을 쓰자 같은 100걸음이 0.31초로 **8배 빨라졌습니다.** GPU가 한 일(0.09초)은 똑같아요. 기다리는 시간만 줄었습니다.

일꾼 8명으로도 GPU 사용률은 27.9%입니다. 남은 시간은 어디로 갔을까요? 이 CNN은 너무 작아서 걸음마다 GPU 일이 1ms도 안 되는데, 파이썬이 커널 수십 개를 맡기고 옵티마이저를 돌리는 데 그보다 긴 시간이 듭니다. 16.1절의 "작은 일" 문제예요. 이럴 때는 배치를 키우거나(다음 절), `torch.compile`로 커널 수를 줄이는 것이 다음 처방입니다.

`nvidia-smi`의 `GPU-Util`이 학습 중에 낮게 오르내릴 때도 데이터 쪽부터 의심하세요. 다만 이 숫자는 "커널이 하나라도 돈 시간의 비율"이라 100%여도 계산 장치를 다 쓴다는 뜻은 아니니, 정확히 보려면 프로파일러가 낫습니다.

## 16.11 배치 크기와 처리량

16.1절에서 "GPU에는 큰 일을 한꺼번에 맡겨야 한다"고 했습니다. 배치를 키우면 정말 계속 빨라질까요? ResNet18을 `bfloat16` autocast로 학습하면서 배치 크기에 따라 걸음당 시간과 **처리량(throughput)**, 즉 초당 몇 장을 학습하는지를 쟀습니다.

```python
import time

import torch
import torch.nn.functional as F
from torchvision.models import resnet18

GB = 1024 ** 3
torch.manual_seed(0)
모델 = resnet18(num_classes=10).to("cuda")
옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.01)

for 배치 in [8, 32, 128, 512]:
    x = torch.randn(배치, 3, 224, 224, device="cuda")
    y = torch.randint(0, 10, (배치,), device="cuda")
    torch.cuda.reset_peak_memory_stats()
    for 걸음 in range(13):
        if 걸음 == 3:                                   # 준비 운동 세 걸음 뒤부터 잰다
            torch.cuda.synchronize()
            시작 = time.perf_counter()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            손실 = F.cross_entropy(모델(x), y)
        옵티마이저.zero_grad(set_to_none=True)
        손실.backward()
        옵티마이저.step()
    torch.cuda.synchronize()
    ms = (time.perf_counter() - 시작) / 10 * 1000
    print(f"배치 {배치:>3}: 걸음당 {ms:6.1f} ms | 초당 사진 {배치 / ms * 1000:5.0f}장"
          f" | 최고 메모리 {torch.cuda.max_memory_allocated() / GB:5.2f} GB")
    del x, y, 손실
```

```text
배치   8: 걸음당    3.1 ms | 초당 사진  2559장 | 최고 메모리  0.22 GB
배치  32: 걸음당    8.4 ms | 초당 사진  3818장 | 최고 메모리  0.51 GB
배치 128: 걸음당   33.6 ms | 초당 사진  3808장 | 최고 메모리  1.63 GB
배치 512: 걸음당  141.0 ms | 초당 사진  3632장 | 최고 메모리  6.13 GB
```

배치 8에서 32로 키우자 처리량이 초당 2,559장에서 3,818장으로 1.5배 늘었습니다. 배치 8은 GPU를 다 채우기에 일이 작았던 거예요. 그런데 32에서 128, 512로 키워도 처리량은 3,800장 근처에서 더 늘지 않습니다. 걸음당 시간이 배치에 정확히 비례해서 늘었어요(8.4 → 33.6 → 141.0ms). **GPU가 이미 꽉 찼다**는 뜻입니다. 메모리만 0.51GB에서 6.13GB로 늘었죠.

그러니 배치 크기는 "들어가는 만큼 최대한"이 아니라 **처리량이 더 늘지 않는 지점** 근처가 적당합니다. 그보다 크게 해도 속도 이득은 없고 메모리만 쓰며, 무엇보다 학습 결과가 달라질 수 있어요. 배치를 키우면 한 에폭의 걸음 수가 줄어 가중치를 고칠 기회가 적어지고, 보통은 학습률도 함께 조정해야 합니다. 배치 크기를 바꾸면 8장의 과적합 진단과 18장의 실험 기록으로 결과가 정말 같은지 확인하세요.

GPU가 꽉 차는 배치는 모델과 입력 크기마다 다르니, 새 모델은 이 절처럼 처리량부터 재 보세요.

> **Q. 배치를 키울 때 학습률은 어떻게 바꾸나요?**
> 정해진 공식은 없지만, 많이 쓰는 경험칙은 "배치를 k배로 키우면 학습률도 k배로"(SGD)입니다. Adam 계열은 그보다 덜 키우는 경우가 많고(예: √k배), 처음 몇백 걸음은 학습률을 천천히 올리는 워밍업(warm-up)을 함께 써요. 8장 8.7절의 스케줄러로 할 수 있습니다. 어느 쪽이든 검증 손실로 확인하는 것이 정답이에요.

## 16.12 성능 체크리스트

이 장에서 잰 것을 순서대로 정리하면, 느린 학습을 빠르게 만드는 체크리스트가 됩니다. 위에서부터 차례로 확인하세요. 위쪽일수록 고치기 쉽고 효과가 큰 것들이에요.

| 순서 | 확인할 것 | 방법 | 이 장 |
|---|---|---|---|
| 1 | 재는 방법이 맞는가 | 준비 운동, `synchronize`, 중앙값, `benchmark.Timer` | 16.2 |
| 2 | GPU가 놀고 있지 않은가 | 프로파일러로 GPU 사용률 보기, `num_workers`·`pin_memory` | 16.10, 7.10 |
| 3 | 불필요한 왕복·동기화가 없는가 | 모델·데이터는 GPU에 두기, 매 걸음 `.item()` 줄이기, `non_blocking` | 16.3, 16.5 |
| 4 | 16비트로 계산하는가 | `autocast` + `bfloat16` (또는 `float16` + `GradScaler`) | 16.6 |
| 5 | `float32` 행렬 곱에 TF32를 쓰는가 | `set_float32_matmul_precision("high")` | 16.7 |
| 6 | 어텐션은 SDPA를 쓰는가 | `F.scaled_dot_product_attention` | 16.9 |
| 7 | 커널을 합쳤는가 | `torch.compile`, 모드, 그래프 끊김 확인 | 16.8 |
| 8 | 배치 크기가 알맞은가 | 처리량이 더 늘지 않는 지점, 메모리 여유 | 16.11, 16.4 |
| 9 | 시간이 어디서 드는가 | `torch.profiler`로 큰 순서 보기 | 16.10 |

이 밖에 합성곱 모델에서 `torch.backends.cudnn.benchmark = True`를 켜면 cuDNN이 입력 크기에 맞는 가장 빠른 합성곱 방법을 처음에 실험해서 고릅니다. 입력 크기가 일정한 이미지 학습에서 흔히 쓰는 설정인데, 8장 8.10절의 재현성과는 잘 맞지 않아요. 빠른 쪽을 고르는 실험이 실행마다 다른 방법을 고를 수 있어서, 결과의 끝자리가 달라질 수 있기 때문입니다.

한 가지 원칙을 덧붙이면, **한 번에 하나씩 바꾸고 매번 잽니다.** 여러 개를 한꺼번에 바꾸면 무엇이 효과가 있었는지, 무엇이 오히려 느리게 했는지 알 수 없어요. 그리고 속도를 고친 뒤에는 **정확도가 그대로인지** 꼭 확인합니다. 다음 실습이 바로 그 순서를 따릅니다.

## 16.13 실습: 옷 분류기 학습을 단계별로 빠르게

9장 9.10절에서 만든 작은 ResNet 옷 분류기를 다시 가져오겠습니다. FashionMNIST 6만 장으로 학습하고 1만 장으로 시험하며, 7장의 증강(상하좌우 2칸 안에서 밀기, 좌우 뒤집기)과 8장 8.7절의 OneCycleLR을 썼어요. 이 학습을 이 장에서 배운 방법으로 한 단계씩 빠르게 만듭니다.

1. **① 기본**: `float32`, 일꾼 없음. 지금까지 이 책에서 해 온 방식입니다.
2. **② + bfloat16 autocast**: 16.6절
3. **③ + torch.compile**: 16.8절
4. **④ + 데이터 로더 일꾼 8**: 16.10절과 7장 7.10절. `pin_memory`와 `persistent_workers`도 함께 켜고, `non_blocking`으로 옮깁니다.
5. **⑤ ④에서 autocast·compile 빼기**: 데이터 병목을 없앤 뒤 ②, ③이 얼마나 기여하는지 따로 보기 위한 비교입니다.

단계마다 4에폭씩 학습하고, 첫 에폭(준비 시간이 섞임)과 나머지 에폭의 평균 시간, 그리고 시험 정확도를 기록합니다.

```python
import os
import time
from contextlib import nullcontext

import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import v2

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")


class 잔차블록(nn.Module):
    """9장 9.8절의 잔차 블록."""

    def __init__(self, 입력: int, 출력: int, 보폭: int = 1) -> None:
        super().__init__()
        self.합성곱1 = nn.Conv2d(입력, 출력, 3, stride=보폭, padding=1, bias=False)
        self.정규화1 = nn.BatchNorm2d(출력)
        self.합성곱2 = nn.Conv2d(출력, 출력, 3, padding=1, bias=False)
        self.정규화2 = nn.BatchNorm2d(출력)
        self.지름길 = nn.Identity()
        if 보폭 != 1 or 입력 != 출력:
            self.지름길 = nn.Sequential(nn.Conv2d(입력, 출력, 1, stride=보폭, bias=False),
                                        nn.BatchNorm2d(출력))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        고칠양 = self.정규화2(self.합성곱2(F.relu(self.정규화1(self.합성곱1(x)))))
        return F.relu(고칠양 + self.지름길(x))


def 작은_ResNet() -> nn.Sequential:
    """9장 9.10절의 작은 ResNet."""
    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1, bias=False), nn.BatchNorm2d(32), nn.ReLU(),
        잔차블록(32, 32), 잔차블록(32, 64, 보폭=2), 잔차블록(64, 128, 보폭=2),
        nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(0.3), nn.Linear(128, 10))


def 로더들(일꾼: int) -> tuple[DataLoader, DataLoader]:
    증강 = v2.Compose([v2.ToImage(), v2.RandomCrop(28, padding=2), v2.RandomHorizontalFlip(),
                       v2.ToDtype(torch.float32, scale=True)])
    기본 = v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
    학습 = datasets.FashionMNIST(데이터_폴더, train=True, download=True, transform=증강)
    시험 = datasets.FashionMNIST(데이터_폴더, train=False, download=True, transform=기본)
    옵션 = dict(num_workers=일꾼, pin_memory=일꾼 > 0, persistent_workers=일꾼 > 0)
    return (DataLoader(학습, batch_size=256, shuffle=True, **옵션),
            DataLoader(시험, batch_size=1024, **옵션))


def 실험(이름: str, amp: bool, 컴파일: bool, 일꾼: int, 에폭_수: int = 4) -> None:
    torch.manual_seed(0)
    학습_로더, 시험_로더 = 로더들(일꾼)
    모델 = 작은_ResNet().to("cuda")
    옵티마이저 = torch.optim.AdamW(모델.parameters())        # 학습률은 아래 OneCycleLR이 정한다
    스케줄러 = torch.optim.lr_scheduler.OneCycleLR(          # 8장 8.7절, 배치마다 step()
        옵티마이저, max_lr=4e-3, total_steps=에폭_수 * len(학습_로더))
    실행 = torch.compile(모델) if 컴파일 else 모델

    def 정밀도():
        """amp를 켰으면 bfloat16 autocast, 아니면 아무것도 안 하는 with 블록."""
        return torch.autocast("cuda", dtype=torch.bfloat16) if amp else nullcontext()

    에폭_시간 = []
    for _ in range(에폭_수):
        모델.train()
        torch.cuda.synchronize()
        시작 = time.perf_counter()
        for x, y in 학습_로더:
            x, y = x.to("cuda", non_blocking=True), y.to("cuda", non_blocking=True)
            with 정밀도():
                손실 = F.cross_entropy(실행(x), y)
            옵티마이저.zero_grad(set_to_none=True)
            손실.backward()
            옵티마이저.step()
            스케줄러.step()
        torch.cuda.synchronize()
        에폭_시간.append(time.perf_counter() - 시작)
    모델.eval()
    맞힘 = 0
    with torch.no_grad(), 정밀도():
        for x, y in 시험_로더:
            맞힘 += (실행(x.to("cuda")).argmax(dim=1).cpu() == y).sum().item()
    이후 = sum(에폭_시간[1:]) / (에폭_수 - 1)               # 첫 에폭은 준비 시간이 섞여 따로 본다
    print(f"첫 에폭 {에폭_시간[0]:4.1f}초 | 이후 에폭 평균 {이후:4.1f}초"
          f" | 시험 정확도 {맞힘 / 100:5.2f}% ← {이름}")


if __name__ == "__main__":
    실험("① 기본", amp=False, 컴파일=False, 일꾼=0)
    실험("② + bfloat16 autocast", amp=True, 컴파일=False, 일꾼=0)
    실험("③ + torch.compile", amp=True, 컴파일=True, 일꾼=0)
    실험("④ + 데이터 로더 일꾼 8", amp=True, 컴파일=True, 일꾼=8)
    실험("⑤ ④에서 autocast·compile 빼기", amp=False, 컴파일=False, 일꾼=8)
```

```text
첫 에폭  5.3초 | 이후 에폭 평균  5.1초 | 시험 정확도 90.94% ← ① 기본
첫 에폭  5.2초 | 이후 에폭 평균  5.1초 | 시험 정확도 90.85% ← ② + bfloat16 autocast
첫 에폭  6.2초 | 이후 에폭 평균  5.2초 | 시험 정확도 90.97% ← ③ + torch.compile
첫 에폭  1.0초 | 이후 에폭 평균  1.0초 | 시험 정확도 90.78% ← ④ + 데이터 로더 일꾼 8
첫 에폭  1.1초 | 이후 에폭 평균  1.1초 | 시험 정확도 90.86% ← ⑤ ④에서 autocast·compile 빼기
```

결과를 순서대로 읽어 보겠습니다.

- **①에서 ②, ③으로: 전혀 빨라지지 않았습니다.** 에폭당 5.1초 → 5.1초 → 5.2초예요. 16.10절에서 일꾼 없이는 GPU가 시간의 97%를 놀았던 것을 떠올려 보세요. 데이터가 오지 않는데 계산을 빨리 해 봐야 기다리는 시간만 늘어납니다. ③의 첫 에폭 6.2초에는 컴파일 시간이 더해졌어요(컴파일 캐시가 비어 있던 첫 실행에서는 17초쯤 걸렸습니다).
- **④: 에폭당 1.0초로 5.2배 빨라졌습니다.** 데이터 로더에 일꾼 8명을 붙인 것 하나로요. 병목은 처음부터 데이터였던 거예요.
- **⑤: 1.1초.** 데이터 대기를 크게 줄인 상태에서 autocast와 compile을 빼면 1.0초에서 1.1초로 10%쯤 느려집니다. 16.6절의 작은 GPT에서 2.5배였던 것과 비교하면 작은데, 28 × 28 흑백 사진을 다루는 작은 CNN은 계산 자체가 작아서 줄일 것이 적기 때문이에요. 다만 이 10%를 두 기능의 몫 전부라고 보기는 어렵습니다. 16.10절에서 일꾼 8명을 붙인 작은 CNN도 GPU 사용률이 28%에 그쳤듯이, ④에서도 GPU는 여전히 데이터와 일감 맡기기를 기다리는 시간이 있을 거예요. 그 시간이 남아 있는 한 GPU 계산을 줄여도 전체 시간에는 덜 드러납니다.
- **정확도는 다섯 단계 모두 90.8~91.0%로 같습니다.** 빠르게 만드느라 학습 결과를 잃지 않았다는 확인이에요. 단계마다 끝자리가 조금씩 다른 것은 16비트 계산의 작은 오차와, 일꾼 수에 따라 증강의 무작위 순서가 달라지는 것 때문입니다.

이 실습에서 가장 중요한 교훈은 순서입니다. 만약 ②, ③만 해 보고 "혼합 정밀도도 compile도 효과가 없네"라고 결론 내렸다면 크게 틀렸을 거예요. **가장 느린 곳을 먼저 고쳐야 나머지 처방이 효과를 냅니다.** 그래서 16.12절의 체크리스트에서 "GPU가 놀고 있지 않은가"를 위쪽에 두었어요. 실제 프로젝트에서는 ① 상태에서 16.10절의 프로파일러부터 돌려 보고 병목을 확인한 뒤 고치는 순서가 맞습니다.

## 16.14 정리와 다음 장 미리보기

이 장에서는 같은 GPU로 같은 모델을 더 빠르고 가볍게 돌리는 방법을 직접 재면서 익혔습니다.

- **GPU가 빠른 이유**: 단순한 계산을 수천 개씩 동시에. 대신 일감 하나를 맡기는 데 몇 µs가 들어, 작은 일을 여러 번 시키면 CPU보다 느리다
- **시간 재기**: GPU는 비동기라 `torch.cuda.synchronize()`나 CUDA 이벤트로 기다린 뒤 재고, 준비 운동 후 중앙값. `torch.utils.benchmark.Timer`. `.item()`은 숨은 동기화
- **CPU와 GPU의 교차점**: 작은 행렬은 CPU, 큰 행렬은 GPU. 옮기는 비용이 그 사이 이득을 갉아먹으니 GPU에 올린 것은 GPU에 둔다
- **메모리**: `memory_allocated`(실제 사용)와 `memory_reserved`(캐싱 할당자의 창고), `max_memory_allocated`. 학습 메모리의 대부분은 배치에 비례하는 활성화. `torch.OutOfMemoryError`와 대처 순서
- **옮기기**: GPU 밖으로 나가는 길(PCIe)은 GPU 안보다 수십 배 좁다. 고정 메모리 + `non_blocking=True`, DataLoader의 `pin_memory=True`
- **혼합 정밀도**: `float16`은 좁고 촘촘, `bfloat16`은 넓고 성기다. `autocast`가 계산마다 자료형을 고르고, `float16`이면 `GradScaler`로 언더플로를 막는다. 학습 2.5배, 메모리 감소, 정확도는 그대로
- **TF32**: `set_float32_matmul_precision("high")` 한 줄로 `float32` 행렬 곱 1.6배
- **torch.compile**: 첫 실행에 컴파일 시간, 그다음부터 커널 융합으로 빨라진다. 원소별 계산에서 특히 크다. `reduce-overhead`(CUDA 그래프), 그래프 끊김과 `explain`, `fullgraph=True`
- **SDPA**: 플래시·메모리 효율 백엔드는 점수 표를 만들지 않아 수십 배 빠르고 메모리는 수백 분의 일
- **프로파일러**: `torch.profiler`로 시간이 드는 연산을 큰 순서로, `record_function`으로 구간 이름표, GPU 사용률로 데이터 병목 찾기
- **배치와 처리량**: 처리량이 더 늘지 않는 지점이 GPU가 꽉 찬 곳. 그 너머는 메모리만 쓴다
- **순서**: 가장 느린 곳부터. 한 번에 하나씩 바꾸고, 매번 재고, 정확도를 확인한다

이 장에서는 GPU 한 장의 성능을 끝까지 끌어냈습니다. 그런데 모델이 GPU 한 장의 메모리에 다 들어가지 않거나, 한 장으로는 학습이 며칠씩 걸린다면 어떻게 할까요? 다음 17장에서는 먼저 한 장 안에서 메모리를 아끼는 방법(그래디언트 누적, 활성화 체크포인팅)을 보고, 이 서버의 GPU 두 장을 함께 써서 학습하는 분산 학습(DDP)으로 넘어갑니다. 16.5절에서 본 "GPU 밖으로 나가는 좁은 길"이 두 GPU가 기울기를 주고받을 때 어떤 비용이 되는지도 직접 재 볼 거예요.
