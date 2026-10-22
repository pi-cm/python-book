# Chapter 7. 데이터 파이프라인: Dataset과 DataLoader

> **학습 목표**  
> - 데이터를 한꺼번에 메모리에 올리지 않고 필요할 때 꺼내 쓰는 이유 설명하기
> - `__len__`과 `__getitem__`으로 CSV 파일, 이미지 폴더용 Dataset을 직접 만들기
> - DataLoader의 `batch_size`, `shuffle`, `drop_last`, `num_workers`가 하는 일을 결과로 확인하기
> - transforms로 정규화와 데이터 증강을 하고, 길이가 다른 샘플은 `collate_fn`으로 묶기
> - 재현 가능하게 학습/검증을 나누고, 불균형 데이터는 샘플러로 고르게 뽑기

---

## 들어가며: 주방은 재료를 한꺼번에 꺼내지 않습니다

손님이 몰리는 식당 주방을 떠올려 보세요. 하루에 쓸 재료를 아침에 창고에서 전부 꺼내 조리대에 쌓아 두는 주방은 없습니다. 조리대가 감당할 수 없을 뿐 아니라, 재료가 상하고 정작 필요한 칼과 도마를 놓을 자리도 없어지니까요. 실제 주방은 **창고에 무엇이 어디 있는지 목록만 쥐고**, 주문이 들어오면 그때 필요한 재료를 꺼내 **손질하고**, 같은 테이블 음식은 **쟁반 하나에 담아** 내보냅니다.

딥러닝 학습도 똑같은 문제를 겪습니다. 4장에서 사진 한 장이 숫자 15만 개쯤 된다고 했죠. 사진이 많아지면 어떻게 될까요?

```python
import torch

한장 = torch.zeros(3, 224, 224)               # 컬러 사진 한 장 (색, 세로, 가로)
한장_바이트 = 한장.numel() * 한장.element_size()  # 숫자 개수 × 숫자 하나의 크기(float32 = 4바이트)
print(f"사진 한 장: 숫자 {한장.numel():,}개, {한장_바이트 / 1024**2:.2f}MB")

for 장수 in [1_000, 100_000, 1_000_000]:
    print(f"사진 {장수:>9,}장: {장수 * 한장_바이트 / 1024**3:8.1f}GB")
```

```text
사진 한 장: 숫자 150,528개, 0.57MB
사진     1,000장:      0.6GB
사진   100,000장:     56.1GB
사진 1,000,000장:    560.8GB
```

224 × 224 컬러 사진 한 장은 약 0.57MB지만, 10만 장이면 56GB, 100만 장이면 560GB가 넘습니다. 이 책을 쓴 노트북의 메모리로는 10만 장도 한꺼번에 올릴 수 없어요. 그래서 PyTorch는 데이터를 다루는 일을 주방처럼 세 역할로 나눕니다.

- **Dataset (창고 목록)**: 샘플이 몇 개인지 알고, "n번 샘플 주세요"라고 하면 그 하나만 꺼내 줍니다.
- **transform (손질)**: 꺼낸 샘플을 모델이 먹기 좋은 텐서로 바꾸고, 필요하면 살짝 변형(증강)합니다.
- **DataLoader (쟁반)**: 샘플을 여러 개 꺼내 배치 하나로 묶어 모델에 건넵니다. 순서를 섞고, 여러 일꾼에게 나눠 꺼내게 하는 일도 맡아요.

이렇게 데이터가 창고에서 모델까지 흘러가는 길을 **데이터 파이프라인**이라고 부릅니다. 5장에서는 `randperm`으로 직접 섞고 잘라 묶음을 만들었고, 6장 실습에서는 torchvision이 준비해 둔 FashionMNIST를 `DataLoader`에 넘겨 썼죠. 이번에는 그 안에서 무슨 일이 일어나는지 열어 보고, 내 파일로 직접 만들어 봅니다. 실제 프로젝트에서는 학습 코드보다 이 파이프라인을 짜는 데 시간이 더 들 때가 많아요. 모델이 아무리 좋아도 엉뚱한 데이터가 들어가면 소용없고, 데이터가 늦게 오면 비싼 GPU가 놀기 때문입니다.

이 장에서는 Dataset을 직접 만들어 보는 것부터 시작해서 CSV 파일과 이미지 폴더를 읽고, 증강을 걸고, 길이가 다른 문장을 묶고, 학습/검증을 나누고, 드문 클래스를 더 자주 뽑고, 마지막으로 파이프라인이 느린 곳을 찾는 법까지 다룹니다. 모델은 거의 등장하지 않아요. 모델 학습은 6장, 학습을 잘 시키는 요령은 8장의 몫이고, 이 장의 주인공은 오직 데이터가 흘러가는 길입니다.

> **Q. 이 장의 예제 데이터는 어디서 받나요?**
> 받을 필요가 없습니다. CSV 파일, 도형 그림, 짧은 리뷰 문장 모두 **예제용으로 만든 데이터**이고, 만드는 코드가 각 예제 안에 들어 있어요. 예제를 실행하면 현재 폴더 아래 `data/` 폴더에 파일이 생깁니다. 이 장의 예제는 PyTorch 2.14, torchvision 0.29, 파이썬 3.12에서 실행해 확인했고, `uv add torchvision pillow pandas`로 필요한 라이브러리를 더할 수 있어요.

## 7.1 Dataset: 번호를 주면 샘플 하나를 주는 약속

### 두 가지 특수 메서드면 충분합니다

PyTorch의 Dataset은 생각보다 단순한 약속입니다. 딱 두 가지만 할 줄 알면 돼요.

- `len(데이터셋)`이라고 물으면 샘플이 몇 개인지 답한다 → `__len__`
- `데이터셋[i]`라고 하면 i번 샘플 하나를 돌려준다 → `__getitem__`

1권 11장에서 `len()`과 `객체[번호]`가 사실 `__len__`과 `__getitem__`이라는 특수 메서드를 부르는 것이라고 배웠죠. Dataset은 바로 그 두 메서드를 구현한 클래스일 뿐입니다. 0부터 n-1까지의 수와 그 제곱을 (입력, 정답) 짝으로 돌려주는 가장 작은 데이터셋을 만들어 보겠습니다. 샘플이 언제 만들어지는지 보려고 `__getitem__` 안에 출력문을 하나 넣었어요.

```python
from torch.utils.data import Dataset


class 제곱수_데이터셋(Dataset):
    """0부터 n-1까지의 수와 그 제곱을 (입력, 정답) 짝으로 돌려준다."""

    def __init__(self, n: int) -> None:
        self.n = n                         # 재료 목록만 기억해 둔다

    def __len__(self) -> int:
        return self.n                      # 샘플이 모두 몇 개인가

    def __getitem__(self, i: int) -> tuple[int, int]:
        if i >= self.n:
            raise IndexError(f"{i}번 샘플은 없습니다")
        print(f"  ({i}번 샘플을 지금 만듭니다)")
        return i, i * i                    # i번 샘플 하나를 그때 만들어 돌려준다


데이터 = 제곱수_데이터셋(4)
print("샘플 수:", len(데이터))
print("3번 샘플:", 데이터[3])
for 입력, 정답 in 데이터:
    print("반복:", 입력, 정답)
```

```text
샘플 수: 4
  (3번 샘플을 지금 만듭니다)
3번 샘플: (3, 9)
  (0번 샘플을 지금 만듭니다)
반복: 0 0
  (1번 샘플을 지금 만듭니다)
반복: 1 1
  (2번 샘플을 지금 만듭니다)
반복: 2 4
  (3번 샘플을 지금 만듭니다)
반복: 3 9
```

출력을 순서대로 보세요. `len(데이터)`는 아무 샘플도 만들지 않고 바로 4를 답했습니다. `데이터[3]`을 하자 그제야 "(3번 샘플을 지금 만듭니다)"가 찍혔어요. 주방 비유 그대로입니다. `__init__`은 창고 목록(여기서는 개수 `n`)만 기억해 두고, 실제 재료는 `__getitem__`이 불릴 때 하나씩 꺼냅니다. 샘플이 100만 개여도 한 번에 메모리에 있는 것은 지금 꺼낸 하나뿐이에요.

`for 입력, 정답 in 데이터:`도 잘 돌았습니다. 우리는 `__iter__`를 만든 적이 없는데 말이죠. 1권 15장에서 `for`문은 `__iter__`와 `__next__`로 돈다고 배웠는데, 파이썬에는 오래된 방법이 하나 더 있습니다. `__iter__`가 없고 `__getitem__`만 있으면 0, 1, 2, …를 차례로 넣어 보다가 `IndexError`가 나는 순간 멈추는 거예요. 그래서 범위를 벗어난 번호에 `IndexError`를 일으키는 줄이 중요합니다. 이 줄을 빼면 `for`문이 끝나지 않아요. 다만 실제 학습에서는 Dataset을 직접 `for`로 돌릴 일이 거의 없습니다. 7.3절의 DataLoader가 그 일을 대신하니까요.

> **Q. 꼭 `Dataset`을 상속해야 하나요?**
> 꼭 그렇지는 않습니다. DataLoader는 "`__len__`과 `__getitem__`이 있는가"만 보기 때문에, 7.7절에서처럼 평범한 파이썬 리스트를 넣어도 돌아가요. 1권 2장에서 본 "오리처럼 걸으면 오리"라는 생각 그대로입니다. 그래도 상속해 두면 읽는 사람이 "이건 데이터셋이구나" 하고 바로 알 수 있고, `데이터셋1 + 데이터셋2`로 두 데이터셋을 이어 붙이는 기능 같은 덤도 따라오니 상속하는 것이 관례예요.

### 무거운 일은 `__getitem__`에서

Dataset을 만들 때 기억할 원칙은 하나입니다. **`__init__`은 가볍게, 무거운 일은 `__getitem__`에서.** `__init__`에서는 파일 경로 목록이나 정답 표처럼 작은 정보만 준비하고, 그림 파일을 열거나 글을 숫자로 바꾸는 일은 샘플을 꺼내는 순간에 합니다. 그래야 데이터가 아무리 커도 메모리가 버티고, 7.10절에서 볼 것처럼 꺼내는 일을 여러 일꾼에게 나눠 맡길 수도 있어요. 반대로 데이터가 작다면 `__init__`에서 전부 읽어 두는 편이 빠릅니다. 다음 절의 TensorDataset이 그런 경우예요.

## 7.2 TensorDataset: 이미 텐서로 있을 때

특성과 정답이 이미 텐서로 메모리에 다 올라와 있다면, 클래스를 만들 필요도 없습니다. `TensorDataset`이 텐서들을 받아 같은 번호끼리 짝지어 줘요.

```python
import torch
from torch.utils.data import TensorDataset

torch.manual_seed(0)
X = torch.randn(6, 3)                    # 샘플 6개 × 특성 3개
y = torch.tensor([0, 1, 0, 1, 1, 0])     # 샘플마다 정답 하나

데이터 = TensorDataset(X, y)
print("샘플 수:", len(데이터))
x0, y0 = 데이터[0]                         # 0번 샘플: (특성 3개, 정답)
print(x0, y0)
특성들, 정답들 = 데이터[1:3]               # 슬라이스로 여러 개도 꺼낼 수 있다
print(특성들.shape, 정답들)

try:
    TensorDataset(X, torch.tensor([0, 1]))   # 샘플 수가 다르면?
except AssertionError as e:
    print("오류:", e)
```

```text
샘플 수: 6
tensor([-1.1258, -1.1524,  0.5667]) tensor(0)
torch.Size([2, 3]) tensor([1, 0])
오류: Size mismatch between tensors
```

`TensorDataset(X, y)`는 `X`의 0번 줄과 `y`의 0번 값을 짝지어 0번 샘플로 돌려줍니다. 샘플 수는 텐서의 첫 번째 차원 길이(6)가 되고, `데이터[1:3]`처럼 슬라이스로 여러 샘플을 한 번에 꺼낼 수도 있어요. 텐서를 몇 개든 넣을 수 있어서 `TensorDataset(X, y, 가중치)`처럼 세 개를 짝지어도 됩니다.

넣은 텐서들의 첫 번째 차원 길이가 다르면 바로 "Size mismatch between tensors" 오류를 냅니다. 특성은 6개 샘플인데 정답이 2개뿐이면 짝을 지을 수가 없으니까요. 이 검사 덕분에 특성과 정답의 개수가 어긋나는 실수를 일찍 잡을 수 있습니다.

TensorDataset은 데이터가 메모리에 다 들어갈 만큼 작을 때, 예를 들어 3장에서 다룬 것 같은 표 데이터나 이 장의 7.3절처럼 작은 실험을 할 때 가장 간편한 선택이에요.

## 7.3 DataLoader: 배치로 묶어 나르기

### batch_size, drop_last, shuffle

Dataset이 샘플을 **하나씩** 꺼내 준다면, DataLoader는 그걸 **배치로 묶어** 나릅니다. 4장에서 모델은 사진을 한 장씩이 아니라 수십 장씩 묶어서 처리해야 GPU가 쉬지 않는다고 했죠. 샘플 10개짜리 데이터셋으로 DataLoader의 기본 옵션 세 가지를 확인해 보겠습니다. 정답을 샘플 번호와 같게 만들어서, 출력의 정답 목록이 곧 "몇 번 샘플들이 묶였는지"가 되게 했어요.

```python
import torch
from torch.utils.data import DataLoader, TensorDataset

X = torch.arange(10).float().unsqueeze(1) * 10   # 샘플 10개 × 특성 1개: 0, 10, ..., 90
y = torch.arange(10)                             # 정답은 샘플 번호와 같게
데이터 = TensorDataset(X, y)

로더 = DataLoader(데이터, batch_size=4)
print("배치 수:", len(로더))
for xb, yb in 로더:
    print(tuple(xb.shape), yb.tolist())

버리는_로더 = DataLoader(데이터, batch_size=4, drop_last=True)
print("drop_last=True 배치 수:", len(버리는_로더))

g = torch.Generator().manual_seed(0)             # 섞는 순서도 씨앗으로 고정
섞는_로더 = DataLoader(데이터, batch_size=4, shuffle=True, generator=g)
for 에폭 in range(2):
    print(f"에폭 {에폭}:", [yb.tolist() for _, yb in 섞는_로더])
```

```text
배치 수: 3
(4, 1) [0, 1, 2, 3]
(4, 1) [4, 5, 6, 7]
(2, 1) [8, 9]
drop_last=True 배치 수: 2
에폭 0: [[3, 7, 5, 2], [0, 8, 1, 6], [9, 4]]
에폭 1: [[1, 3, 2, 7], [5, 9, 0, 6], [4, 8]]
```

- **`batch_size=4`**: 샘플 4개씩 묶습니다. 입력은 `(1,)` 모양 샘플 4개가 쌓여 `(4, 1)`이 됐어요. 10개를 4개씩 묶으면 마지막 배치에는 2개만 남는데, 버리지 않고 작은 배치로 내보냅니다. 그래서 `len(로더)`는 3입니다.
- **`drop_last=True`**: 크기가 모자란 마지막 배치를 버립니다. 배치 수가 2로 줄었어요. 배치 정규화(8장)처럼 배치 크기가 너무 작으면 불안정해지는 경우에 씁니다.
- **`shuffle=True`**: 에폭마다 순서를 새로 섞습니다. **에폭(epoch)** 은 데이터 전체를 한 바퀴 도는 것을 말해요. 에폭 0과 에폭 1의 순서가 다르죠? 샘플 순서가 늘 같으면 모델이 순서의 버릇까지 배워 버릴 수 있어서, 학습할 때는 보통 섞습니다.

`generator=g`로 섞는 순서의 씨앗을 고정한 것도 눈여겨보세요. 4장에서 본 "나만 쓰는 번호표 기계" `torch.Generator`예요. DataLoader에 씨앗을 고정한 생성기를 넘기면 언제 실행해도 같은 순서로 섞입니다. 그래서 이 책의 출력과 여러분의 출력이 같게 나와요. 재현성 전반은 18장에서 정리합니다.

DataLoader의 옵션은 많지만 자주 쓰는 것은 이 정도입니다. 나머지는 이 장의 뒤쪽 절에서 하나씩 만나요.

| 옵션 | 하는 일 | 나오는 곳 |
|---|---|---|
| `batch_size` | 배치 하나에 넣을 샘플 수 | 7.3절 |
| `shuffle` | 에폭마다 순서 섞기 (학습용은 `True`, 검증용은 `False`) | 7.3절 |
| `drop_last` | 모자란 마지막 배치 버리기 | 7.3절 |
| `generator` | 섞기·뽑기에 쓸 난수 씨앗 | 7.3절, 7.8절 |
| `collate_fn` | 샘플 목록을 배치 하나로 합치는 함수 | 7.7절 |
| `sampler`, `batch_sampler` | 어떤 순서로 몇 번 샘플을 뽑을지 직접 정하기 | 7.7절, 7.9절 |
| `num_workers` | 샘플을 꺼내는 일꾼 프로세스 수 | 7.10절 |
| `persistent_workers` | 에폭이 끝나도 일꾼을 살려 두기 | 7.10절 |
| `pin_memory` | CPU→GPU 복사를 빠르게 하는 고정 메모리 (CUDA) | 7.10절 |

### 샘플을 배치로 합치는 규칙

DataLoader는 샘플 여러 개를 **어떻게** 하나로 합칠까요? 샘플이 텐서 하나가 아니라 이름, 점수, 합격 여부가 섞인 딕셔너리라면요?

```python
import torch
from torch.utils.data import DataLoader, Dataset


class 학생_데이터셋(Dataset):
    """샘플 하나를 딕셔너리로 돌려주는 데이터셋 (예제용 점수)."""

    def __init__(self) -> None:
        self.이름 = ["가온", "나래", "다온", "라희", "마루"]
        self.점수 = torch.tensor([[80.0, 70.0], [92.0, 88.0], [75.0, 95.0],
                                 [60.0, 65.0], [88.0, 91.0]])
        self.합격 = [1, 1, 1, 0, 1]

    def __len__(self) -> int:
        return len(self.이름)

    def __getitem__(self, i: int) -> dict:
        return {"이름": self.이름[i], "점수": self.점수[i], "합격": self.합격[i]}


print("샘플 하나:", 학생_데이터셋()[0])
로더 = DataLoader(학생_데이터셋(), batch_size=3)
배치 = next(iter(로더))                     # 첫 배치만 꺼내 보기
for 키, 값 in 배치.items():
    print(f"{키}: {type(값).__name__} {값}")
```

```text
샘플 하나: {'이름': '가온', '점수': tensor([80., 70.]), '합격': 1}
이름: list ['가온', '나래', '다온']
점수: Tensor tensor([[80., 70.],
        [92., 88.],
        [75., 95.]])
합격: Tensor tensor([1, 1, 1])
```

DataLoader는 샘플의 **생김새를 그대로 유지하면서** 안쪽 값만 묶어 줍니다. 샘플이 딕셔너리면 배치도 같은 키를 가진 딕셔너리가 되고, 키마다 이렇게 처리해요.

- **텐서**(`점수`)는 4장의 `torch.stack`처럼 새 차원을 만들어 쌓습니다. `(2,)` 모양 3개가 `(3, 2)`가 됐어요.
- **숫자**(`합격`)는 텐서로 바꿔 모읍니다. 파이썬 정수 1, 1, 1이 `tensor([1, 1, 1])`이 됐죠.
- **문자열**(`이름`)은 텐서로 바꿀 수 없으니 리스트로 모읍니다.

샘플이 `(입력, 정답)` 튜플이면 배치도 `(입력 묶음, 정답 묶음)` 튜플이 됩니다. 앞의 예제에서 `for xb, yb in 로더:`로 바로 풀어 쓸 수 있었던 이유예요. 이 합치는 규칙을 **collate**(모아 맞추기)라고 부르고, 기본 규칙이 맞지 않을 때는 7.7절처럼 직접 바꿀 수 있습니다. 샘플에 파일 이름이나 원문 문장 같은 문자열을 함께 넣어 두면, 나중에 모델이 틀린 샘플을 찾아볼 때 아주 편해요.

### 번호가 없는 데이터: IterableDataset

지금까지의 Dataset은 "몇 번 샘플"이라고 번호로 꺼낼 수 있었습니다. 이런 것을 **맵 스타일(map-style)** 데이터셋이라고 해요. 그런데 끝없이 쌓이는 주문 기록이나, 한 줄씩 읽을 수밖에 없는 거대한 로그 파일처럼 **번호로 바로 찾아갈 수 없는** 데이터도 있습니다. 이럴 때는 1권 15장의 제너레이터처럼 처음부터 차례로 흘려보내는 `IterableDataset`을 씁니다.

```python
from collections.abc import Iterator

import torch
from torch.utils.data import DataLoader, IterableDataset


class 주문_흐름(IterableDataset):
    """주문 기록을 처음부터 차례로 흘려보내는 데이터셋 (예제용)."""

    def __init__(self, 주문_수: int) -> None:
        self.주문_수 = 주문_수

    def __iter__(self) -> Iterator[torch.Tensor]:
        for 번호 in range(self.주문_수):   # 실제로는 파일을 한 줄씩 읽는 자리
            yield torch.tensor([번호, 번호 * 1000])


로더 = DataLoader(주문_흐름(7), batch_size=3)
for 배치 in 로더:
    print(배치.tolist())

try:
    DataLoader(주문_흐름(7), batch_size=3, shuffle=True)
except ValueError as e:
    print("오류:", str(e).split(",")[0])
```

```text
[[0, 0], [1, 1000], [2, 2000]]
[[3, 3000], [4, 4000], [5, 5000]]
[[6, 6000]]
오류: DataLoader with IterableDataset: expected unspecified shuffle option
```

`__len__`과 `__getitem__` 대신 `__iter__` 하나만 만들었습니다. 안에서 `yield`로 샘플을 하나씩 내보내면 DataLoader가 3개씩 모아 배치로 만들어 줘요. 1권 15장에서 제너레이터를 파이프처럼 이어 붙이면 데이터가 아무리 커도 메모리에는 한 배치만 머문다고 했는데, 바로 그 생각입니다.

대신 잃는 것도 있습니다. `shuffle=True`를 주자 오류가 났죠. 번호가 없으니 DataLoader가 순서를 섞을 방법이 없기 때문입니다. 섞고 싶다면 `__iter__` 안에서 직접 일정량을 모아 섞어야 해요. 그리고 7.10절에서 볼 여러 일꾼과 함께 쓸 때 주의할 점이 하나 더 있습니다. 그래서 번호로 꺼낼 수 있는 데이터라면 맵 스타일이 기본이고, IterableDataset은 정말 흘려보낼 수밖에 없을 때 꺼내는 도구예요.

## 7.4 직접 만든 Dataset ①: CSV 파일

### 예제용 CSV 만들기

이제 실제 파일을 읽는 Dataset을 만들어 보겠습니다. 첫 번째는 표 데이터가 담긴 CSV 파일이에요. 귤의 무게, 당도, 껍질 두께를 재서 상·중·하 등급을 매긴 표가 있다고 해 봅시다. 실제 측정값이 아니라 **예제용으로 만든 데이터**로, 등급이 높을수록 무겁고 달고 껍질이 얇도록 만들었어요. 학습용 160개와 검증용 40개를 서로 다른 파일로 저장합니다.

```python
from pathlib import Path

import numpy as np
import pandas as pd

# 예제용으로 만든 귤 품질 데이터: 무게(g), 당도(브릭스), 껍질 두께(mm) → 등급
rng = np.random.default_rng(7)
등급들 = np.array(["하", "중", "상"])


def 귤_표_만들기(개수: int) -> pd.DataFrame:
    """등급을 먼저 정하고, 등급에 따라 조금씩 다른 측정값을 만든다."""
    등급번호 = rng.integers(0, 3, 개수)
    return pd.DataFrame({
        "무게": (rng.normal(80, 12, 개수) + 등급번호 * 8).round(1),
        "당도": (rng.normal(9.5, 1.0, 개수) + 등급번호 * 1.2).round(1),
        "껍질": (rng.normal(3.0, 0.4, 개수) - 등급번호 * 0.3).round(2),
        "등급": 등급들[등급번호],
    })


폴더 = Path("data/귤")
폴더.mkdir(parents=True, exist_ok=True)
귤_표_만들기(160).to_csv(폴더 / "학습.csv", index=False)
귤_표_만들기(40).to_csv(폴더 / "검증.csv", index=False)
print((폴더 / "학습.csv").read_text(encoding="utf-8").splitlines()[:4])
```

```text
['무게,당도,껍질,등급', '114.3,10.5,2.09,상', '82.9,10.2,2.77,중', '92.4,12.6,2.56,상']
```

첫 줄이 열 이름이고 그 아래로 귤 한 개가 한 줄씩 적혀 있습니다. 1권 12장에서 다룬 CSV 형식 그대로예요. pandas로 표를 만들고 `to_csv`로 저장하는 방법은 1권 20장에서 봤습니다.

### CSV를 읽는 Dataset

이 파일을 읽는 Dataset을 만들어 보겠습니다. 표 데이터는 몇 MB를 넘는 경우가 드물어서, 이번에는 `__init__`에서 파일 전체를 읽어 텐서로 바꿔 두는 쪽을 택했어요. 대신 특성을 **표준화**하는 일은 꺼낼 때 합니다.

```python
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset

# 7.4절 앞 블록과 같은 예제용 귤 데이터를 만든다(이미 있으면 그대로 쓴다)
폴더 = Path("data/귤")
if not (폴더 / "학습.csv").exists():
    rng = np.random.default_rng(7)
    폴더.mkdir(parents=True, exist_ok=True)
    for 이름, 개수 in [("학습", 160), ("검증", 40)]:
        n = rng.integers(0, 3, 개수)
        pd.DataFrame({"무게": (rng.normal(80, 12, 개수) + n * 8).round(1),
                      "당도": (rng.normal(9.5, 1.0, 개수) + n * 1.2).round(1),
                      "껍질": (rng.normal(3.0, 0.4, 개수) - n * 0.3).round(2),
                      "등급": np.array(["하", "중", "상"])[n]}
                     ).to_csv(폴더 / f"{이름}.csv", index=False)


class 귤_데이터셋(Dataset):
    """CSV 한 파일을 읽어 (특성 3개, 등급 번호)를 돌려준다."""

    특성_열 = ["무게", "당도", "껍질"]
    등급_번호 = {"하": 0, "중": 1, "상": 2}

    def __init__(self, 경로: Path, 평균: torch.Tensor | None = None,
                 표준편차: torch.Tensor | None = None) -> None:
        표 = pd.read_csv(경로)
        self.X = torch.tensor(표[self.특성_열].to_numpy(), dtype=torch.float32)
        self.y = torch.tensor(표["등급"].map(self.등급_번호).to_numpy())
        # 기준값을 받지 않았으면 이 파일에서 구한다(학습용일 때만 그래야 한다)
        self.평균 = self.X.mean(dim=0) if 평균 is None else 평균
        self.표준편차 = self.X.std(dim=0) if 표준편차 is None else 표준편차

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, torch.Tensor]:
        x = (self.X[i] - self.평균) / self.표준편차   # 꺼낼 때 표준화
        return x, self.y[i]


학습 = 귤_데이터셋(폴더 / "학습.csv")
검증 = 귤_데이터셋(폴더 / "검증.csv", 학습.평균, 학습.표준편차)  # 학습 기준을 그대로 넘긴다
print("샘플 수:", len(학습), len(검증))
print("학습 기준 평균:", 학습.평균)
x, y = 학습[0]
print("0번 샘플:", x, y)
xb, yb = next(iter(DataLoader(학습, batch_size=8)))
print("배치 모양:", tuple(xb.shape), tuple(yb.shape), yb.dtype)
print("등급별 개수:", torch.bincount(학습.y).tolist())
```

```text
샘플 수: 160 40
학습 기준 평균: tensor([86.9087, 10.7006,  2.5896])
0번 샘플: tensor([ 2.0863, -0.1422, -1.1424]) tensor(2)
배치 모양: (8, 3) (8,) torch.int64
등급별 개수: [46, 62, 52]
```

앞부분의 `if not ... exists():` 덩어리는 이 예제만 따로 실행해도 돌아가도록 앞 블록과 같은 데이터를 다시 만드는 부분이니 건너뛰어도 됩니다. 볼 곳은 `귤_데이터셋` 클래스예요.

- **`__init__`**: `pd.read_csv`로 표를 읽고, 특성 세 열은 `float32` 텐서로, 등급 글자는 `map`으로 0·1·2 번호로 바꿔 정수 텐서로 만듭니다. 4장에서 NumPy에서 넘어온 값은 `float64`라 32비트로 바꾸라고 했던 것 기억나죠? `dtype=torch.float32`가 그 역할입니다. 정답을 정수(`int64`) 번호로 만든 것은 6장의 분류 손실 함수가 이 형태를 기대하기 때문이에요.
- **`__getitem__`**: 특성에서 평균을 빼고 표준편차로 나눠 표준화한 뒤 돌려줍니다. 0번 귤은 무게가 학습 데이터 평균보다 표준편차의 2배쯤 무거운 귤이라는 뜻이죠.
- **배치**: DataLoader로 8개를 묶으니 특성은 `(8, 3)`, 정답은 `(8,)`의 `int64`가 됐습니다.

여기서 가장 중요한 줄은 `검증 = 귤_데이터셋(..., 학습.평균, 학습.표준편차)`입니다. 검증 데이터를 표준화할 때 **검증 데이터의 평균이 아니라 학습 데이터의 평균**을 썼어요. 2장에서 본 **데이터 누수** 이야기입니다. 검증 데이터는 "모델이 처음 보는 데이터"를 흉내 내야 하는데, 표준화 기준에 검증 데이터가 섞이면 시험 문제를 미리 엿본 셈이 됩니다. 그래서 기준값은 학습 데이터에서만 구하고, 검증·테스트 데이터에는 그 값을 넘겨서 씁니다. scikit-learn에서 `fit`은 학습 데이터에만, `transform`은 양쪽에 하던 것과 같은 원칙이에요.

마지막 줄의 `torch.bincount`는 0, 1, 2가 각각 몇 번 나왔는지 세어 줍니다. 하·중·상이 46, 62, 52개로 적당히 섞여 있네요. 새 데이터셋을 만들면 클래스별 개수부터 세어 보는 습관을 들이세요. 7.9절에서 클래스 개수가 크게 차이 날 때의 대처를 다룹니다.

> **Q. CSV 파일이 수십 GB라서 한 번에 못 읽으면요?**
> 몇 가지 길이 있습니다. 한 번만 전처리해서 NumPy 파일로 저장해 두고 `np.load(..., mmap_mode="r")`로 열면, 디스크에 둔 채 필요한 줄만 읽어 올 수 있어요(메모리 매핑). 순서대로 읽어도 되는 데이터라면 pandas의 `read_csv(..., chunksize=...)`로 조금씩 읽어 7.3절의 IterableDataset으로 흘려보내는 방법도 있습니다. 어느 쪽이든 원칙은 같아요. 창고 목록만 들고 있다가 필요할 때 꺼내는 것이죠.

## 7.5 직접 만든 Dataset ②: 이미지 폴더

### 폴더 이름이 곧 정답

이미지 데이터는 보통 이런 모양으로 정리되어 있습니다. 클래스마다 폴더를 하나씩 만들고, 그 안에 해당하는 그림을 넣는 거예요. 폴더 이름이 곧 정답이 됩니다.

```text
data/shapes/
├── circle/     000.png, 001.png, ...
├── square/     000.png, 001.png, ...
└── triangle/   000.png, 001.png, ...
```

예제용 그림을 직접 만들어 보겠습니다. 32 × 32 흰 바탕에 동그라미, 네모, 세모 중 하나를 무작위 색과 크기, 위치로 그려요. 이 코드는 7.11절 실습에서도 다시 쓰니 **`도형_만들기.py`라는 파일로 저장**해 두세요. 맨 아래의 `if __name__ == "__main__":`은 1권 14장에서 배운 장치입니다. 이 파일을 직접 실행하면 그림 폴더를 만들고 내용을 보여 주지만, 다른 파일에서 `import`하면 함수만 빌려줘요.

```python
# 도형_만들기.py — 예제용 도형 그림 폴더를 만드는 모듈
import random
from pathlib import Path

from PIL import Image, ImageDraw


def 도형_그리기(모양: str, rng: random.Random) -> Image.Image:
    """흰 바탕 32×32 그림에 무작위 색·크기·위치로 도형 하나를 그린다."""
    그림 = Image.new("RGB", (32, 32), "white")
    펜 = ImageDraw.Draw(그림)
    크기 = rng.randint(12, 22)
    x, y = rng.randint(1, 31 - 크기), rng.randint(1, 31 - 크기)
    색 = tuple(rng.randint(0, 200) for _ in range(3))
    if 모양 == "circle":
        펜.ellipse([x, y, x + 크기, y + 크기], fill=색)
    elif 모양 == "square":
        펜.rectangle([x, y, x + 크기, y + 크기], fill=색)
    else:
        펜.polygon([(x + 크기 // 2, y), (x, y + 크기), (x + 크기, y + 크기)], fill=색)
    return 그림


def 도형_폴더_만들기(뿌리: Path, 개수: dict[str, int], 씨앗: int = 0) -> None:
    """뿌리/모양/번호.png 구조로 그림을 저장한다. 폴더가 이미 있으면 건너뛴다."""
    if 뿌리.exists():
        return
    rng = random.Random(씨앗)
    for 모양, n in 개수.items():
        폴더 = 뿌리 / 모양                      # 폴더 이름이 곧 정답(클래스)
        폴더.mkdir(parents=True)
        for i in range(n):
            도형_그리기(모양, rng).save(폴더 / f"{i:03d}.png")


if __name__ == "__main__":
    뿌리 = Path("data/shapes")
    도형_폴더_만들기(뿌리, {"circle": 20, "square": 20, "triangle": 20})
    for 폴더 in sorted(뿌리.iterdir()):
        파일들 = sorted(폴더.glob("*.png"))
        print(f"{폴더.name}: {len(파일들)}개", [f.name for f in 파일들[:3]], "...")
```

```text
circle: 20개 ['000.png', '001.png', '002.png'] ...
square: 20개 ['000.png', '001.png', '002.png'] ...
triangle: 20개 ['000.png', '001.png', '002.png'] ...
```

그림 그리기에는 파이썬 이미지 라이브러리 Pillow(`PIL`)를 썼습니다. `ImageDraw`의 `ellipse`, `rectangle`, `polygon`으로 도형을 그리고 `save`로 PNG 파일을 저장해요. `random.Random(씨앗)`으로 난수 생성기를 따로 만들어서, 언제 실행해도 같은 그림이 나오게 했습니다. 폴더 이름을 영어로 지은 것은 운영체제마다 한글 파일 이름을 저장하는 방식이 조금씩 달라서 생기는 문제를 피하려는 거예요.

### 그림 폴더를 읽는 Dataset

이제 이 폴더를 읽는 Dataset입니다. CSV와 달리 그림은 수가 많고 커질 수 있으니, `__init__`에서는 **(파일 경로, 정답) 목록만** 만들고 그림 파일은 `__getitem__`에서 엽니다. 직접 만든 것과 torchvision이 준비해 둔 `ImageFolder`를 나란히 비교해 볼게요.

```python
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision.datasets import ImageFolder

from 도형_만들기 import 도형_폴더_만들기

뿌리 = Path("data/shapes")
도형_폴더_만들기(뿌리, {"circle": 20, "square": 20, "triangle": 20})


class 그림폴더_데이터셋(Dataset):
    """뿌리/클래스이름/파일.png 구조의 폴더를 읽는다."""

    def __init__(self, 뿌리: Path) -> None:
        self.클래스들 = sorted(p.name for p in 뿌리.iterdir() if p.is_dir())
        self.클래스_번호 = {이름: i for i, 이름 in enumerate(self.클래스들)}
        # 그림을 읽지 않고 (경로, 정답) 목록만 만들어 둔다
        self.목록 = [(경로, self.클래스_번호[이름])
                     for 이름 in self.클래스들
                     for 경로 in sorted((뿌리 / 이름).glob("*.png"))]

    def __len__(self) -> int:
        return len(self.목록)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, int]:
        경로, 정답 = self.목록[i]
        with Image.open(경로) as 그림:                   # 필요한 그 순간에 파일을 연다
            배열 = np.array(그림.convert("RGB"))          # (세로, 가로, 색), 0~255 정수
        텐서 = torch.from_numpy(배열).permute(2, 0, 1)   # (색, 세로, 가로)
        return 텐서.float() / 255, 정답


우리것 = 그림폴더_데이터셋(뿌리)
print("클래스:", 우리것.클래스_번호, "샘플 수:", len(우리것))
그림, 정답 = 우리것[25]
print("25번:", tuple(그림.shape), 그림.dtype, "정답", 정답, "경로", 우리것.목록[25][0].name)

기성품 = ImageFolder(뿌리)                               # torchvision이 준비해 둔 같은 기능
print("ImageFolder:", 기성품.class_to_idx, len(기성품))
그림2, 정답2 = 기성품[25]
print("25번:", type(그림2).__name__, 그림2.size, "정답", 정답2, 기성품.samples[25][0])
```

```text
클래스: {'circle': 0, 'square': 1, 'triangle': 2} 샘플 수: 60
25번: (3, 32, 32) torch.float32 정답 1 경로 005.png
ImageFolder: {'circle': 0, 'square': 1, 'triangle': 2} 60
25번: Image (32, 32) 정답 1 data/shapes/square/005.png
```

직접 만든 `그림폴더_데이터셋`의 흐름을 따라가 보겠습니다.

1. **클래스 목록**: 하위 폴더 이름을 정렬해서 `circle`, `square`, `triangle`에 0, 1, 2 번호를 붙였습니다. **정렬**이 중요해요. 정렬하지 않으면 컴퓨터마다 폴더를 읽는 순서가 달라서 같은 그림의 정답 번호가 바뀔 수 있습니다.
2. **(경로, 정답) 목록**: 그림 60장의 경로와 정답만 담았습니다. 그림 자체는 아직 하나도 읽지 않았어요.
3. **꺼내기**: `Image.open`으로 파일을 열어 NumPy 배열로 바꾸면 모양이 (세로, 가로, 색)입니다. 4장 4.5절에서 본 것처럼 PyTorch는 (색, 세로, 가로)를 원하니 `permute(2, 0, 1)`로 순서를 바꾸고, 0~255 정수를 255로 나눠 0~1 실수로 만들었어요. 파일은 1권 12장에서 배운 `with` 문으로 열어서, 다 읽으면 저절로 닫히게 했습니다.

25번 샘플은 정답 1(`square`) 폴더의 `005.png`입니다. 동그라미 20장(0~19번) 다음이 네모의 0번(20번)이니 계산이 맞죠.

아래쪽 `ImageFolder`는 이 일을 한 줄로 해 줍니다. `class_to_idx`가 우리 것과 똑같고, 25번 샘플도 같은 파일을 가리켜요. 차이가 하나 있습니다. `ImageFolder`는 그림을 텐서로 바꾸지 않고 **Pillow 그림(`Image`) 그대로** 돌려줍니다. 텐서로 바꾸는 일은 다음 절의 transform에 맡기라는 뜻이에요. 실무에서는 폴더 구조가 이 모양이면 `ImageFolder`를 쓰고, 정답이 CSV에 따로 적혀 있는 식으로 구조가 다르면 위처럼 직접 만듭니다.

## 7.6 transforms: 꺼낼 때 손질하기

### 변환 단계를 숫자로 따라가기

창고에서 꺼낸 재료를 그대로 손님에게 내지는 않죠. 씻고, 썰고, 간을 맞춥니다. 그림도 모델에 넣기 전에 손질이 필요해요. Pillow 그림을 텐서로 바꾸고, 0~255 정수를 실수로 바꾸고, 값의 범위를 고르게 맞추는 일입니다. torchvision은 이런 손질 도구를 `transforms`에 모아 두었고, 이 책은 최신 버전인 `torchvision.transforms.v2`를 씁니다. 세로 2 × 가로 3짜리 아주 작은 그림으로 각 단계가 숫자를 어떻게 바꾸는지 따라가 보겠습니다.

```python
import numpy as np
import torch
from PIL import Image
from torchvision.transforms import v2

# 세로 2 × 가로 3짜리 아주 작은 컬러 그림 (예제용 숫자)
배열 = np.array([[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
                 [[255, 255, 255], [128, 128, 128], [0, 0, 0]]], dtype=np.uint8)
그림 = Image.fromarray(배열)

텐서 = v2.ToImage()(그림)                                  # PIL → (색, 세로, 가로) 텐서
print("ToImage :", tuple(텐서.shape), 텐서.dtype)
print(텐서[0])                                              # 빨강 채널만
실수 = v2.ToDtype(torch.float32, scale=True)(텐서)          # 0~255 → 0~1
print("ToDtype :", 실수.dtype)
print(실수[0])
정규화 = v2.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])(실수)
print("Normalize:")
print(정규화[0])

한번에 = v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True),
                    v2.Normalize(mean=[0.5] * 3, std=[0.5] * 3)])
print("Compose와 같은가:", torch.equal(한번에(그림), 정규화))
```

```text
ToImage : (3, 2, 3) torch.uint8
tensor([[255,   0,   0],
        [255, 128,   0]], dtype=torch.uint8)
ToDtype : torch.float32
tensor([[1.0000, 0.0000, 0.0000],
        [1.0000, 0.5020, 0.0000]])
Normalize:
tensor([[ 1.0000, -1.0000, -1.0000],
        [ 1.0000,  0.0039, -1.0000]])
Compose와 같은가: True
```

빨강 채널의 숫자만 따라가 보세요.

- **`ToImage()`**: Pillow 그림을 `(색, 세로, 가로)` 텐서로 바꿉니다. 앞 절에서 손으로 한 `permute`를 대신해 주는 거예요. 값은 아직 0~255의 `uint8`입니다. 첫 줄의 빨강·초록·파랑 칸에서 빨강 채널 값은 255, 0, 0이고, 둘째 줄의 흰색·회색·검은색 칸은 255, 128, 0이에요.
- **`ToDtype(torch.float32, scale=True)`**: `float32`로 바꾸면서 255로 나눠 0~1로 맞춥니다. 128은 0.5020이 됐어요. `scale=True`를 빼먹으면 자료형만 바뀌고 값은 0~255 그대로라서, 뒤의 정규화가 엉뚱한 결과를 냅니다. 자주 하는 실수예요.
- **`Normalize(mean, std)`**: 채널마다 `(값 - 평균) / 표준편차`를 계산합니다. 평균 0.5, 표준편차 0.5를 주면 0~1이 -1~1로 바뀌어요. 1은 1, 0은 -1, 0.502는 0.0039가 됐죠.

6장에서 쓴 `transforms.ToTensor()`는 앞의 두 단계(텐서로 바꾸기와 0~1로 맞추기)를 한 번에 하는 기존 방식입니다. 6장과 9장은 결과를 서로 비교하려고 이 방식을 끝까지 쓰지만, 새로 짜는 코드라면 v2처럼 두 단계를 나눠 쓰기를 권해요. 자료형과 크기 조절을 따로 정할 수 있어서 실수가 줄기 때문입니다.

`Compose`는 여러 변환을 순서대로 이어 붙여 하나의 변환으로 만듭니다. 결과가 단계별로 한 것과 똑같았어요. 실전에서는 이 `Compose`를 Dataset의 `transform`으로 넘겨서, `__getitem__`이 샘플을 꺼낼 때마다 적용되게 합니다.

정규화에 쓰는 평균과 표준편차는 7.4절의 표준화처럼 **학습 데이터에서 구한 값**을 씁니다. 7.11절 실습에서 직접 구해 볼 거예요. 인터넷의 예제 코드에서 `mean=[0.485, 0.456, 0.406]`이라는 숫자를 자주 보게 되는데, 이것은 ImageNet이라는 큰 사진 데이터셋에서 구한 값입니다. ImageNet으로 미리 학습된 모델을 가져다 쓸 때는 그 모델이 배운 기준에 맞춰야 해서 이 값을 그대로 써요. 10장 전이 학습에서 다시 만납니다.

자주 쓰는 변환을 정리하면 이렇습니다.

| 변환 | 하는 일 | 증강인가 |
|---|---|---|
| `v2.ToImage()` | Pillow 그림·NumPy 배열 → `(색, 세로, 가로)` 텐서 | 아니요 |
| `v2.ToDtype(torch.float32, scale=True)` | 실수로 바꾸고 0~1로 맞추기 | 아니요 |
| `v2.Normalize(mean, std)` | 채널마다 `(값 - 평균) / 표준편차` | 아니요 |
| `v2.Resize(크기)` | 크기 바꾸기 | 아니요 |
| `v2.CenterCrop(크기)` | 가운데 잘라 내기 | 아니요 |
| `v2.RandomHorizontalFlip(p)` | 확률 p로 좌우 뒤집기 | 예 |
| `v2.RandomCrop(크기, padding)` | 테두리를 두르고 무작위 위치 잘라 내기 | 예 |
| `v2.RandomResizedCrop(크기)` | 무작위 크기·위치로 잘라 원하는 크기로 | 예 |
| `v2.RandomRotation(각도)` | 무작위 각도로 돌리기 | 예 |
| `v2.ColorJitter(...)` | 밝기·대비·채도를 무작위로 바꾸기 | 예 |

### 데이터 증강: 같은 그림을 조금씩 다르게

표 아래쪽의 `Random`으로 시작하는 변환들이 **데이터 증강(data augmentation)** 입니다. 고양이 사진을 좌우로 뒤집어도 여전히 고양이죠. 조금 잘라 내도, 살짝 어둡게 해도 고양이입니다. 이렇게 **정답이 바뀌지 않는 범위에서 그림을 살짝 바꿔** 보여 주면, 모델은 "고양이 귀가 꼭 왼쪽 위에 있어야 하는 건 아니구나"를 배웁니다. 같은 사진을 계속 똑같이 보여 줘서 사진을 통째로 외워 버리는 일도 줄어들고요. 증강이 정말 과적합을 줄이는지 숫자로 확인하는 일은 8장 실습에서 하고, 여기서는 증강이 숫자를 어떻게 바꾸는지만 정확히 보겠습니다.

```python
import torch
from torchvision.transforms import v2

torch.manual_seed(0)
그림 = torch.arange(1, 13, dtype=torch.uint8).reshape(1, 3, 4)   # 흑백 1채널, 세로 3 × 가로 4
print(f"원본:\n{그림[0]}")

print(f"좌우 뒤집기:\n{v2.RandomHorizontalFlip(p=1.0)(그림)[0]}")
print(f"상하 뒤집기:\n{v2.RandomVerticalFlip(p=1.0)(그림)[0]}")

자르기 = v2.RandomCrop(size=(3, 4), padding=1)     # 테두리를 0으로 1칸 두른 뒤 원래 크기로 자르기
for i in range(2):
    print(f"무작위 자르기 {i + 1}:\n{자르기(그림)[0]}")

반반 = v2.RandomHorizontalFlip(p=0.5)
뒤집힌_횟수 = sum(int(not torch.equal(반반(그림), 그림)) for _ in range(1000))
print("p=0.5로 1000번 중 뒤집힌 횟수:", 뒤집힌_횟수)
```

```text
원본:
tensor([[ 1,  2,  3,  4],
        [ 5,  6,  7,  8],
        [ 9, 10, 11, 12]], dtype=torch.uint8)
좌우 뒤집기:
tensor([[ 4,  3,  2,  1],
        [ 8,  7,  6,  5],
        [12, 11, 10,  9]], dtype=torch.uint8)
상하 뒤집기:
tensor([[ 9, 10, 11, 12],
        [ 5,  6,  7,  8],
        [ 1,  2,  3,  4]], dtype=torch.uint8)
무작위 자르기 1:
tensor([[ 0,  5,  6,  7],
        [ 0,  9, 10, 11],
        [ 0,  0,  0,  0]], dtype=torch.uint8)
무작위 자르기 2:
tensor([[ 0,  1,  2,  3],
        [ 0,  5,  6,  7],
        [ 0,  9, 10, 11]], dtype=torch.uint8)
p=0.5로 1000번 중 뒤집힌 횟수: 493
```

`p=1.0`으로 확률을 100%로 만들어 확실히 뒤집어 봤습니다. 좌우 뒤집기는 각 줄의 순서를 거꾸로(1, 2, 3, 4 → 4, 3, 2, 1), 상하 뒤집기는 줄의 순서를 거꾸로 바꿔요.

`RandomCrop(size=(3, 4), padding=1)`은 먼저 그림 둘레에 0을 한 칸씩 둘러 5 × 6으로 키운 뒤, 그 안에서 원래 크기인 3 × 4를 **무작위 위치**에서 잘라 냅니다. 첫 번째는 오른쪽 위로, 두 번째는 오른쪽으로 한 칸 밀린 것처럼 보이죠. 그림 속 물체를 위아래, 좌우로 조금씩 옮기는 효과가 있어요. 테두리에 채울 값은 `fill`로 정할 수 있습니다. 실습에서는 바탕이 흰색이라 흰색으로 채울 거예요.

`p=0.5`로 1000번 적용했더니 493번 뒤집혔습니다. 반쯤 뒤집힌다는 뜻이 그대로 나타났죠. 증강 변환은 이렇게 **부를 때마다 새로 주사위를 굴립니다.** 이것이 Dataset 안에서 어떤 의미인지 그림으로 보겠습니다.

```python
import torch
from torch.utils.data import Dataset
from torchvision.transforms import v2

ㄱ = torch.tensor([[0, 0, 0, 0, 0, 0],
                  [0, 1, 1, 1, 1, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 0, 0]], dtype=torch.uint8).unsqueeze(0)   # (1, 6, 6)


class 글자_데이터셋(Dataset):
    """그림 한 장짜리 데이터셋. 꺼낼 때마다 transform을 새로 적용한다."""

    def __init__(self, transform: v2.Transform | None = None) -> None:
        self.그림들 = [ㄱ]
        self.transform = transform

    def __len__(self) -> int:
        return len(self.그림들)

    def __getitem__(self, i: int) -> torch.Tensor:
        그림 = self.그림들[i]
        return self.transform(그림) if self.transform else 그림


def 그려_보기(그림들: list[torch.Tensor]) -> None:
    """여러 그림을 #과 . 으로 나란히 찍는다."""
    for 줄 in range(그림들[0].shape[1]):
        print("   ".join("".join("#" if v else "." for v in g[0, 줄].tolist()) for g in 그림들))


torch.manual_seed(1)
증강 = v2.Compose([v2.RandomHorizontalFlip(p=0.5),
                  v2.RandomCrop(size=6, padding=1)])
데이터 = 글자_데이터셋(transform=증강)
그려_보기([데이터[0] for _ in range(5)])        # 같은 0번 샘플을 다섯 번 꺼낸다
```

```text
..####   ......   ####..   ..####   .####.
.....#   .####.   #.....   ..#...   ....#.
.....#   ....#.   #.....   ..#...   ....#.
.....#   ....#.   #.....   ..#...   ....#.
......   ....#.   ......   ......   ......
......   ......   ......   ......   ......
```

그림 한 장(한글 자음 ㄱ)뿐인 데이터셋에서 **같은 0번 샘플을 다섯 번** 꺼냈습니다. 그런데 결과가 매번 다르죠. 첫 번째는 오른쪽 위로 한 칸씩 밀렸고, 두 번째는 원래 모습 그대로이고, 세 번째와 네 번째는 좌우가 뒤집힌 채 위치도 옮겨졌고, 다섯 번째는 위로 한 칸 올라갔어요. `transform`이 `__getitem__` 안에서 꺼낼 때마다 새로 적용되기 때문입니다.

여기서 증강의 중요한 성질이 나옵니다. **증강은 데이터 개수를 늘리지 않습니다.** 데이터셋의 길이는 그대로 1이고, 한 에폭에 이 그림은 한 번만 나와요. 대신 에폭이 바뀔 때마다 조금씩 다른 모습으로 나옵니다. 100에폭을 학습하면 모델은 같은 그림의 100가지 변형을 보게 되는 셈이죠. 파일을 미리 100배로 불려 저장하지 않아도 되니 디스크도 아낍니다.

> **Q. 증강은 많이 할수록 좋은가요?**
> 아닙니다. 증강은 **정답이 바뀌지 않는 범위**에서만 해야 해요. 위 결과의 세 번째 그림을 보세요. 좌우가 뒤집힌 ㄱ은 더 이상 ㄱ이 아닙니다. 글자를 알아보는 모델이라면 좌우 뒤집기를 쓰면 안 되는 거죠. 숫자 6을 상하로 뒤집으면 9처럼 보이고, 왼쪽·오른쪽을 구분하는 표지판도 뒤집으면 뜻이 반대가 됩니다. 증강을 고를 때는 "이렇게 바꾼 그림에도 사람이 같은 정답을 붙일까?"를 먼저 물어보세요. 그리고 증강은 **학습 데이터에만** 합니다. 검증 데이터는 실제로 만날 그림 그대로여야 정확한 점수를 잴 수 있어요. 7.8절에서 둘을 나누는 방법을 봅니다.

## 7.7 collate_fn: 길이가 다른 샘플 묶기

### 기본 규칙이 실패할 때

그림은 미리 크기를 맞춰 두면 되지만, 문장은 길이가 제각각입니다. "최고"는 두 글자, "기다리다 지쳤어요"는 아홉 글자죠. 예제용으로 만든 짧은 식당 리뷰 여덟 개를 데이터셋으로 만들어 보겠습니다. 모델은 글자를 바로 읽지 못하니, 글자마다 번호를 붙여 숫자 목록으로 바꿉니다. 번호는 1부터 붙이고 0은 비워 두었어요. 잠시 뒤에 쓸 자리입니다.

```python
import torch
from torch.utils.data import DataLoader, Dataset

# 예제용으로 만든 짧은 식당 리뷰와 라벨(1: 좋음, 0: 나쁨)
리뷰들 = [("맛있어요", 1), ("너무 짜요", 0), ("또 오고 싶어요", 1), ("별로", 0),
         ("친절하고 깔끔해요", 1), ("다시는 안 가요", 0), ("최고", 1), ("기다리다 지쳤어요", 0)]


class 리뷰_데이터셋(Dataset):
    """문장을 글자 번호 텐서로 바꿔 돌려준다. 0번은 빈칸 채우기(패딩)용으로 비워 둔다."""

    def __init__(self, 자료: list[tuple[str, int]]) -> None:
        self.자료 = 자료
        글자들 = sorted({글자 for 문장, _ in 자료 for 글자 in 문장})
        self.글자_번호 = {글자: i + 1 for i, 글자 in enumerate(글자들)}

    def __len__(self) -> int:
        return len(self.자료)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, int]:
        문장, 라벨 = self.자료[i]
        return torch.tensor([self.글자_번호[글자] for 글자 in 문장]), 라벨


데이터 = 리뷰_데이터셋(리뷰들)
print("글자 종류:", len(데이터.글자_번호))
for i in range(3):
    번호들, 라벨 = 데이터[i]
    print(f"{리뷰들[i][0]} → {번호들.tolist()}, 라벨 {라벨}")

try:
    next(iter(DataLoader(데이터, batch_size=4)))
except RuntimeError as e:
    print("오류:", e)
```

```text
글자 종류: 30
맛있어요 → [13, 22, 19, 21], 라벨 1
너무 짜요 → [7, 14, 1, 25, 21], 라벨 0
또 오고 싶어요 → [10, 1, 20, 3, 1, 17, 19, 21], 라벨 1
오류: stack expects each tensor to be equal size, but got [4] at entry 0 and [5] at entry 1
```

여덟 문장에 쓰인 서로 다른 글자는 띄어쓰기까지 30종류입니다. "맛있어요"는 네 글자라 숫자 4개, "너무 짜요"는 띄어쓰기 포함 다섯 글자라 숫자 5개가 됐어요. 띄어쓰기의 번호가 1번이라 "너무 짜요"의 세 번째 숫자가 1이죠.

그런데 이걸 DataLoader로 4개씩 묶으려 하자 오류가 났습니다. 7.3절에서 본 기본 규칙은 텐서를 `torch.stack`으로 쌓는데, 4장에서 배운 것처럼 `stack`은 모양이 같은 텐서만 쌓을 수 있어요. 4장 "오류 메시지 읽는 법"에서 미리 봤던 바로 그 오류로, "0번은 [4]인데 1번은 [5]"라고 정확히 짚어 줍니다.

글자를 번호로 바꾸는 이 방식은 가장 단순한 형태입니다. 실제 한국어 처리에서는 글자보다 큰 단위로 자르는 토크나이저를 쓰는데, 13장에서 자세히 다뤄요. 어떤 방식으로 자르든 "문장마다 길이가 다르다"는 문제는 똑같이 남습니다.

### 패딩으로 길이 맞추기

해결책은 짧은 문장의 뒤를 **빈칸 번호(0)로 채워서** 가장 긴 문장에 길이를 맞추는 것입니다. 이것을 **패딩(padding)** 이라고 해요. 0번을 비워 둔 이유가 이것입니다. DataLoader의 `collate_fn` 자리에 이 일을 하는 함수를 넘기면 기본 규칙 대신 그 함수로 배치를 만들어요.

```python
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

# 앞 블록의 리뷰 데이터셋이 돌려준 샘플 세 개를 그대로 옮겨 적었다
샘플들 = [(torch.tensor([13, 22, 19, 21]), 1),
         (torch.tensor([7, 14, 1, 25, 21]), 0),
         (torch.tensor([10, 1, 20, 3, 1, 17, 19, 21]), 1)]


def 패딩_묶기(배치: list[tuple[torch.Tensor, int]]) -> dict[str, torch.Tensor]:
    """길이가 다른 문장들을 가장 긴 문장에 맞춰 0으로 채워 묶는다."""
    문장들 = [문장 for 문장, _ in 배치]
    return {
        "입력": pad_sequence(문장들, batch_first=True, padding_value=0),
        "길이": torch.tensor([len(문장) for 문장 in 문장들]),
        "정답": torch.tensor([라벨 for _, 라벨 in 배치]),
    }


배치 = 패딩_묶기(샘플들)                    # collate_fn은 그냥 함수라 직접 불러 볼 수 있다
print(배치["입력"])
print("길이:", 배치["길이"].tolist(), "정답:", 배치["정답"].tolist())
print("진짜 글자 자리(마스크):")
print((배치["입력"] != 0).int())

로더 = DataLoader(샘플들, batch_size=2, collate_fn=패딩_묶기)   # 리스트도 데이터셋이 된다
for 배치 in 로더:
    print(tuple(배치["입력"].shape), 배치["길이"].tolist())
```

```text
tensor([[13, 22, 19, 21,  0,  0,  0,  0],
        [ 7, 14,  1, 25, 21,  0,  0,  0],
        [10,  1, 20,  3,  1, 17, 19, 21]])
길이: [4, 5, 8] 정답: [1, 0, 1]
진짜 글자 자리(마스크):
tensor([[1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1]], dtype=torch.int32)
(2, 5) [4, 5]
(1, 8) [8]
```

`collate_fn`은 특별한 것이 아니라 **샘플 목록을 받아 배치 하나를 돌려주는 평범한 함수**입니다. 그래서 DataLoader 없이 직접 불러 볼 수 있었어요. 안에서 하는 일은 세 가지입니다.

- **`pad_sequence`**: 길이가 4, 5, 8인 문장을 가장 긴 8에 맞춰 뒤를 0으로 채우고 쌓았습니다. `batch_first=True`를 줘야 `(문장 수, 길이)` 순서가 돼요. 주지 않으면 `(길이, 문장 수)`로 나옵니다.
- **길이**: 원래 길이 `[4, 5, 8]`을 따로 담아 두었습니다. 11장의 순환 신경망은 이 값을 받아 채운 칸을 건너뛸 수 있어요.
- **마스크**: `배치["입력"] != 0`은 진짜 글자 자리만 1인 표를 만듭니다. 4장에서 본 마스크 그대로예요. 12장의 어텐션은 이 마스크로 "채운 칸은 보지 마"라고 알려 줍니다.

마지막 부분에서는 DataLoader에 **평범한 리스트**를 데이터셋으로 넣었습니다. 7.1절 Q&A에서 말했듯 리스트도 `__len__`과 `__getitem__`이 있으니 데이터셋 노릇을 할 수 있어요. 배치마다 길이가 다른 것도 보세요. 첫 배치는 가장 긴 문장이 5글자라 `(2, 5)`, 둘째 배치는 문장 하나라 `(1, 8)`입니다. 패딩은 **배치 안에서만** 맞추기 때문에, 데이터 전체에서 가장 긴 문장에 맞출 필요가 없어요.

### 비슷한 길이끼리 묶기

그런데 패딩한 0도 모델은 계산합니다. 채운 칸이 많을수록 헛일이 늘어나는 거죠. 길이가 3~60글자로 제각각인 문장 1,000개로 얼마나 낭비되는지 재 보겠습니다.

```python
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

torch.manual_seed(0)
# 예제용: 길이가 3~60글자로 제각각인 문장 1,000개 (글자 번호는 1~9)
문장들 = [torch.randint(1, 10, (int(n),)) for n in torch.randint(3, 61, (1000,))]


def 패딩_묶기(배치: list[torch.Tensor]) -> torch.Tensor:
    return pad_sequence(배치, batch_first=True, padding_value=0)


def 패딩_비율(로더: DataLoader) -> float:
    """배치에 들어간 칸 중 0으로 채운 칸의 비율."""
    전체 = 빈칸 = 0
    for 배치 in 로더:
        전체 += 배치.numel()
        빈칸 += (배치 == 0).sum().item()
    return 빈칸 / 전체


g = torch.Generator().manual_seed(0)
그냥 = DataLoader(문장들, batch_size=32, shuffle=True, collate_fn=패딩_묶기, generator=g)
print(f"그냥 섞었을 때 패딩 비율: {패딩_비율(그냥):.1%}")

# 길이순으로 줄 세운 뒤 32개씩 끊고, 묶음의 순서만 섞는다
길이순 = sorted(range(len(문장들)), key=lambda i: len(문장들[i]))
묶음들 = [길이순[i:i + 32] for i in range(0, len(길이순), 32)]
묶음들 = [묶음들[i] for i in torch.randperm(len(묶음들), generator=g).tolist()]
비슷한_길이끼리 = DataLoader(문장들, batch_sampler=묶음들, collate_fn=패딩_묶기)
print(f"비슷한 길이끼리 묶었을 때: {패딩_비율(비슷한_길이끼리):.1%}")
print("배치 수:", len(그냥), len(비슷한_길이끼리))
```

```text
그냥 섞었을 때 패딩 비율: 46.1%
비슷한 길이끼리 묶었을 때: 2.6%
배치 수: 32 32
```

그냥 섞어서 32개씩 묶었더니 배치에 들어간 칸의 46.1%가 0으로 채운 칸이었습니다. 짧은 문장과 긴 문장이 한 배치에 섞이니 짧은 쪽이 대부분 빈칸으로 채워진 거예요. 계산의 절반 가까이가 헛일입니다.

두 번째 방법은 문장을 **길이순으로 줄 세운 뒤 32개씩 끊고**, 그렇게 만든 묶음들의 순서만 섞었습니다. 비슷한 길이끼리 한 배치에 모이니 패딩 비율이 2.6%로 줄었어요. 배치 수는 32개로 같습니다. DataLoader의 `batch_sampler`에 "배치마다 어떤 번호들을 묶을지" 목록을 직접 넘겨서 만든 거예요. `batch_sampler`를 쓰면 묶는 방법을 우리가 정했으니 `batch_size`와 `shuffle`은 주지 않습니다.

이 방법을 **버킷팅(bucketing)** 이라고 부르고, 문장을 다루는 학습에서 널리 씁니다. 다만 배치 안의 문장들이 너무 비슷해지면 섞는 효과가 줄어드니, 실무에서는 데이터를 큰 덩어리로 섞은 다음 덩어리 안에서만 길이순으로 정렬하는 식으로 절충해요.

## 7.8 학습/검증 나누기: random_split과 재현 가능한 분할

### random_split과 씨앗

2장에서 데이터를 학습/검증/테스트로 나누는 이유를 봤죠. 모델이 처음 보는 데이터에서 얼마나 잘하는지 재려면 학습에 쓰지 않은 데이터를 떼어 둬야 합니다. 7.4절의 귤 데이터처럼 처음부터 파일이 나뉘어 있으면 좋겠지만, 데이터셋 하나만 받았다면 PyTorch의 `random_split`으로 나눠요.

```python
import torch
from torch.utils.data import TensorDataset, random_split

데이터 = TensorDataset(torch.arange(100).float(), torch.arange(100))   # 샘플 100개 (예제용)

학습, 검증 = random_split(데이터, [0.8, 0.2], generator=torch.Generator().manual_seed(42))
print("크기:", len(학습), len(검증), type(학습).__name__)
print("검증에 뽑힌 번호(앞 8개):", 검증.indices[:8])
print("검증 2번 샘플:", 검증[2], "= 원래 데이터의", 검증.indices[2], "번")

다시_학습, 다시_검증 = random_split(데이터, [0.8, 0.2], generator=torch.Generator().manual_seed(42))
print("같은 씨앗이면 같은 분할:", 검증.indices == 다시_검증.indices)
print("학습과 검증이 겹치나:", bool(set(학습.indices) & set(검증.indices)))

학, 검, 시 = random_split(데이터, [70, 15, 15], generator=torch.Generator().manual_seed(42))
print("세 갈래:", len(학), len(검), len(시))
```

```text
크기: 80 20 Subset
검증에 뽑힌 번호(앞 8개): [2, 91, 8, 53, 30, 90, 26, 23]
검증 2번 샘플: (tensor(8.), tensor(8)) = 원래 데이터의 8 번
같은 씨앗이면 같은 분할: True
학습과 검증이 겹치나: False
세 갈래: 70 15 15
```

- **`[0.8, 0.2]`**: 비율로 나눕니다. 100개가 80개와 20개로 나뉘었어요. `[70, 15, 15]`처럼 개수로 줘도 되고, 세 갈래 이상으로도 나눌 수 있습니다.
- **`Subset`**: 결과는 데이터를 복사한 것이 아니라 **원래 데이터셋과 번호 목록**을 들고 있는 `Subset`입니다. 검증의 2번 샘플을 달라고 하면 `indices[2]`인 원래 8번 샘플을 꺼내 줘요. 4장에서 슬라이스가 원본을 들여다보는 창이었던 것처럼, Subset도 원래 데이터셋을 들여다보는 창입니다.
- **`generator`**: 씨앗을 고정한 `Generator`를 넘기면 언제 실행해도 같은 분할이 나옵니다. 이게 정말 중요해요. 씨앗 없이 나누면 실행할 때마다 검증 데이터가 바뀌어서, 어제 모델과 오늘 모델의 점수를 비교할 수가 없습니다. 어제는 쉬운 문제로, 오늘은 어려운 문제로 시험을 본 셈이니까요. 학습과 검증이 겹치지 않는다는 것도 확인했습니다.

### transform이 다를 때의 함정

그런데 7.6절에서 증강은 **학습 데이터에만** 해야 한다고 했죠. `random_split`으로 나눈 학습용과 검증용은 같은 원래 데이터셋을 들여다보는 창이라서, 원래 데이터셋에 증강 transform을 걸면 검증용에도 증강이 걸립니다. 실제로 확인해 보겠습니다. 증강 흉내로 작은 잡음을 더하는 `흔들기`를 transform으로 썼어요.

```python
from collections.abc import Callable

import torch
from torch.utils.data import Dataset, Subset, random_split


class 숫자_데이터셋(Dataset):
    """꺼낼 때 transform을 적용하는 아주 작은 데이터셋 (예제용)."""

    def __init__(self, transform: Callable[[torch.Tensor], torch.Tensor] | None = None) -> None:
        self.X = torch.arange(10).float()
        self.transform = transform

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, i: int) -> torch.Tensor:
        x = self.X[i]
        return self.transform(x) if self.transform else x


def 흔들기(x: torch.Tensor) -> torch.Tensor:
    """학습용 증강 흉내: 작은 잡음을 더한다."""
    return x + torch.randn(()) * 0.1


torch.manual_seed(0)
g = torch.Generator().manual_seed(42)

# 잘못된 방법: 하나를 나누면 검증 쪽도 같은 transform을 쓴다
학습, 검증 = random_split(숫자_데이터셋(transform=흔들기), [0.7, 0.3], generator=g)
print("잘못: 검증 0번을 두 번 꺼내면", round(검증[0].item(), 4), round(검증[0].item(), 4))

# 바른 방법: transform이 다른 두 데이터셋을 만들고, 같은 번호로 나눈다
번호 = torch.randperm(10, generator=g).tolist()
학습 = Subset(숫자_데이터셋(transform=흔들기), 번호[:7])
검증 = Subset(숫자_데이터셋(transform=None), 번호[7:])
print("바름: 검증 0번을 두 번 꺼내면", 검증[0].item(), 검증[0].item())
print("학습 0번을 두 번 꺼내면", round(학습[0].item(), 4), round(학습[0].item(), 4))
```

```text
잘못: 검증 0번을 두 번 꺼내면 9.1541 8.9707
바름: 검증 0번을 두 번 꺼내면 0.0 0.0
학습 0번을 두 번 꺼내면 2.7821 3.0568
```

잘못된 방법에서는 검증 0번 샘플을 두 번 꺼냈더니 9.1541, 8.9707로 값이 매번 달라졌습니다. 원래 값은 9인데 잡음이 섞인 거예요. 검증 점수가 잴 때마다 흔들리면 믿을 수가 없죠.

바른 방법은 **transform만 다른 데이터셋 두 개**를 만들고, **같은 번호 목록**을 나눠서 각각 `Subset`으로 감싸는 것입니다. 번호는 `torch.randperm`으로 0~9를 씨앗 고정해 섞은 뒤 앞 7개는 학습, 뒤 3개는 검증으로 잘랐어요. 이제 검증 0번은 몇 번 꺼내도 0.0으로 같고, 학습 0번만 꺼낼 때마다 달라집니다. 번호를 한곳에서 섞어 잘랐으니 두 데이터셋이 겹칠 일도 없어요. 7.11절 실습이 바로 이 방법을 씁니다.

데이터셋을 두 번 만들면 메모리가 두 배로 들지 않을까 걱정될 수 있는데, 7.5절의 그림 폴더 데이터셋처럼 `__init__`에서 경로 목록만 들고 있다면 거의 차이가 없어요. 무거운 일은 `__getitem__`에서 한다는 7.1절의 원칙이 여기서도 도움이 됩니다.

> **Q. 테스트 데이터도 이렇게 나누면 되나요?**
> 나눌 수는 있지만, 테스트 데이터는 되도록 **처음부터 따로** 두고 마지막에 한 번만 쓰세요. 검증 점수를 보면서 모델을 이리저리 고치다 보면 모르는 사이에 모델이 검증 데이터에 맞춰지기 때문입니다. 날짜 순서가 있는 데이터라면 무작위로 섞어 나누면 안 되고 과거로 학습해 미래로 검증해야 한다는 점도 2장에서 본 그대로예요. 그럴 때는 `random_split` 대신 날짜순으로 정렬한 번호를 앞뒤로 잘라 `Subset`을 만들면 됩니다.

## 7.9 불균형 데이터: WeightedRandomSampler

공장에서 나온 제품 1,000개 중 불량이 50개뿐이라고 해 봅시다. 2장에서 `class_weight`로 다뤄 봤듯이 이런 **불균형 데이터**로 그냥 학습하면, 모델은 "전부 정상"이라고만 답해도 95%를 맞히니 불량을 찾는 법을 열심히 배우지 않습니다. 한 가지 대처는 **드문 클래스를 더 자주 뽑아서** 모델에게 자주 보여 주는 것이에요. DataLoader의 `sampler` 자리에 `WeightedRandomSampler`를 넘기면 됩니다.

```python
import torch
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler

# 예제용 불균형 데이터: 정상 950개, 불량 50개
정답 = torch.cat([torch.zeros(950, dtype=torch.long), torch.ones(50, dtype=torch.long)])
데이터 = TensorDataset(torch.arange(1000), 정답)        # 입력 자리에는 샘플 번호를 넣어 둔다


def 한_에폭_세기(로더: DataLoader) -> None:
    """한 에폭 동안 나온 클래스별 개수와, 불량 샘플이 몇 종류였는지 센다."""
    개수 = torch.zeros(2, dtype=torch.long)
    본_불량 = set()
    배치별_불량 = []
    for 번호, y in 로더:
        개수 += torch.bincount(y, minlength=2)
        본_불량.update(번호[y == 1].tolist())
        배치별_불량.append(int(y.sum()))
    print(f"  정상 {개수[0]}개, 불량 {개수[1]}개 (서로 다른 불량 샘플 {len(본_불량)}종)")
    print(f"  배치마다 불량 개수(앞 8배치): {배치별_불량[:8]}")


g = torch.Generator().manual_seed(0)
print("그냥 섞기:")
한_에폭_세기(DataLoader(데이터, batch_size=50, shuffle=True, generator=g))

클래스별_개수 = torch.bincount(정답)                    # [950, 50]
샘플_가중치 = 1.0 / 클래스별_개수[정답].float()          # 드문 클래스일수록 크게
print(f"가중치: 정상 {샘플_가중치[0]:.5f}, 불량 {샘플_가중치[-1]:.5f}")
샘플러 = WeightedRandomSampler(샘플_가중치, num_samples=len(데이터),
                              replacement=True, generator=g)
print("WeightedRandomSampler:")
한_에폭_세기(DataLoader(데이터, batch_size=50, sampler=샘플러))
```

```text
그냥 섞기:
  정상 950개, 불량 50개 (서로 다른 불량 샘플 50종)
  배치마다 불량 개수(앞 8배치): [2, 4, 2, 2, 2, 4, 5, 3]
가중치: 정상 0.00105, 불량 0.02000
WeightedRandomSampler:
  정상 500개, 불량 500개 (서로 다른 불량 샘플 50종)
  배치마다 불량 개수(앞 8배치): [27, 25, 24, 22, 29, 26, 23, 23]
```

먼저 그냥 섞은 경우입니다. 한 에폭에 정상 950개, 불량 50개가 정확히 한 번씩 나왔고, 50개씩 묶은 배치를 앞에서부터 8개 보면 불량이 2~5개뿐이었어요. 모델 입장에서는 배치마다 정상 품목만 잔뜩 보는 셈이죠.

`WeightedRandomSampler`는 샘플마다 **뽑힐 가중치**를 받습니다. 여기서는 "1 / 그 클래스의 개수"로 줬어요. 정상 샘플 하나는 1/950 ≈ 0.00105, 불량 샘플 하나는 1/50 = 0.02입니다. 이렇게 하면 정상 950개의 가중치 합과 불량 50개의 가중치 합이 둘 다 1이 되어, 두 클래스가 **같은 확률**로 뽑혀요. `클래스별_개수[정답]`은 4장에서 본 목록으로 고르기 인덱싱으로, 샘플마다 자기 클래스의 개수를 꺼내 1,000개짜리 텐서를 만든 것입니다.

결과를 보면 한 에폭 1,000번 뽑기에서 정상과 불량이 500개씩, 배치마다 불량이 22~29개로 거의 반반이 됐습니다. 무작위로 뽑으니 정확히 반반일 필요는 없고 씨앗에 따라 조금씩 달라져요.

여기서 놓치면 안 되는 숫자가 있습니다. **서로 다른 불량 샘플은 여전히 50종**이에요. 불량 500번은 같은 50개를 평균 10번씩 반복해서 뽑은 것입니다. `replacement=True`(뽑은 것을 다시 넣고 또 뽑기)여야 이렇게 같은 샘플을 여러 번 뽑을 수 있어요. 새로운 불량 사례가 생긴 것이 아니니, 모델이 그 50개를 통째로 외워 버릴 위험이 커집니다. 그래서 이 샘플러는 7.6절의 데이터 증강과 함께 쓰는 경우가 많아요. 같은 불량품이 뽑힐 때마다 조금씩 다른 모습으로 나오게 하는 거죠.

몇 가지를 더 기억해 두세요.

- `sampler`가 순서를 정하므로 `shuffle=True`와 함께 쓸 수 없습니다. 함께 주면 오류가 나요.
- 샘플러는 **학습용 로더에만** 씁니다. 검증 데이터는 실제 비율 그대로 평가해야 실제 상황의 성능을 알 수 있어요.
- 다른 대처로, 뽑는 비율은 그대로 두고 손실 함수에서 드문 클래스의 틀림에 더 큰 벌점을 주는 방법도 있습니다. 6장의 `CrossEntropyLoss`에 `weight`를 넘기는 방식이에요. 어느 쪽이 나은지는 데이터마다 달라서, 8장의 방법으로 검증 곡선을 보며 정합니다.

## 7.10 num_workers와 병목 찾기

### 일꾼 프로세스와 `__main__` 가드

지금까지는 샘플을 꺼내는 일을 학습하는 프로그램이 직접 했습니다. 주방으로 치면 요리사가 재료 손질까지 혼자 하는 거예요. 그동안 화구(GPU)는 놀고 있죠. `num_workers`를 1 이상으로 주면 DataLoader가 **일꾼 프로세스**를 따로 띄워서, 모델이 계산하는 동안 일꾼들이 다음 배치를 미리 꺼내 둡니다. 1권 15장에서 "요리사를 여러 명 고용한다"고 비유했던 멀티프로세싱이 바로 이것이에요.

그런데 macOS와 Windows에서 처음 `num_workers`를 쓰면 많은 사람이 이상한 오류를 만납니다. 직접 확인해 보죠. 똑같은 코드를 `if __name__ == "__main__":` 가드 없이 쓴 파일과 가드 안에 넣은 파일로 저장해서 따로 실행해 봤습니다.

```python
import subprocess
import sys
from pathlib import Path

가드_없음 = """
import torch
from torch.utils.data import DataLoader, TensorDataset

로더 = DataLoader(TensorDataset(torch.arange(8)), batch_size=4, num_workers=2)
for (배치,) in 로더:
    print("배치:", 배치.tolist())
"""

가드_있음 = """
import torch
from torch.utils.data import DataLoader, TensorDataset


def main() -> None:
    로더 = DataLoader(TensorDataset(torch.arange(8)), batch_size=4, num_workers=2)
    for (배치,) in 로더:
        print("배치:", 배치.tolist())


if __name__ == "__main__":
    main()
"""

for 이름, 본문 in [("가드_없음.py", 가드_없음), ("가드_있음.py", 가드_있음)]:
    Path(이름).write_text(본문, encoding="utf-8")            # 파일로 저장해서
    결과 = subprocess.run([sys.executable, 이름],              # 따로 실행해 본다
                          capture_output=True, text=True, timeout=120)
    print(f"--- {이름} (종료 코드 {결과.returncode})")
    if 결과.stdout:
        print(결과.stdout.strip())
    줄들 = [줄.strip() for 줄 in 결과.stderr.splitlines()]
    첫줄 = "An attempt has been made to start a new process before the"
    if 첫줄 in 줄들:                                          # 일꾼 프로세스가 남긴 설명
        시작 = 줄들.index(첫줄)
        print("\n".join(줄들[시작:시작 + 6]))
```

```text
--- 가드_없음.py (종료 코드 1)
An attempt has been made to start a new process before the
current process has finished its bootstrapping phase.

This probably means that you are not using fork to start your
child processes and you have forgotten to use the proper idiom
in the main module:
--- 가드_있음.py (종료 코드 0)
배치: [0, 1, 2, 3]
배치: [4, 5, 6, 7]
```

가드가 없는 파일은 종료 코드 1로 실패했고, 일꾼 프로세스가 "현재 프로세스가 준비 단계를 마치기 전에 새 프로세스를 띄우려 했다. 메인 모듈에 알맞은 관용구를 쓰지 않은 것 같다"는 설명을 남겼습니다. 가드 안에 넣은 파일은 배치 두 개를 잘 받았어요.

이유는 일꾼을 띄우는 방식에 있습니다. macOS와 Windows는 일꾼 프로세스를 새로 시작하면서 **우리 파일을 처음부터 다시 import** 합니다(이 방식을 spawn이라고 해요). 가드가 없으면 일꾼이 import하는 순간 파일 맨 아래의 DataLoader 반복이 또 실행되고, 일꾼이 다시 일꾼을 띄우려다 멈추는 거예요. 1권 14장에서 배운 대로 `if __name__ == "__main__":` 아래의 코드는 **직접 실행할 때만** 돌고 import할 때는 건너뛰니, 일꾼들은 함수와 클래스 정의만 가져가고 반복은 하지 않습니다. Linux는 파이썬 3.13까지 프로세스를 통째로 복제하는 방식(fork)이 기본이라 가드 없이도 돌아가지만, 3.14부터는 Linux도 다른 방식(forkserver)이 기본이 되어 가드가 필요합니다. 어디서나 돌아가는 코드를 쓰려면 **`num_workers`를 쓸 때는 항상 가드 안에서** 실행하는 습관을 들이세요. 이 장의 나머지 예제도 모두 그렇게 씁니다.

같은 이유로 Jupyter 노트북에서 `num_workers`를 쓰면 데이터셋 클래스를 노트북 셀 안에 정의했을 때 일꾼이 그 클래스를 찾지 못해 실패할 수 있어요. 그럴 때는 데이터셋 클래스를 `.py` 파일로 옮겨 import하면 해결됩니다.

### 일꾼이 몇이면 빨라질까

일꾼 수에 따라 얼마나 달라지는지 재 보겠습니다. 실제 디스크와 모델을 쓰면 컴퓨터마다 결과가 너무 달라서, 샘플 하나를 읽는 데 10ms, 배치 하나로 학습하는 데 50ms가 걸린다고 정하고 `time.sleep`으로 흉내 냈어요. 그리고 학습 반복 중에 **다음 배치를 기다린 시간**을 따로 쟀습니다.

```python
import time

import torch
from torch.utils.data import DataLoader, Dataset

읽기_시간 = 0.01      # 샘플 하나를 디스크에서 읽고 푸는 데 10ms 걸린다고 치자
계산_시간 = 0.05      # 배치 하나로 모델을 학습시키는 데 50ms 걸린다고 치자


class 느린_데이터셋(Dataset):
    """꺼낼 때마다 읽기_시간만큼 기다리는 데이터셋 (디스크 읽기 흉내)."""

    def __len__(self) -> int:
        return 160

    def __getitem__(self, i: int) -> torch.Tensor:
        time.sleep(읽기_시간)
        return torch.full((3, 32, 32), float(i))


def 한_에폭(로더: DataLoader) -> tuple[float, float]:
    """한 에폭 전체 시간과, 그중 다음 배치를 기다린 시간을 잰다."""
    대기 = 0.0
    시작 = time.perf_counter()
    반복자 = iter(로더)
    while True:
        t = time.perf_counter()
        배치 = next(반복자, None)                # 다음 배치가 올 때까지 기다린다
        대기 += time.perf_counter() - t
        if 배치 is None:
            break
        time.sleep(계산_시간)                    # 학습 계산 흉내
    return time.perf_counter() - 시작, 대기


def main() -> None:
    for 일꾼 in [0, 2, 4]:
        로더 = DataLoader(느린_데이터셋(), batch_size=16, num_workers=일꾼,
                         persistent_workers=일꾼 > 0)   # 에폭이 끝나도 일꾼을 살려 둔다
        첫_전체, _ = 한_에폭(로더)
        전체, 대기 = 한_에폭(로더)
        print(f"num_workers={일꾼}: 첫 에폭 {첫_전체:.1f}초, 둘째 에폭 {전체:.1f}초 "
              f"(그중 데이터 대기 {대기 / 전체:.0%})")


if __name__ == "__main__":
    main()
```

```text
num_workers=0: 첫 에폭 2.5초, 둘째 에폭 2.5초 (그중 데이터 대기 78%)
num_workers=2: 첫 에폭 1.6초, 둘째 에폭 1.1초 (그중 데이터 대기 51%)
num_workers=4: 첫 에폭 1.3초, 둘째 에폭 0.7초 (그중 데이터 대기 27%)
```

이 책의 실행 환경에서 잰 값이라 여러분의 숫자는 조금 다를 수 있지만, 흐름은 같을 거예요.

- **`num_workers=0`**: 한 에폭에 약 2.5초가 걸렸고, 그중 78%가 데이터를 기다린 시간입니다. 배치 하나(16개)를 꺼내는 데 160ms, 계산은 50ms이니 대부분의 시간 동안 계산 쪽이 놀고 있었던 거예요. 이런 상태를 **데이터 병목**이라고 합니다.
- **`num_workers=2`, `4`**: 일꾼이 늘수록 둘째 에폭이 1.1초, 0.7초로 줄고 대기 비율도 약 50%, 약 25%로 떨어졌습니다. 일꾼 넷이 동시에 배치를 준비하니, 계산 50ms 동안 다음 배치가 거의 준비되어 있는 거죠.
- **첫 에폭이 더 느린 이유**: 일꾼 프로세스를 띄우고 각자 torch를 import하는 준비 시간이 들기 때문입니다. `persistent_workers=True`를 주면 에폭이 끝나도 일꾼을 살려 두어서, 둘째 에폭부터는 이 비용이 없어요. 주지 않으면 에폭마다 일꾼을 새로 띄웁니다.

일꾼은 많을수록 좋은 게 아닙니다. 일꾼마다 프로세스 하나와 그만큼의 메모리를 쓰고, 계산보다 데이터 준비가 빨라지면 더 늘려도 소용이 없어요. 위 예에서 대기 비율이 이미 4분의 1 정도까지 떨어졌으니 8개로 늘려도 얻을 것이 크지 않습니다. 보통 CPU 코어 수의 절반 정도에서 시작해 **대기 비율을 재 보며** 조절하세요. 일꾼마다 미리 준비해 두는 배치 수는 `prefetch_factor`(기본 2)로 바꿀 수 있습니다.

NVIDIA GPU를 쓴다면 `pin_memory=True`도 함께 주는 경우가 많습니다. 배치를 GPU로 옮기기 좋은 특별한 메모리 영역에 담아 두어 복사를 빠르게 하는 옵션이에요. Apple MPS에서는 아직 지원되지 않아 "MPS에서는 쓰지 않는다"는 경고만 나오므로 이 책의 예제에서는 쓰지 않았습니다. GPU 쪽 성능은 16장에서 자세히 봅니다.

### IterableDataset과 일꾼

7.3절에서 IterableDataset을 일꾼과 함께 쓸 때 주의할 점이 있다고 했죠. 주문 번호 0~5를 흘려보내는 데이터셋을 일꾼 2명으로 읽어 보겠습니다.

```python
from collections.abc import Iterator

from torch.utils.data import DataLoader, IterableDataset, get_worker_info


class 주문_흐름(IterableDataset):
    """주문 번호를 차례로 흘려보낸다. 나눠_읽기=True면 일꾼끼리 몫을 나눈다."""

    def __init__(self, 주문_수: int, 나눠_읽기: bool) -> None:
        self.주문_수 = 주문_수
        self.나눠_읽기 = 나눠_읽기

    def __iter__(self) -> Iterator[int]:
        정보 = get_worker_info()                 # 일꾼 안이면 (번호, 전체 수)를 알려 준다
        if not self.나눠_읽기 or 정보 is None:
            return iter(range(self.주문_수))
        # 일꾼 0은 0, 2, 4, ...  일꾼 1은 1, 3, 5, ... 처럼 건너뛰며 맡는다
        return iter(range(정보.id, self.주문_수, 정보.num_workers))


def main() -> None:
    for 나눠_읽기 in [False, True]:
        로더 = DataLoader(주문_흐름(6, 나눠_읽기), batch_size=None, num_workers=2)
        받은_것 = sorted(int(x) for x in 로더)
        print(f"나눠_읽기={나눠_읽기}: {받은_것}")


if __name__ == "__main__":
    main()
```

```text
나눠_읽기=False: [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
나눠_읽기=True: [0, 1, 2, 3, 4, 5]
```

`나눠_읽기=False`일 때 모든 주문이 **두 번씩** 나왔습니다. 일꾼마다 데이터셋을 통째로 복사해 가서 각자 처음부터 끝까지 흘려보냈기 때문이에요. 맵 스타일 데이터셋은 DataLoader가 "너는 3번, 너는 7번" 하고 번호를 나눠 주니 이런 일이 없지만, 번호가 없는 IterableDataset은 일꾼끼리 몫을 나누는 일을 **우리가 직접** 해야 합니다.

`get_worker_info()`는 일꾼 안에서 부르면 자기 번호(`id`)와 전체 일꾼 수(`num_workers`)를 알려 주고, 일꾼 없이 실행하면 `None`을 돌려줍니다. 이걸로 일꾼 0은 0, 2, 4번을, 일꾼 1은 1, 3, 5번을 맡게 하니 중복 없이 하나씩 나왔어요. `batch_size=None`은 배치로 묶지 않고 샘플을 하나씩 받겠다는 뜻입니다.

### 병목 찾기 체크리스트

학습이 생각보다 느리다면, 모델을 고치기 전에 데이터 파이프라인부터 의심해 보세요. 순서는 이렇습니다.

1. **기다린 시간을 잽니다.** 위의 `한_에폭`처럼 다음 배치를 기다린 시간과 계산 시간을 나눠 재면, 느린 쪽이 데이터인지 모델인지 바로 알 수 있어요. 대기 비율이 높으면 데이터 병목입니다.
2. **`num_workers`를 늘려 봅니다.** 0에서 2, 4, 8로 늘려 가며 대기 비율이 떨어지는지 봅니다. `persistent_workers=True`도 함께 주세요.
3. **`__getitem__`을 가볍게 합니다.** 큰 사진을 매번 읽어서 줄이고 있다면, 미리 작은 크기로 줄여 저장해 두세요. 매번 똑같이 나오는 손질(크기 바꾸기, 글자를 번호로 바꾸기)은 한 번만 해서 저장하고, 매번 달라야 하는 증강만 `__getitem__`에 남깁니다.
4. **배치 하나를 직접 들여다봅니다.** 속도와 별개로, 학습 전에 배치 하나를 꺼내 모양, 자료형, 값의 범위, 클래스 개수를 찍어 보는 습관이 많은 사고를 막아 줍니다. 다음 절 실습이 바로 그 일을 해요.

계산 쪽이 느린 경우, 즉 GPU가 일을 제대로 하고 있는지 자세히 들여다보는 프로파일러는 16장에서 다룹니다.

## 7.11 실습: 도형 그림 파이프라인 한 바퀴

이 장에서 배운 것을 모두 이어서 학습 직전까지의 파이프라인을 완성해 보겠습니다. 데이터는 7.5절의 `도형_만들기.py`로 만든 예제용 도형 그림인데, 이번에는 일부러 **불균형**하게 동그라미 120장, 네모 60장, 세모 20장을 만들어요. 할 일은 다섯 가지입니다.

1. 씨앗을 고정해 학습 80%, 검증 20%로 나누기
2. 학습용 그림에서만 색 채널별 평균과 표준편차 구하기
3. 학습용에는 증강과 정규화, 검증용에는 정규화만 걸기
4. 학습용 로더에는 WeightedRandomSampler, 둘 다 일꾼 2명
5. 한 에폭을 돌며 배치 모양, 값의 범위, 클래스 개수를 확인하고, 검증 데이터가 매번 같은지 확인하기

`도형_만들기.py`를 같은 폴더에 두고 실행하세요. 일꾼을 쓰니 7.10절에서 본 대로 `main()` 함수와 `__main__` 가드로 감쌌습니다.

```python
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Subset, WeightedRandomSampler
from torchvision.datasets import ImageFolder
from torchvision.transforms import v2

from 도형_만들기 import 도형_폴더_만들기

뿌리 = Path("data/shapes_practice")
씨앗 = 42


def 학습_검증_번호(전체_수: int, 검증_비율: float = 0.2) -> tuple[list[int], list[int]]:
    """씨앗을 고정해 섞은 번호를 학습용과 검증용으로 자른다."""
    번호 = torch.randperm(전체_수, generator=torch.Generator().manual_seed(씨앗)).tolist()
    검증_수 = int(전체_수 * 검증_비율)
    return 번호[검증_수:], 번호[:검증_수]


def 채널_통계(데이터: Subset) -> tuple[list[float], list[float]]:
    """학습용 그림만으로 색 채널별 평균과 표준편차를 구한다."""
    모두 = torch.stack([그림 for 그림, _ in 데이터])            # (N, 3, 32, 32)
    return 모두.mean(dim=(0, 2, 3)).tolist(), 모두.std(dim=(0, 2, 3)).tolist()


def 로더_만들기() -> tuple[DataLoader, DataLoader, list[str]]:
    학습_번호, 검증_번호 = 학습_검증_번호(len(ImageFolder(뿌리)))
    기본 = [v2.ToImage(), v2.ToDtype(torch.float32, scale=True)]
    평균, 표준편차 = 채널_통계(Subset(ImageFolder(뿌리, transform=v2.Compose(기본)), 학습_번호))
    print("학습용 채널 평균:", [round(m, 3) for m in 평균])

    정규화 = v2.Normalize(mean=평균, std=표준편차)
    학습_변환 = v2.Compose([v2.ToImage(),
                          v2.RandomHorizontalFlip(p=0.5),
                          v2.RandomCrop(size=32, padding=3, fill=255),   # 흰 바탕색으로 테두리
                          v2.ToDtype(torch.float32, scale=True), 정규화])
    검증_변환 = v2.Compose(기본 + [정규화])                                # 증강 없음

    학습 = Subset(ImageFolder(뿌리, transform=학습_변환), 학습_번호)
    검증 = Subset(ImageFolder(뿌리, transform=검증_변환), 검증_번호)

    정답 = torch.tensor(학습.dataset.targets)[학습_번호]                  # 학습용 샘플의 정답들
    가중치 = 1.0 / torch.bincount(정답)[정답].float()
    샘플러 = WeightedRandomSampler(가중치, num_samples=len(학습), replacement=True,
                                  generator=torch.Generator().manual_seed(씨앗))
    print("학습용 클래스별 개수:", torch.bincount(정답).tolist())

    학습_로더 = DataLoader(학습, batch_size=32, sampler=샘플러, num_workers=2)
    검증_로더 = DataLoader(검증, batch_size=64, shuffle=False, num_workers=2)
    return 학습_로더, 검증_로더, 학습.dataset.classes


def main() -> None:
    torch.manual_seed(씨앗)
    도형_폴더_만들기(뿌리, {"circle": 120, "square": 60, "triangle": 20}, 씨앗=1)
    학습_로더, 검증_로더, 클래스들 = 로더_만들기()
    print("클래스:", 클래스들, "| 배치 수:", len(학습_로더), len(검증_로더))

    에폭_개수 = torch.zeros(len(클래스들), dtype=torch.long)
    for 단계, (그림, 정답) in enumerate(학습_로더):
        에폭_개수 += torch.bincount(정답, minlength=len(클래스들))
        if 단계 == 0:
            print("첫 배치:", tuple(그림.shape), 그림.dtype, 정답.dtype)
            print(f"첫 배치 평균 {그림.mean():.3f}, 표준편차 {그림.std():.3f}")
    print("한 에폭 동안 본 클래스별 개수:", 에폭_개수.tolist())

    첫번째 = torch.cat([그림 for 그림, _ in 검증_로더])
    두번째 = torch.cat([그림 for 그림, _ in 검증_로더])
    print("검증 데이터:", tuple(첫번째.shape), "| 두 번 읽어도 같은가:", torch.equal(첫번째, 두번째))


if __name__ == "__main__":
    main()
```

```text
학습용 채널 평균: [0.841, 0.842, 0.845]
학습용 클래스별 개수: [98, 46, 16]
클래스: ['circle', 'square', 'triangle'] | 배치 수: 5 1
첫 배치: (32, 3, 32, 32) torch.float32 torch.int64
첫 배치 평균 0.089, 표준편차 0.959
한 에폭 동안 본 클래스별 개수: [50, 52, 58]
검증 데이터: (40, 3, 32, 32) | 두 번 읽어도 같은가: True
```

단계마다 짚어 보겠습니다.

- **나누기 (`학습_검증_번호`)**: 200장의 번호를 씨앗 42로 섞어 앞 40개를 검증, 나머지 160개를 학습으로 잘랐습니다. 7.8절의 바른 방법 그대로, 이 번호 목록을 transform이 다른 두 `ImageFolder`에 똑같이 써서 `Subset`을 만들었어요.
- **정규화 기준 (`채널_통계`)**: 증강 없이 텐서로만 바꾼 학습용 그림 160장을 `torch.stack`으로 쌓아 `(160, 3, 32, 32)`를 만들고, `dim=(0, 2, 3)`으로 그림·세로·가로 방향을 한꺼번에 접어 채널별 평균을 구했습니다. 4장에서 "`dim`으로 지정한 차원이 사라진다"고 했죠. 색 채널 3개만 남아요. 평균이 0.84 정도로 높은 것은 흰 바탕(1.0)이 그림의 대부분을 차지하기 때문입니다. 검증용 그림은 이 계산에 넣지 않았어요(데이터 누수 방지).
- **변환**: 학습용은 좌우 뒤집기와 무작위 자르기를 거쳐 정규화합니다. 도형은 좌우로 뒤집어도 같은 도형이니 뒤집기를 써도 괜찮아요. 자르기의 테두리는 `fill=255`로 흰색을 채워, 바탕과 똑같이 보이게 했습니다. 검증용은 `기본 + [정규화]`로 증강 없이 같은 정규화만 겁니다.
- **샘플러**: 학습용 160장 중 동그라미 98장, 네모 46장, 세모 16장이었습니다. `학습.dataset.targets`는 `ImageFolder`가 들고 있는 전체 정답 목록이고, 거기서 학습용 번호만 골라 가중치를 만들었어요.
- **한 에폭**: 학습용 로더는 160장을 32장씩 5배치, 검증용은 40장을 한 배치로 냅니다. 첫 배치는 `(32, 3, 32, 32)`의 `float32` 그림과 `int64` 정답으로, 6장에서 만든 것 같은 분류 모델에 바로 넣을 수 있는 모양이에요. 정규화한 값의 평균은 0.089, 표준편차는 0.959로 0과 1에 가깝습니다. 딱 0과 1이 아닌 것은 증강으로 흰 테두리가 섞이고 샘플러가 그림을 고르게 뽑지 않기 때문이에요.
- **클래스 균형**: 한 에폭 동안 동그라미 50, 네모 52, 세모 58장을 봤습니다. 원래 98 : 46 : 16이던 비율이 거의 1 : 1 : 1이 됐어요. 세모 16장이 평균 3번 넘게 반복해서 나왔지만, 증강 덕분에 나올 때마다 조금씩 다른 모습입니다.
- **검증 데이터**: 검증 로더를 두 번 돌려 받은 그림 40장이 완전히 같았습니다(`True`). 증강이 걸리지 않았고 섞지도 않았으니까요. 이래야 에폭마다 잰 검증 점수를 서로 비교할 수 있습니다.

이 파이프라인에 6장의 모델과 학습 루프를 붙이면 바로 학습을 시작할 수 있어요. 데이터 개수와 그림 크기만 바꾸면 실제 이미지 분류 프로젝트에서도 뼈대는 그대로 씁니다. 시간이 있다면 세 가지를 바꿔 보세요. 증강에 `v2.RandomRotation(15)`를 더하면 첫 배치의 평균이 어떻게 바뀌는지, 샘플러를 빼고 `shuffle=True`로 바꾸면 에폭의 클래스 개수가 어떻게 되는지, `num_workers=0`으로 바꾸면 가드 없이도 돌아가는지 직접 확인해 보는 겁니다.

## 7.12 정리와 다음 장 미리보기

이 장에서 데이터가 창고에서 모델까지 흘러가는 길을 만들었습니다.

- **Dataset**: `__len__`과 `__getitem__` 두 메서드의 약속. `__init__`은 목록만 가볍게, 무거운 일은 꺼낼 때. 메모리에 다 들어가면 `TensorDataset`, 번호 없이 흘려보내야 하면 `IterableDataset`
- **직접 만든 Dataset**: CSV는 읽어서 텐서로(표준화 기준은 학습 데이터에서만), 이미지 폴더는 (경로, 정답) 목록만 들고 꺼낼 때 열기. 폴더 구조가 맞으면 `ImageFolder`
- **DataLoader**: `batch_size`, `shuffle`(씨앗은 `generator`로), `drop_last`. 샘플의 생김새를 유지하며 묶는 기본 collate 규칙
- **transforms**: `ToImage` → `ToDtype(scale=True)` → `Normalize`를 `Compose`로. 증강은 꺼낼 때마다 새로 적용되고, 정답이 바뀌지 않는 범위에서 학습용에만
- **collate_fn**: 길이가 다른 샘플은 `pad_sequence`로 채우고 길이·마스크를 함께. 비슷한 길이끼리 묶으면 패딩 낭비가 크게 준다
- **분할과 샘플링**: `random_split`과 씨앗 고정 `Generator`, transform이 다르면 같은 번호로 두 `Subset`. 불균형에는 `WeightedRandomSampler`(같은 샘플 반복에 주의)
- **속도**: `num_workers`는 `__main__` 가드 안에서, `persistent_workers`로 일꾼 살려 두기, 기다린 시간을 재서 병목 찾기. IterableDataset은 일꾼끼리 몫을 직접 나누기

다음 8장에서는 이렇게 준비한 학습용·검증용 데이터를 가지고 **모델을 잘 학습시키는 법**을 다룹니다. 학습 손실은 계속 줄어드는데 검증 손실이 다시 올라가는 순간, 즉 과적합을 학습 곡선에서 알아보는 것부터 시작해요. 이 장에서 맛만 본 데이터 증강이 실제로 과적합을 얼마나 줄이는지도, 드롭아웃과 가중치 감쇠 같은 다른 처방과 함께 숫자로 비교해 보겠습니다.
