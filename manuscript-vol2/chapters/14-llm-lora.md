# Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA

> **학습 목표**  
> - 사전학습된 작은 언어 모델을 내려받아 불러오고, 크기와 구조를 숫자로 읽기
> - 언어 모델이 하는 일이 "다음 토큰 맞히기" 하나뿐이라는 것을 직접 생성 루프를 짜서 확인하기
> - 탐욕·샘플링·온도·top-k·top-p가 다음 토큰 고르기를 어떻게 바꾸는지 설명하기
> - 채팅 템플릿과 시스템 프롬프트, 예시(few-shot), 대화 기록을 다루기
> - 모델 크기·자료형·KV 캐시로 메모리를 계산하고, 양자화를 직접 흉내 내 보기
> - LoRA를 손으로 구현한 뒤 peft로 작은 LLM에 붙여 미세조정하고, 무엇을 배우고 무엇을 못 배우는지 측정하기

---

## 들어가며: 휴대폰 자판은 어떻게 다음 단어를 알까요?

휴대폰으로 "오늘 저녁에"까지 치면 자판 위에 "뭐", "같이", "시간" 같은 단어가 떠오릅니다. 자판은 내 마음을 읽은 게 아니라, 수많은 문장에서 "오늘 저녁에" 다음에 자주 나온 말을 기억해 두었다가 보여 줄 뿐이에요. 그중 하나를 누르면 다시 그다음 단어를 추천하죠.

요즘 화제인 **대규모 언어 모델(LLM, Large Language Model)** 도 놀랍게도 같은 놀이를 합니다. 다른 점은 규모예요. 휴대폰 자판이 단어 몇 개의 짝을 기억한다면, LLM은 인터넷 문서와 책 수조 토큰을 읽으며 수억에서 수천억 개의 숫자에 "이 글 다음에는 무엇이 올까"를 새겨 둡니다. 그 놀이를 아주 잘하게 되면 질문에 답하고, 요약하고, 코드를 짜는 것처럼 보이게 돼요.

12장에서는 트랜스포머를 직접 만들고 작은 문자 단위 GPT를 처음부터 학습시켰습니다. 노트북에서 몇 분 학습한 모델이니 문장이 그럴듯해지는 정도에서 멈췄죠. 이 장에서는 방향을 바꿔, 남이 큰 컴퓨터로 오래 학습해 공개한 **사전학습 모델**을 내려받아 씁니다. 순서는 이렇습니다.

1. 모델을 불러와 크기를 재고, 다음 토큰을 어떻게 고르는지 직접 들여다봅니다.
2. 프롬프트와 채팅 템플릿으로 모델에게 일을 시키고, 작은 모델의 한계를 정직하게 확인합니다.
3. 모델이 메모리를 얼마나 먹는지 계산하고, 줄이는 방법(양자화)을 맛봅니다.
4. 모델 전체가 아니라 아주 작은 부분만 학습하는 **LoRA**를 손으로 만든 뒤, 그 방법으로 모델을 우리 데이터에 맞게 고쳐 봅니다.

이 장에서 쓰는 모델은 알리바바 Qwen 팀이 공개한 **Qwen2.5-0.5B-Instruct**입니다. 라이선스는 Apache-2.0이고(모델 카드: huggingface.co/Qwen/Qwen2.5-0.5B-Instruct), 로그인이나 동의 절차 없이 받을 수 있어요. 이름의 0.5B는 파라미터가 약 5억(0.5 billion) 개라는 뜻이고, Instruct는 질문에 답하도록 추가 학습한 판이라는 뜻입니다. 노트북에서 돌릴 수 있는 가장 작은 축에 드는 LLM이에요.

> **Q. 무엇을 설치해야 하나요?**
> 4장의 PyTorch에 더해 `uv add transformers peft`를 실행하세요. `transformers`는 사전학습 모델을 불러오고 쓰는 Hugging Face의 라이브러리(13장에서 처음 썼습니다), `peft`는 LoRA 같은 "적은 파라미터만 학습하는" 방법을 모아 둔 라이브러리예요. `peft`를 설치하면 함께 쓰는 `accelerate`도 따라 설치됩니다. 이 장의 예제는 파이썬 3.12, PyTorch 2.14.1, transformers 5.20.2, peft 0.21.2, accelerate 1.15.0에서 실행해 확인했습니다. 모델 파일은 처음 실행할 때 약 1GB를 내려받아 사용자 폴더의 캐시(`~/.cache/huggingface`)에 저장하고, 그다음부터는 다시 받지 않아요.

## 14.1 사전학습 언어 모델 불러오기

### 이름 하나로 모델과 토크나이저 받기

Hugging Face 허브에는 모델이 "만든 곳/모델 이름" 형식의 이름으로 올라 있습니다. `transformers`는 이 이름만 주면 설정 파일과 가중치를 내려받아 알맞은 PyTorch 모델을 만들어 줘요. 언어 모델은 글을 왼쪽에서 오른쪽으로 이어 쓰는 모델이라 `AutoModelForCausalLM`("앞만 보고 다음을 맞히는 언어 모델")으로 불러옵니다.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"                 # Hugging Face에 올라 있는 모델 이름
토크나이저 = AutoTokenizer.from_pretrained(이름)     # 글자 ↔ 번호 변환기
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32)

print(type(모델).__name__)
print(f"파라미터: {sum(p.numel() for p in 모델.parameters()):,}개")
설정 = 모델.config
print("층 수:", 설정.num_hidden_layers, "/ 은닉 크기:", 설정.hidden_size,
      "/ 어텐션 헤드:", 설정.num_attention_heads)
print("어휘 크기:", 설정.vocab_size, "/ 한 번에 읽는 최대 길이:", 설정.max_position_embeddings)
print(isinstance(모델, torch.nn.Module))           # 6장의 nn.Module 그대로
```

```text
Qwen2ForCausalLM
파라미터: 494,032,768개
층 수: 24 / 은닉 크기: 896 / 어텐션 헤드: 14
어휘 크기: 151936 / 한 번에 읽는 최대 길이: 32768
True
```

파라미터가 494,032,768개, 약 4억 9천만 개입니다. 6장 6.11절의 FashionMNIST 분류기가 235,146개였으니 2천 배쯤 큰 모델이에요. 설정(`config`)을 읽어 보면 구조가 보입니다. 트랜스포머 블록 24개를 쌓았고, 토큰 하나를 숫자 896개로 표현하며, 어텐션 헤드는 14개예요. 블록, 은닉 크기, 헤드는 모두 12장에서 직접 만든 부품의 이름 그대로입니다. 크기만 다를 뿐 같은 설계도라는 뜻이죠.

**어휘 크기** 151,936은 이 모델이 아는 토큰의 종류 수입니다. 마지막 층이 토큰마다 점수를 하나씩 내니, 다음 토큰을 고를 때마다 15만 개가 넘는 후보 중에서 하나를 고르는 셈이에요. 최대 길이 32,768은 한 번에 읽을 수 있는 토큰 수의 한계입니다. 마지막 줄의 `True`는 이 거대한 모델도 결국 6장에서 배운 `nn.Module`이라는 확인이에요. `parameters()`, `eval()`, `.to(장치)`, `state_dict()`가 모두 그대로 통합니다.

### 글자를 번호로: 토크나이저

모델은 글자를 직접 읽지 못하고 번호만 받습니다. 글을 조각(토큰)으로 자르고 번호를 붙이는 일은 모델과 짝을 이루는 **토크나이저**가 해요. 자르는 방법은 13장에서 자세히 다뤘으니 여기서는 이 모델이 한국어를 어떻게 자르는지만 확인하겠습니다.

```python
from transformers import AutoTokenizer

토크나이저 = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")

문장 = "파이썬은 재미있다"
번호 = 토크나이저.encode(문장)
print(번호)
print([토크나이저.decode([n]) for n in 번호])      # 번호 하나하나가 어떤 조각인지
print(토크나이저.decode(번호))                     # 번호를 다시 글자로

# 같은 뜻의 문장, 토큰은 몇 개일까?
for 글 in ["오늘 날씨가 정말 좋네요.", "The weather is really nice today."]:
    print(f"{len(글):2}글자 → {len(토크나이저.encode(글)):2}토큰: {글}")
```

```text
[126793, 12802, 144773, 33704, 129242, 56039, 13165, 19946]
['파', '이', '썬', '은', ' 재', '미', '�', '�다']
파이썬은 재미있다
14글자 → 10토큰: 오늘 날씨가 정말 좋네요.
33글자 →  7토큰: The weather is really nice today.
```

"파이썬은 재미있다"가 번호 8개가 됐습니다. 조각을 하나씩 글자로 되돌려 보면 "파", "이", "썬"처럼 거의 한 글자씩 잘렸고, "있"은 깨진 조각(`�`) 두 개에 나뉘어 들어갔는데 둘째 조각은 "다"와 한 토큰이 됐어요. 이 토크나이저는 글자를 컴퓨터 내부 표현인 **바이트**까지 쪼갤 수 있게 만들어져서, 어휘에 통째로 들어 있지 않은 글자는 바이트 단위 조각으로 나눕니다. 조각 하나만 글자로 바꾸면 깨져 보이지만, 번호를 모두 이어서 되돌리면 원래 문장이 그대로 나와요.

아래 두 줄은 같은 뜻의 문장입니다. 한국어는 14글자에 토큰 10개, 영어는 33글자에 토큰 7개가 들었어요. 영어는 단어 하나가 토큰 하나인 경우가 많지만, 한국어는 한두 글자마다 토큰이 하나씩 필요합니다. 모델이 학습할 때 영어 글을 훨씬 많이 봐서 영어 조각을 크게 만들어 두었기 때문이에요. 같은 내용을 말하는 데 토큰이 더 필요하다는 건, 한국어가 같은 길이 한도 안에 덜 들어가고 생성도 더 오래 걸린다는 뜻입니다. 14.5절에서 이 이야기를 다시 합니다.

## 14.2 다음 토큰 예측: LLM이 하는 일은 하나뿐

### 모델이 내는 것은 점수표

번호를 모델에 넣으면 무엇이 나올까요? 6장의 분류 모델이 클래스마다 점수(로짓)를 냈던 것처럼, 언어 모델은 **어휘에 있는 토큰마다** 점수를 냅니다.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()

입력 = 토크나이저("대한민국의 수도는", return_tensors="pt")
print("입력 번호:", 입력["input_ids"])
with torch.no_grad():
    로짓 = 모델(**입력).logits                       # (배치, 토큰 수, 어휘 크기)
print("로짓 모양:", tuple(로짓.shape))

마지막 = 로짓[0, -1]                                # 마지막 자리의 점수 = 다음 토큰 후보
확률 = torch.softmax(마지막, dim=-1)
상위 = 확률.topk(5)
for p, n in zip(상위.values, 상위.indices):
    print(f"{p.item():.3f}  {토크나이저.decode([n.item()])!r}")
```

```text
입력 번호: tensor([[ 66845,  23573, 125496, 124785,  20401, 134013,  16560]])
로짓 모양: (1, 7, 151936)
0.110  '?\n'
0.089  ' 어디'
0.077  ' 무엇'
0.057  ' __'
0.052  ' 서울'
```

"대한민국의 수도는"이 토큰 7개로 들어갔고, 로짓 모양은 `(1, 7, 151936)`입니다. 4장 4.2절에서 권한 대로 자리마다 이름을 붙여 읽으면 "문장 1개, 토큰 7자리, 자리마다 어휘 151,936개의 점수"예요. 언어 모델은 **모든 자리에서 동시에** "이 자리 다음에 올 토큰"의 점수를 냅니다. 학습할 때는 7자리 모두의 예측을 정답과 비교해 한꺼번에 배우고, 생성할 때는 마지막 자리의 점수만 쓰면 돼요. 12장에서 어텐션 마스크로 뒤쪽을 가렸던 이유가 바로 이것입니다.

마지막 자리의 점수를 6장 6.2절의 소프트맥스로 확률로 바꾸고 4장 4.6절의 `topk`로 상위 다섯 개를 뽑았습니다. 1등은 `'?\n'`(물음표와 줄바꿈)이고, ' 어디', ' 무엇'이 뒤를 잇고, ' 서울'은 5등으로 5.2%입니다. 의외죠? 모델은 "대한민국의 수도는"을 **질문의 앞부분**으로 읽은 거예요. 인터넷에는 "대한민국의 수도는?"으로 끝나는 퀴즈 문장이 많으니까요. 모델은 사실을 묻는 게 아니라 "이런 글 다음에는 보통 무엇이 오는가"를 답합니다. 이 차이를 기억해 두면 이 장 후반의 이상한 대답들이 이해가 됩니다.

### 생성 루프를 직접 짜 보기

그럼 문장은 어떻게 길게 만들까요? 다음 토큰 하나를 고르고, 그것을 입력 뒤에 붙여서 다시 모델에 넣고, 또 하나를 고르기를 되풀이하면 됩니다. 휴대폰 자판에서 추천 단어를 계속 누르는 것과 똑같아요.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()

번호 = 토크나이저("대한민국의 수도는", return_tensors="pt")["input_ids"]
시작_길이 = 번호.shape[1]

# 직접 만든 생성 루프: 가장 점수가 높은 토큰을 골라 뒤에 붙이고 다시 넣기
with torch.no_grad():
    for _ in range(15):
        다음 = 모델(번호).logits[0, -1].argmax()        # 탐욕(greedy): 1등만 고른다
        번호 = torch.cat([번호, 다음.view(1, 1)], dim=1)
직접 = 토크나이저.decode(번호[0, 시작_길이:])
print(repr(직접))

# 같은 일을 generate 한 줄로 (반복 억제 기본값 1.1을 꺼서 직접 만든 루프와 똑같은 규칙으로)
입력 = 토크나이저("대한민국의 수도는", return_tensors="pt")
with torch.no_grad():
    결과 = 모델.generate(**입력, max_new_tokens=15, do_sample=False, repetition_penalty=1.0)
자동 = 토크나이저.decode(결과[0, 시작_길이:])
print(repr(자동))
print("같은가:", 직접 == 자동)
```

```text
'?\nA. 서울\nB. 인천\nC. 대구\n'
'?\nA. 서울\nB. 인천\nC. 대구\n'
같은가: True
```

15번 반복하면서 매번 1등 토큰(`argmax`)을 골라 4장의 `torch.cat`으로 이어 붙였습니다. 매번 가장 점수가 높은 것만 고르는 방법을 **탐욕(greedy) 디코딩**이라고 불러요. 결과를 보면 앞에서 확인한 1등 `'?\n'`을 고른 뒤, 정말로 객관식 퀴즈를 만들어 냈습니다. "A. 서울"이 정답 자리에 있긴 하네요.

아래의 `generate` 한 줄은 같은 일을 하는 지름길이고, 결과가 글자 하나까지 같습니다. `repetition_penalty=1.0`은 14.3절에서 볼 이 모델의 기본값 하나(반복 억제)를 꺼서, 직접 짠 루프와 규칙을 똑같이 맞춘 거예요. 다만 `generate`는 훨씬 효율적으로 돌아요. 직접 짠 루프는 토큰을 하나 붙일 때마다 문장 전체를 처음부터 다시 계산하지만, `generate`는 앞 토큰들의 어텐션 계산 결과(키와 값)를 저장해 두었다가 새 토큰 하나만 계산합니다. 이 저장소를 **KV 캐시**라고 하는데, 14.6절에서 이것이 메모리를 얼마나 쓰는지 계산해 봐요.

## 14.3 디코딩: 다음 토큰을 고르는 방법

### 온도: 확률 분포를 날카롭게, 또는 평평하게

탐욕 디코딩은 언제나 같은 답을 냅니다. 사실을 물을 때는 좋지만, 이야기나 아이디어처럼 다양한 답이 필요할 때는 지루하죠. 그래서 확률대로 **뽑는(sampling)** 방법을 쓰는데, 이때 가장 먼저 만지는 손잡이가 **온도(temperature)** 입니다. 소프트맥스를 하기 전에 점수를 온도로 나누는 단순한 계산이에요.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()

입력 = 토크나이저("점심 메뉴로 추천하는 음식은", return_tensors="pt")
with torch.no_grad():
    로짓 = 모델(**입력).logits[0, -1]

후보 = 로짓.topk(5).indices                           # 원래 점수 기준 상위 5개 후보
print("후보:", [토크나이저.decode([n]) for n in 후보.tolist()])
for 온도 in [0.5, 1.0, 2.0]:
    확률 = torch.softmax(로짓 / 온도, dim=-1)        # 점수를 온도로 나눈 뒤 확률로
    print(f"온도 {온도}: 상위 5개 {[round(p, 3) for p in 확률[후보].tolist()]}"
          f"  나머지 합 {1 - 확률[후보].sum().item():.3f}")
```

```text
후보: [' 무엇', '?', ' 다음과', " '", ' 어떤']
온도 0.5: 상위 5개 [0.967, 0.016, 0.004, 0.002, 0.001]  나머지 합 0.010
온도 1.0: 상위 5개 [0.414, 0.054, 0.027, 0.016, 0.016]  나머지 합 0.473
온도 2.0: 상위 5개 [0.014, 0.005, 0.004, 0.003, 0.003]  나머지 합 0.971
```

"점심 메뉴로 추천하는 음식은" 다음 토큰의 상위 다섯 후보입니다. 온도 1.0이 모델이 원래 낸 확률이에요. 1등 ' 무엇'이 41.4%이고, 상위 다섯 개 밖의 나머지 15만여 개가 모두 합쳐 47.3%를 나눠 갖습니다.

- **온도를 낮추면(0.5)** 점수 차이가 두 배로 벌어져서 1등이 96.7%를 가져갑니다. 거의 탐욕 디코딩처럼 늘 같은 답을 내게 돼요. 온도를 0에 가깝게 하면 탐욕과 같아집니다.
- **온도를 높이면(2.0)** 점수 차이가 반으로 줄어 분포가 평평해집니다. 1등도 1.4%뿐이고, 나머지가 97.1%예요. 15만 개 중 아무거나 뽑힐 수 있다는 뜻이라, 엉뚱한 토큰이 자주 섞입니다.

온도는 이렇게 "모델이 자신 있는 쪽을 얼마나 믿을지"를 정하는 손잡이입니다.

### top-k와 top-p: 엉뚱한 후보는 아예 빼기

온도가 1이어도 문제가 남습니다. 확률이 아주 낮은 후보 수만 개를 모두 합치면 큰 확률이 되기 때문이에요. 앞에서 "나머지 합"이 47.3%였죠. 뽑을 때마다 그중 엉뚱한 것이 걸릴 수 있습니다. 그래서 뽑기 전에 후보를 추리는 두 가지 방법을 함께 씁니다. 원리를 보기 쉽게 후보 여섯 개짜리 예제로 직접 구현해 보겠습니다.

```python
import torch

# 다음 토큰 후보 6개의 확률 (예제용 숫자)
후보 = ["김밥", "라면", "비빔밥", "떡볶이", "냉면", "우주선"]
확률 = torch.tensor([0.50, 0.20, 0.12, 0.08, 0.06, 0.04])


def top_k_거르기(확률: torch.Tensor, k: int) -> torch.Tensor:
    """확률이 높은 k개만 남기고 다시 합이 1이 되게 맞춘다."""
    남길 = torch.zeros_like(확률)
    값, 번호 = 확률.topk(k)
    남길[번호] = 값
    return 남길 / 남길.sum()


def top_p_거르기(확률: torch.Tensor, p: float) -> torch.Tensor:
    """높은 순서로 더해 가다 누적 확률이 p에 닿을 때까지만 남긴다."""
    정렬값, 정렬번호 = 확률.sort(descending=True)
    누적 = 정렬값.cumsum(dim=0)
    버릴 = (누적 - 정렬값) >= p                       # 앞까지의 합이 이미 p 이상이면 버린다
    정렬값[버릴] = 0.0
    남길 = torch.zeros_like(확률).scatter(0, 정렬번호, 정렬값)
    return 남길 / 남길.sum()


print("top-k=3 :", [round(v, 3) for v in top_k_거르기(확률, 3).tolist()])
print("top-p=0.85:", [round(v, 3) for v in top_p_거르기(확률, 0.85).tolist()])

생성기 = torch.Generator().manual_seed(0)
for 이름, 분포 in [("그대로", 확률), ("top-p=0.85", top_p_거르기(확률, 0.85))]:
    뽑기 = torch.multinomial(분포, 1000, replacement=True, generator=생성기)
    횟수 = torch.bincount(뽑기, minlength=6)
    print(f"{이름:10} 1000번 뽑기:", dict(zip(후보, 횟수.tolist())))
```

```text
top-k=3 : [0.61, 0.244, 0.146, 0.0, 0.0, 0.0]
top-p=0.85: [0.556, 0.222, 0.133, 0.089, 0.0, 0.0]
그대로        1000번 뽑기: {'김밥': 500, '라면': 206, '비빔밥': 125, '떡볶이': 59, '냉면': 55, '우주선': 55}
top-p=0.85 1000번 뽑기: {'김밥': 566, '라면': 228, '비빔밥': 117, '떡볶이': 89, '냉면': 0, '우주선': 0}
```

- **top-k**는 "확률이 높은 k개만 남긴다"입니다. k=3이면 김밥·라면·비빔밥만 남고, 셋의 합이 1이 되게 다시 나눠서 김밥이 0.61이 됐어요.
- **top-p**(nucleus sampling이라고도 해요)는 "높은 순서로 더해서 누적 확률이 p에 닿을 때까지만 남긴다"입니다. 0.50, 0.70, 0.82까지는 아직 0.85에 못 미치니 떡볶이까지 넷이 남고, 냉면부터는 앞까지의 합이 이미 0.90이라 버려졌어요. 코드에서는 4장의 `sort`로 정렬하고, `cumsum`(누적 합)으로 더해 가고, `scatter`로 원래 자리에 되돌려 놓았습니다.

두 방법의 차이는 "몇 개 남길지"를 고정하느냐, 분포 모양에 맡기느냐입니다. 모델이 확신할 때(1등이 0.9쯤)는 top-p가 한두 개만 남기고, 헷갈릴 때는 여러 개를 남겨요. 그래서 실무에서는 top-p를 더 많이 씁니다.

마지막 두 줄은 `torch.multinomial`로 1000번 뽑아 센 결과입니다. 그대로 뽑으면 확률 4%짜리 "우주선"도 55번 나와요. 점심 메뉴를 묻는데 1000번 중 55번은 우주선이라고 답하는 셈이죠. top-p로 거르면 우주선과 냉면은 한 번도 나오지 않습니다. 4장의 `torch.Generator`로 뽑기 순서를 고정해서 몇 번을 실행해도 같은 숫자가 나와요.

### generate로 비교하기

실제 모델에서 세 가지 방법을 나란히 돌려 보겠습니다. 방법마다 씨앗을 두 번 바꿔 봐요.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()
입력 = 토크나이저("비 오는 날 창밖을 보며", return_tensors="pt")
길이 = 입력["input_ids"].shape[1]

# 모델의 기본값(top_k=20, top_p=0.8, 반복 억제 1.1)이 끼어들지 않게 손잡이를 모두 직접 적는다
끄기 = dict(top_k=0, top_p=1.0, repetition_penalty=1.0)
설정들 = {
    "탐욕": dict(do_sample=False, repetition_penalty=1.0),
    "온도 0.7, top-p 0.9": dict(끄기, do_sample=True, temperature=0.7, top_p=0.9),
    "온도 1.5": dict(끄기, do_sample=True, temperature=1.5),
}
for 설명, 옵션 in 설정들.items():
    for 씨앗 in [1, 2]:
        torch.manual_seed(씨앗)
        결과 = 모델.generate(**입력, max_new_tokens=25, **옵션)
        글 = 토크나이저.decode(결과[0, 길이:], skip_special_tokens=True)
        print(f"[{설명} / 씨앗 {씨앗}] {글!r}")
```

```text
[탐욕 / 씨앗 1] ', 그는 놀라운 일들을 보았습니다. 그는 놀라운 일들을 보았'
[탐욕 / 씨앗 2] ', 그는 놀라운 일들을 보았습니다. 그는 놀라운 일들을 보았'
[온도 0.7, top-p 0.9 / 씨앗 1] ', 이어질 수 없는 우주의 진화와 재생의 문화가 있습니다. 2012년'
[온도 0.7, top-p 0.9 / 씨앗 2] ' "오늘 밤은 달빛이 매력적이고, 움직이는 생명체들의 수요를'
[온도 1.5 / 씨앗 1] ' 목야()})\n{\\hangfmt}`,ห้องที่ 관});\n\n\n.perform_pipe("DMETHOD皋 design score efficiently prioritize detail activity cap'
[온도 1.5 / 씨앗 2] ' 통해弨 tắt reacts bc 달 에Congress 리 Toni compens foreverمنح Tedﺍ Failed doğ의 buz Accessed быстро כל fullWidth'
```

- **탐욕**은 씨앗과 상관없이 두 번 모두 같은 문장입니다. 뽑기를 하지 않으니 씨앗이 할 일이 없죠. 게다가 "그는 놀라운 일들을 보았습니다"를 벌써 되풀이하기 시작했어요. 매번 1등만 고르면 한번 들어선 흐름에서 빠져나오지 못하는데, 작은 모델의 탐욕 디코딩에서 흔히 보이는 모습입니다.
- **온도 0.7, top-p 0.9**는 씨앗마다 다른 문장이 나오면서도 한국어 문장의 꼴은 유지합니다. 이야기나 대화에 흔히 쓰는 설정이에요.
- **온도 1.5**(`top_k=0`, `top_p=1.0`으로 후보 거르기를 모두 끈 상태)는 처음 한두 토큰 뒤로 코드 조각과 태국어, 베트남어, 아랍어, 러시아어, 중국어, 영어가 뒤섞인 글자 더미가 됐습니다. 평평해진 분포에서 엉뚱한 토큰이 한 번 뽑히면, 모델은 그 엉뚱한 글을 이어 쓰려고 또 엉뚱한 토큰을 고르게 돼요. 한 번 미끄러지면 계속 미끄러지는 겁니다.

`generate`는 `do_sample=False`이면 탐욕, `True`이면 샘플링이고, `temperature`, `top_k`, `top_p`로 손잡이를 정합니다. 무엇을 정하지 않으면 모델과 함께 배포된 기본값(`generation_config.json`)을 따르는데, 이 모델의 기본값은 `do_sample=True, temperature=0.7, top_k=20, top_p=0.8`에, 이미 나온 토큰의 점수를 깎아 같은 말을 덜 되풀이하게 하는 **반복 억제** `repetition_penalty=1.1`까지 켜져 있어요(`print(모델.generation_config)`로 확인할 수 있습니다). 그래서 이 예제는 쓰지 않을 손잡이까지 `끄기`로 모두 직접 적었습니다. 결과를 비교할 때는 이렇게 직접 적어 주는 것이 안전해요. 다만 위의 탐욕처럼 작은 모델은 반복 억제 없이 쓰면 같은 말을 되풀이하기 쉬워서, 14.4절부터 모델에게 답을 받을 때는 탐욕 디코딩에 기본값의 반복 억제(1.1)를 켜 두고 씁니다.

> **Q. 씨앗을 고정했는데 다른 컴퓨터에서는 다른 문장이 나와요. 왜 그런가요?**
> 샘플링은 확률 계산의 아주 작은 차이에도 다른 토큰을 뽑을 수 있습니다. CPU, CUDA, Apple MPS는 같은 계산도 더하는 순서나 내부 정밀도가 조금씩 달라서, 소수점 아래 끝자리가 달라지면 거기서부터 다른 문장으로 갈라져요. MPS에서는 같은 컴퓨터에서도 실행마다 달라질 수 있습니다. 그래서 이 장의 예제는 모두 CPU에서 실행했고, 본문의 출력은 이 책의 실행 환경(Apple M4 Max의 CPU)에서 나온 결과입니다. 여러분의 결과가 글자 하나까지 같지 않아도 이상한 게 아니에요. 4장의 `장치_고르기()`로 GPU에 올려도 코드는 그대로 돌아가지만, 그때 나오는 문장은 이 책과 다를 수 있다는 점만 기억해 두세요.

## 14.4 프롬프트와 채팅 템플릿

### 대화는 사실 하나의 긴 글입니다

지금까지는 "대한민국의 수도는"처럼 글의 앞부분을 주고 이어 쓰게 했습니다. 그런데 우리가 쓰는 챗봇은 질문을 하면 대답을 하죠. Instruct 모델은 어떻게 "이건 질문이니 대답해야 한다"를 알까요? 비밀은 **채팅 템플릿**에 있습니다. 대화를 정해진 표시가 붙은 하나의 글로 바꿔서 넣는 거예요.

```python
from transformers import AutoTokenizer

토크나이저 = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")

대화 = [
    {"role": "system", "content": "너는 친절한 파이썬 선생님이야."},
    {"role": "user", "content": "리스트가 뭐예요?"},
]
글 = 토크나이저.apply_chat_template(대화, tokenize=False, add_generation_prompt=True)
print(글)
print("특수 토큰:", 토크나이저.convert_ids_to_tokens(토크나이저.encode("<|im_start|><|im_end|>")))
```

```text
<|im_start|>system
너는 친절한 파이썬 선생님이야.<|im_end|>
<|im_start|>user
리스트가 뭐예요?<|im_end|>
<|im_start|>assistant

특수 토큰: ['<|im_start|>', '<|im_end|>']
```

대화는 1권 7장의 딕셔너리를 1권 6장의 리스트에 담은 형태입니다. 메시지마다 `role`(누가 말했나)과 `content`(무슨 말인가)가 있고, 역할은 셋이에요.

- **system**: 모델이 지켜야 할 태도나 규칙. 대화 전체에 걸리는 지시입니다.
- **user**: 사용자가 한 말.
- **assistant**: 모델이 한 말.

`apply_chat_template`은 이 리스트를 모델이 학습 때 본 형식의 글로 바꿉니다. `<|im_start|>`와 `<|im_end|>`는 메시지의 시작과 끝을 알리는 **특수 토큰**이에요. 마지막 줄의 `<|im_start|>assistant`는 `add_generation_prompt=True`가 붙여 준 것으로, "이제 모델이 말할 차례"라는 표시입니다. 모델은 여전히 다음 토큰을 이어 쓸 뿐인데, 이 표시 뒤에는 대답이 오고 대답이 끝나면 `<|im_end|>`가 온다는 것을 추가 학습에서 배웠어요. 그래서 질문에 대답하는 것처럼 보입니다.

템플릿은 모델마다 다릅니다. 다른 모델의 템플릿으로 글을 만들어 넣으면 모델이 엉뚱하게 반응해요. 그래서 문자열을 손으로 조립하지 말고 언제나 그 모델 토크나이저의 `apply_chat_template`을 쓰세요.

### 시스템 프롬프트로 태도 정하기

같은 질문에 시스템 지시만 바꿔 보겠습니다. 답만 꺼내 주는 작은 함수 `묻기`를 만들어 이 절 내내 씁니다.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()


def 묻기(대화: list[dict], 최대: int = 50) -> str:
    """대화 기록을 채팅 템플릿에 맞춰 넣고 모델의 답만 돌려준다."""
    입력 = 토크나이저.apply_chat_template(대화, add_generation_prompt=True,
                                         return_tensors="pt", return_dict=True)
    with torch.no_grad():
        결과 = 모델.generate(**입력, max_new_tokens=최대, do_sample=False,
                             repetition_penalty=1.1)      # 모델 기본값의 반복 억제는 켜 둔다
    return 토크나이저.decode(결과[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True)


질문 = {"role": "user", "content": "고양이에 대해 알려 줘."}
for 시스템 in ["답은 반드시 한 문장으로 해.",
             "모든 답을 JSON으로 해. 키는 '요약' 하나뿐이야.",
             "모든 답을 영어로만 해.",
             "너는 해적이야. 해적 말투로 답해."]:
    print(f"[{시스템}] {묻기([{'role': 'system', 'content': 시스템}, 질문])!r}")
```

```text
[답은 반드시 한 문장으로 해.] '고양이는 사람의 식사와 휴식을 즐기며, 농담과 이야기를 나누는 동물입니다.'
[모든 답을 JSON으로 해. 키는 '요약' 하나뿐이야.] '{\n  "요약": "고양이는 고유한 특징과 장점을 가지고 있으며, 특히 농사와 식물栽培에 유명합니다. 고양이는 다양한 종류의 식물과 동물로'
[모든 답을 영어로만 해.] '고양이는 매우 유명한 동물입니다. 그들은 다양한 종류가 있으며, 특히 고유의 특징과 행동은 다음과 같습니다:\n\n1. 고양이는 빨간색 또는 검은색으로 주요 색'
[너는 해적이야. 해적 말투로 답해.] '고양이는 매우 건강하고 유쾌한 동물입니다. 고양이는 편안하게 웃으며, 다양한 활동을 즐길 수 있습니다. 고양이는 높은 체중과 강력한'
```

`return_dict=True`를 주면 번호(`input_ids`)와 마스크(`attention_mask`)가 딕셔너리로 나오고, `**입력`으로 풀어 `generate`에 넘깁니다. 결과에는 질문까지 포함되어 있으니 질문 길이만큼 잘라 내고 대답만 글자로 바꿨어요.

결과는 반반입니다. "한 문장으로"는 지켰고, "JSON으로"도 `{"요약": ...` 꼴로 시작했어요(50토큰에서 잘라서 닫는 괄호는 보이지 않고, 내용이 이상하고 중간에 한자가 섞인 건 다음 절에서 이야기합니다). 그런데 "영어로만"과 "해적 말투로"는 무시했습니다. 작은 모델은 학습 때 자주 본 종류의 지시(길이, 형식)는 잘 따르지만, 질문 언어를 바꾸거나 역할극을 하라는 지시처럼 자기 습관과 부딪히는 지시는 놓치기 쉽습니다. 시스템 프롬프트는 부탁이지 명령이 아니에요. 큰 모델일수록 잘 따르지만, 어떤 모델이든 **결과를 확인하는 코드**를 따로 두는 습관이 필요합니다.

### 예시를 보여 주기: few-shot

말로 설명하는 대신 예시를 보여 주면 어떨까요? 상품 후기를 "긍정"과 "부정"으로 나누는 일을 시켜 보겠습니다. 예시는 **이미 주고받은 대화처럼** 넣는 것이 요령이에요.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()


def 묻기(대화: list[dict], 최대: int) -> str:
    """대화 기록을 채팅 템플릿에 맞춰 넣고 모델의 답만 돌려준다."""
    입력 = 토크나이저.apply_chat_template(대화, add_generation_prompt=True,
                                         return_tensors="pt", return_dict=True)
    with torch.no_grad():
        결과 = 모델.generate(**입력, max_new_tokens=최대, do_sample=False,
                             repetition_penalty=1.1)      # 모델 기본값의 반복 억제는 켜 둔다
    return 토크나이저.decode(결과[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True)


# 예시 두 개를 "이미 주고받은 대화"처럼 넣어 둔다 (예제용 후기)
예시 = [
    {"role": "system", "content": "상품 후기를 읽고 '긍정' 또는 '부정' 한 단어로만 답해."},
    {"role": "user", "content": "배송이 빠르고 품질도 좋아요."},
    {"role": "assistant", "content": "긍정"},
    {"role": "user", "content": "한 번 빨았더니 색이 다 빠졌어요."},
    {"role": "assistant", "content": "부정"},
]
후기들 = ["가격 대비 정말 만족합니다.", "사이즈가 너무 작아서 반품했어요.",
        "포장은 꼼꼼했는데 맛이 별로네요.", "생각보다 튼튼하고 예뻐요."]
for 후기 in 후기들:
    예시없이 = 묻기([{"role": "user", "content": f"다음 후기는 긍정이야 부정이야? {후기}"}], 20)
    예시있게 = 묻기(예시 + [{"role": "user", "content": 후기}], 5)
    print(f"{후기}\n  예시 없이: {예시없이!r}\n  예시 두 개: {예시있게!r}")
```

```text
가격 대비 정말 만족합니다.
  예시 없이: '물론입니다! "가격 대비 정말 만족합니다."는 긍정적인 표현'
  예시 두 개: '긍정'
사이즈가 너무 작아서 반품했어요.
  예시 없이: '죄송합니다, 저는 인공지능으로서 사이트를 운영하고 있습니다. 하지만 개인'
  예시 두 개: '부정'
포장은 꼼꼼했는데 맛이 별로네요.
  예시 없이: '물론입니다! "다음 후기는 긍정이야 부정이야?"와'
  예시 두 개: '긍정'
생각보다 튼튼하고 예뻐요.
  예시 없이: '물론입니다! "다음 후기는 긍정이야"라는 문장은 "'
  예시 두 개: '긍정'
```

예시 없이 물으면 "물론입니다!"로 시작하는 긴 설명을 늘어놓거나, 아예 엉뚱한 답을 합니다. 답을 고르는 대신 대화를 하려 드는 거죠. 예시 두 개를 보여 주자 네 번 모두 딱 한 단어로 답했고, 그중 셋을 맞혔어요. 이렇게 예시 몇 개를 프롬프트에 넣는 방법을 **few-shot 프롬프팅**이라고 부릅니다(예시가 없으면 zero-shot). 모델의 가중치는 하나도 바뀌지 않았는데 행동이 바뀌었다는 점이 중요해요. 모델은 프롬프트 속 예시의 **형식**을 그대로 이어 쓰려고 합니다.

틀린 하나는 "포장은 꼼꼼했는데 맛이 별로네요"입니다. 앞은 칭찬, 뒤는 불만이라 "~는데" 뒤를 읽어야 하는 문장이에요. 작은 모델은 이런 문장에서 쉽게 틀립니다. 이런 분류를 제대로 하려면 13장처럼 분류 모델을 데이터로 미세조정하는 편이 훨씬 정확해요.

### 모델은 대화를 기억하지 않습니다

챗봇이 앞에서 한 말을 기억하는 것처럼 보이는 건 어떻게 된 걸까요?

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()


def 묻기(대화: list[dict], 최대: int = 40) -> str:
    """대화 기록을 채팅 템플릿에 맞춰 넣고 모델의 답만 돌려준다."""
    입력 = 토크나이저.apply_chat_template(대화, add_generation_prompt=True,
                                         return_tensors="pt", return_dict=True)
    with torch.no_grad():
        결과 = 모델.generate(**입력, max_new_tokens=최대, do_sample=False,
                             repetition_penalty=1.1)      # 모델 기본값의 반복 억제는 켜 둔다
    return 토크나이저.decode(결과[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True)


기록 = [{"role": "user", "content": "내 이름은 민준이야."}]
기록.append({"role": "assistant", "content": 묻기(기록)})
print("첫 답:", 기록[-1]["content"])

새_질문 = {"role": "user", "content": "내 이름이 뭐라고 했지?"}
print("기록 없이:", 묻기([새_질문]))
print("기록 함께:", 묻기(기록 + [새_질문]))
print("모델에 들어간 메시지 수:", len(기록 + [새_질문]))
```

```text
첫 답: 안녕하세요! 저는 AI 어시스턴트인 Qwen입니다. 어떻게 도와드릴까요?
기록 없이: 저는 "Qwen"라는 이름을 가지고 있습니다. 이 이름은 "Quantum Neural Network"의 약자로, AI 분야에서 중요한 역할을 하는 인공지능
기록 함께: 당신의 이름은 "민준"이라고 합니다.
모델에 들어간 메시지 수: 3
```

첫 답은 인사만 하고 이름은 따라 말하지 않았네요. 그다음이 중요합니다. 새 질문만 보내면 모델은 민준이라는 이름을 모른 채, 자기 이름이 "Qwen"이라며 "Quantum Neural Network"의 약자라는 지어낸 설명까지 덧붙였어요(실제로 그런 뜻이 아닙니다). 앞의 대화를 리스트에 쌓아 **함께 보내야** 비로소 "민준"이라고 답합니다.

모델 자체에는 기억 장치가 없습니다. 매번 처음 보는 글을 받아 다음 토큰을 이어 쓸 뿐이에요. 챗봇이 대화를 기억하는 것처럼 보이는 건, 프로그램이 지금까지의 대화를 모두 이어 붙여 매번 다시 넣어 주기 때문입니다. 그래서 대화가 길어질수록 넣는 토큰이 늘어나 느려지고, 14.1절의 최대 길이를 넘으면 앞부분을 잘라 내야 해요.

## 14.5 작은 모델의 한계를 정직하게 보기

지금까지 이상한 대답을 몇 번 봤습니다. 이번에는 일부러 사실을 묻는 질문을 해서 한계를 똑바로 보겠습니다.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()


def 묻기(질문: str, 최대: int = 45) -> str:
    """질문 하나를 채팅 형식으로 묻고 답을 한 줄로 돌려준다."""
    입력 = 토크나이저.apply_chat_template([{"role": "user", "content": 질문}],
                                         add_generation_prompt=True,
                                         return_tensors="pt", return_dict=True)
    with torch.no_grad():
        결과 = 모델.generate(**입력, max_new_tokens=최대, do_sample=False,
                             repetition_penalty=1.1)      # 모델 기본값의 반복 억제는 켜 둔다
    답 = 토크나이저.decode(결과[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True)
    return 답.replace("\n", " ")


for 질문 in ["파이썬에서 리스트와 튜플의 차이를 한 문장으로 설명해 줘.",
           "In one sentence, what is the difference between a list and a tuple in Python?",
           "37 곱하기 24는 얼마야? 숫자만 답해.",
           "세종대왕이 만든 문자는?",
           "대한민국에서 가장 높은 산은?"]:
    print(f"Q. {질문}\nA. {묻기(질문)}\n")
```

```text
Q. 파이썬에서 리스트와 튜플의 차이를 한 문장으로 설명해 줘.
A. 파이썬에서 리스트와 튜플의 차이는 다음과 같습니다:  1. 리스트는 원소가 변경될 수 있는 자료형입니다. 2. 튜플은 원소가 변경되지 않아서

Q. In one sentence, what is the difference between a list and a tuple in Python?
A. A list and a tuple in Python are both used to store collections of items, but they differ in their structure and operations: lists are mutable (changeable) and can be indexed, while tuples are immutable (unchangeable

Q. 37 곱하기 24는 얼마야? 숫자만 답해.
A. 37 곡 24은 105입니다.

Q. 세종대왕이 만든 문자는?
A. 세종대왕이 만든 문자는 "서울"입니다.  세종대왕은 19세기의 대한민국의 세종도시에 거주한 대한민국의 천년

Q. 대한민국에서 가장 높은 산은?
A. 대한민국에서 가장 높은 산은 울릉산입니다.  물론, 이는 대략적인 기준으로 생각해 보시면 좋을 것 같습니다:  1. 울릉

```

- **리스트와 튜플(한국어)**: 바꿀 수 있는지 없는지는 맞혔지만, "한 문장으로"라는 요청을 무시하고 목록을 시작했습니다.
- **리스트와 튜플(영어)**: 같은 질문을 영어로 하자 한 문장으로, 정확하게 답합니다.
- **곱셈**: 37 × 24는 888인데 105라고 했고, "곱하기"를 "곡"으로 잘못 썼어요.
- **세종대왕이 만든 문자**: 한글이 아니라 "서울"이라 하고, 세종대왕이 19세기 사람이라는 이야기까지 지어냈습니다.
- **가장 높은 산**: 한라산(약 1,950m)이 아니라 있지도 않은 "울릉산"이라고 답했어요.

이렇게 그럴듯한 말투로 사실이 아닌 내용을 지어내는 것을 **환각(hallucination)** 이라고 부릅니다. 이유는 앞에서 본 것들로 설명할 수 있어요.

- **모델이 작습니다.** 사실을 기억해 둘 숫자가 5억 개 남짓뿐입니다. 큰 모델이 수천억 개를 쓰는 것과 비교하면 세상의 지식을 담기에 턱없이 작아요. 문장을 매끄럽게 잇는 능력은 남아도, 정확한 사실은 자주 빠집니다.
- **한국어 글을 적게 봤습니다.** 이 모델은 주로 영어와 중국어 글로 학습했습니다. 모델 카드는 한국어를 포함해 29개가 넘는 언어를 지원한다고 밝히지만, 비중은 훨씬 작아요. 한국어 답에 한자가 섞여 나오는 것(14.4절의 "栽培")도, 같은 질문인데 영어 답이 훨씬 나은 것도 이 때문이에요. 14.1절에서 본 것처럼 한국어는 토큰도 더 잘게 쪼개져서, 같은 길이 안에 담기는 내용도 적습니다.
- **모델은 사실이 아니라 그럴듯함을 배웁니다.** 14.2절에서 "대한민국의 수도는" 다음에 물음표를 1등으로 고른 것처럼, 모델의 목표는 처음부터 끝까지 "다음에 올 법한 토큰"입니다. 계산기처럼 곱셈을 하지 않고, 사전처럼 사실을 찾아보지 않아요.

그러면 이 모델은 쓸모가 없을까요? 그렇지 않습니다. 형식을 맞추고, 짧게 정리하고, 정해진 꼴로 답하는 일은 잘해요. 그리고 노트북에서 몇 분 안에 학습시켜 볼 수 있을 만큼 작다는 것이 이 장에서는 가장 큰 장점입니다. 같은 코드에 모델 이름만 큰 모델로 바꾸면 답의 질은 확 올라가지만, 그만큼 메모리가 필요해요. 라이선스도 다시 봐야 합니다. 같은 Qwen2.5 계열이라도 크기마다 라이선스가 달라서, 이 책을 쓸 때 모델 카드를 확인해 보니 0.5B·1.5B·7B·14B·32B는 Apache-2.0이지만 3B는 비상업 연구용으로만 쓸 수 있는 Qwen Research 라이선스, 72B는 월 사용자가 1억 명을 넘는 서비스라면 따로 허락을 받아야 하는 Qwen 라이선스였어요. 크기를 바꿀 때는 모델 카드의 라이선스부터 다시 확인하세요. 얼마나 필요한지 계산해 보겠습니다.

## 14.6 메모리 계산과 양자화 맛보기

### 내 노트북에 들어갈까?

4장 4.3절에서 "70억 × 4바이트 = 26.1GB"를 계산하며 7B 모델은 보통 노트북 GPU에 올라가지도 않는다고 했습니다. 이제 진짜 모델로 같은 계산을 해 봐요.

```python
import torch
from transformers import AutoConfig, AutoModelForCausalLM

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32)
GB = 1024 ** 3

# 4장 4.3절: 메모리 = 칸 크기(element_size) × 칸 개수(numel)
바이트 = sum(p.element_size() * p.numel() for p in 모델.parameters())
print(f"float32로 올린 이 모델: {바이트 / GB:.2f} GB")
print("입력 임베딩과 출력층이 같은 가중치인가:",
      모델.get_input_embeddings().weight is 모델.get_output_embeddings().weight)

# 같은 계산을 크기별·자료형별로: 칸당 바이트 수만 바꾸면 된다
for 크기, 개수 in [("0.5B", 494_032_768), ("7B", 7_000_000_000), ("70B", 70_000_000_000)]:
    칸 = {"float32": 4, "bfloat16": 2, "int8": 1, "int4": 0.5}
    print(f"{크기:>4}: " + ", ".join(f"{k} {개수 * v / GB:6.1f}GB" for k, v in 칸.items()))

# 생성할 때 따로 쌓이는 메모리: KV 캐시 (토큰마다 층마다 키와 값을 저장)
설정 = AutoConfig.from_pretrained(이름)
헤드_크기 = 설정.hidden_size // 설정.num_attention_heads
토큰당 = 2 * 설정.num_hidden_layers * 설정.num_key_value_heads * 헤드_크기 * 2   # bfloat16 기준
print(f"키·값 헤드 {설정.num_key_value_heads}개, 헤드 크기 {헤드_크기}, 토큰당 {토큰당:,}바이트")
print(f"토큰 32,768개를 기억하면 KV 캐시 {토큰당 * 32_768 / GB:.2f} GB")
print(f"키·값 헤드가 쿼리 헤드처럼 {설정.num_attention_heads}개였다면 "
      f"{토큰당 * 설정.num_attention_heads // 설정.num_key_value_heads * 32_768 / GB:.2f} GB")
```

```text
float32로 올린 이 모델: 1.84 GB
입력 임베딩과 출력층이 같은 가중치인가: True
0.5B: float32    1.8GB, bfloat16    0.9GB, int8    0.5GB, int4    0.2GB
  7B: float32   26.1GB, bfloat16   13.0GB, int8    6.5GB, int4    3.3GB
 70B: float32  260.8GB, bfloat16  130.4GB, int8   65.2GB, int4   32.6GB
키·값 헤드 2개, 헤드 크기 64, 토큰당 12,288바이트
토큰 32,768개를 기억하면 KV 캐시 0.38 GB
키·값 헤드가 쿼리 헤드처럼 14개였다면 2.62 GB
```

파라미터마다 `element_size() × numel()`을 더하니 1.84GB입니다. 4억 9천만 × 4바이트를 1024³으로 나눈 값과 같아요. 두 번째 줄은 하나 짚어 둘 점입니다. 토큰 번호를 896개 숫자로 바꾸는 입력 임베딩과, 896개 숫자를 다시 15만 개 점수로 바꾸는 출력층이 **같은 가중치를 함께 쓰고** 있어요. 어휘가 15만 개라 이 행렬만 1억 3천만 개가 넘는데, 두 번 두지 않고 한 번만 둬서 아낀 겁니다. 작은 모델에서 자주 쓰는 방법이에요.

가운데 표는 같은 계산을 크기와 자료형만 바꿔 한 것입니다. 7B 모델은 `float32`로 26.1GB, `bfloat16`으로 13.0GB, 숫자 하나를 4비트(0.5바이트)에 담는 `int4`로는 3.3GB예요. 70B 모델도 `int4`라면 32.6GB까지 내려옵니다. 큰 모델을 노트북에서 돌린다는 이야기는 대부분 이렇게 **칸을 줄여서** 담는다는 뜻이에요.

마지막 세 줄은 모델 가중치 말고 따로 쌓이는 메모리, 14.2절의 **KV 캐시**입니다. 생성하는 동안 층마다, 토큰마다 키와 값을 저장하니 크기는 `2(키와 값) × 층 수 × 키·값 헤드 수 × 헤드 크기 × 칸 크기`예요. 이 모델은 토큰 하나에 12,288바이트, 최대 길이 32,768토큰을 다 채우면 0.38GB입니다. 그런데 어텐션 헤드는 14개인데 키·값 헤드는 2개뿐이죠? 쿼리 헤드 일곱 개가 키·값 헤드 하나를 함께 쓰는 설계라서 그래요. 이런 설계를 **그룹 쿼리 어텐션(GQA, Grouped-Query Attention)** 이라고 부릅니다. 키·값 헤드가 14개였다면 2.62GB가 필요했을 테니 일곱 배를 아낀 셈입니다. 긴 글을 다루는 모델에서는 가중치보다 이 캐시가 더 커지기도 해요.

### bfloat16으로 절반만 쓰기

칸을 줄이면 답이 달라질까요? 가장 쉬운 방법인 `bfloat16`부터 비교해 보겠습니다. 불러올 때 `dtype`만 바꾸면 돼요.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
입력 = 토크나이저.apply_chat_template([{"role": "user", "content": "1 더하기 1은?"}],
                                     add_generation_prompt=True,
                                     return_tensors="pt", return_dict=True)
결과 = {}
for 자료형 in [torch.float32, torch.bfloat16]:
    모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=자료형).eval()
    with torch.no_grad():
        로짓 = 모델(**입력).logits[0, -1].float()
        생성 = 모델.generate(**입력, max_new_tokens=20, do_sample=False,
                             repetition_penalty=1.1)
    결과[자료형] = 로짓
    print(f"{str(자료형):15} {모델.get_memory_footprint() / 1024**3:.2f} GB  "
          f"{토크나이저.decode(생성[0, 입력['input_ids'].shape[1]:], skip_special_tokens=True)!r}")

차이 = (결과[torch.float32] - 결과[torch.bfloat16]).abs()
print(f"다음 토큰 점수 차이: 평균 {차이.mean():.3f}, 최대 {차이.max():.3f}")
print("1등 토큰이 같은가:", (결과[torch.float32].argmax() == 결과[torch.bfloat16].argmax()).item())
```

```text
torch.float32   1.84 GB  '1 더하기 1은 2입니다.\n\n더하기 연산자는 두 수를 더합니다'
torch.bfloat16  0.92 GB  '1 더하기 1은 2입니다.\n\n더하기 연산자는 두 수를 더합니다'
다음 토큰 점수 차이: 평균 0.089, 최대 0.458
1등 토큰이 같은가: True
```

`get_memory_footprint()`로 잰 메모리가 1.84GB에서 0.92GB로 정확히 절반이 됐고, 생성된 문장은 똑같습니다. 다음 토큰 점수를 비교하면 평균 0.089, 큰 곳은 0.458까지 차이가 나지만, 1등 토큰은 같아요. 4장 4.3절에서 말한 대로 딥러닝은 끝자리의 작은 오차에 둔감합니다. 그래서 요즘 LLM은 대부분 `bfloat16`으로 배포되고 쓰입니다. 학습까지 16비트로 빠르게 하는 방법은 16장에서 다룹니다.

### 양자화 맛보기: 숫자를 정수 칸에 담기

`bfloat16`보다 더 줄이려면 실수를 **정수**로 바꿔 담습니다. 이것을 **양자화(quantization)** 라고 해요. 원리는 자에 눈금을 새기는 것과 같습니다. 행마다 가장 큰 절댓값을 찾아 그 값이 127이 되게 눈금 간격(배율)을 정하고, 모든 값을 가장 가까운 눈금에 맞춰 정수로 기록해요. 쓸 때는 정수에 배율을 곱해 실수로 되돌립니다. 그 원리를 직접 구현해서, 트랜스포머 층 안의 모든 선형층 가중치를 "정수로 바꿨다가 되돌린 값"으로 바꿔치기해 보겠습니다.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def 양자화_왕복(w: torch.Tensor, 비트: int) -> torch.Tensor:
    """행마다 가장 큰 절댓값을 기준으로 정수 칸에 맞춰 반올림했다가 다시 실수로 되돌린다."""
    최대정수 = 2 ** (비트 - 1) - 1                          # int8이면 127, int4면 7
    배율 = w.abs().amax(dim=1, keepdim=True) / 최대정수        # 행마다 하나 (keepdim: 4장 4.6절)
    정수 = (w / 배율).round().clamp(-최대정수, 최대정수)       # 이 정수만 저장하면 된다
    return 정수 * 배율


w = torch.tensor([[0.12, -0.50, 0.33, 0.07]])
print("원래   :", w)
print("int8   :", 양자화_왕복(w, 8))
print("int4   :", 양자화_왕복(w, 4))

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
문장 = ("파이썬은 배우기 쉬운 프로그래밍 언어입니다. "
        "많은 사람들이 데이터 분석과 인공지능에 파이썬을 씁니다.")
번호 = 토크나이저(문장, return_tensors="pt")["input_ids"]
for 비트 in [None, 8, 4]:
    모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()
    if 비트:
        with torch.no_grad():
            for 층 in 모델.model.layers.modules():          # 트랜스포머 층 안의 선형층만
                if isinstance(층, torch.nn.Linear):
                    층.weight.copy_(양자화_왕복(층.weight, 비트))
    with torch.no_grad():
        손실 = 모델(번호, labels=번호).loss.item()
    print(f"{'원래 float32' if 비트 is None else f'int{비트} 흉내':12} 손실 {손실:.3f}  "
          f"(다음 토큰 정답 확률의 기하평균 {torch.exp(torch.tensor(-손실)):.3f})")
```

```text
원래   : tensor([[ 0.1200, -0.5000,  0.3300,  0.0700]])
int8   : tensor([[ 0.1181, -0.5000,  0.3307,  0.0709]])
int4   : tensor([[ 0.1429, -0.5000,  0.3571,  0.0714]])
원래 float32   손실 2.189  (다음 토큰 정답 확률의 기하평균 0.112)
int8 흉내      손실 2.200  (다음 토큰 정답 확률의 기하평균 0.111)
int4 흉내      손실 3.968  (다음 토큰 정답 확률의 기하평균 0.019)
```

먼저 숫자 네 개짜리 예제입니다. 가장 큰 절댓값이 0.5라서 `int8`이면 눈금 간격이 0.5/127, `int4`면 0.5/7입니다. `int8`은 0.12가 0.1181이 되는 정도로 거의 원래 값이지만, `int4`는 눈금이 열다섯 개(-7~7)뿐이라 0.12가 0.1429로 꽤 멀리 밀렸어요. 가장 큰 값 -0.5는 눈금 위에 정확히 있으니 둘 다 그대로입니다.

이것을 모델 전체에 적용하고 문장 하나의 손실(6장의 교차 엔트로피)을 쟀습니다. 괄호 안의 값은 손실을 확률로 되돌린 것으로, 정답 토큰에 평균적으로 얼마의 확률을 줬는지를 뜻해요. `int8`은 손실이 2.189에서 2.200으로 거의 그대로지만, `int4`는 3.968로 크게 나빠졌습니다. 정답 토큰에 주는 확률이 11%에서 2%로 떨어졌으니 문장을 제대로 이어 쓰기 어려운 수준이에요.

여기서는 원리만 보이려고 정수를 다시 실수로 되돌려 넣었으니 메모리는 줄지 않았습니다. 실제 양자화 도구는 정수와 배율만 저장하고 계산할 때 되돌려요. 그리고 `int4`가 망가진 건 행마다 배율을 **하나만** 썼기 때문입니다. 실제 4비트 양자화는 숫자 수십 개씩 작은 묶음마다 배율을 따로 두고, 결과가 덜 나빠지도록 눈금을 고르는 요령을 더해서 7B 모델도 쓸 만한 품질을 지켜요. 그 방법들과 모델을 실제로 작게 만들어 배포하는 과정은 19장에서 다룹니다.

> **Q. 양자화하면 계산도 빨라지나요?**
> 장비와 방법에 따라 다릅니다. 정수 계산을 빠르게 하는 하드웨어에서 정수 그대로 계산하면 빨라지고, 정수를 실수로 되돌려 계산하는 방식이면 오히려 조금 느려질 수도 있어요. 그래도 LLM 생성은 대개 "계산"보다 "가중치를 메모리에서 읽어 오는 시간"이 병목이라, 읽을 바이트가 줄어드는 것만으로 빨라지는 경우가 많습니다. 확실한 이득은 메모리예요. 들어가지 않던 모델이 들어가게 됩니다. 속도를 재는 법은 16장, 양자화 도구는 19장에서 다룹니다.

## 14.7 LoRA의 아이디어: 고칠 부분만 작게

### 교과서를 다시 쓰지 말고 포스트잇을 붙이기

이제 모델을 우리 일에 맞게 고칠 차례입니다. 6장의 방법대로라면 5억 개 숫자 모두에 기울기를 구하고 Adam으로 고치면 되죠. 그런데 계산해 보면 만만치 않습니다. Adam은 숫자마다 기울기와 이동 평균 두 개를 더 들고 있어야 해서, `float32`라면 가중치 1.84GB에 더해 약 5.5GB가 더 필요해요. 7B 모델이면 100GB가 넘습니다. 고친 모델을 저장할 때도 매번 모델 전체 크기의 파일이 생기고요.

두꺼운 교과서에 틀린 곳이 몇 군데 있다고 책을 통째로 다시 쓰지는 않습니다. 고칠 곳에 포스트잇을 붙이죠. **LoRA(Low-Rank Adaptation)** 가 바로 그 포스트잇입니다. 원래 가중치 `W`는 그대로 얼려 두고, 옆에 고칠 양 `ΔW`를 더하는데, 이 `ΔW`를 아주 작은 행렬 두 개의 곱 `B @ A`로 만듭니다.

### 작은 행렬 두 개로 큰 행렬 만들기

작은 행렬 두 개를 곱하면 어떤 행렬이 될까요? 4장 4.6절의 행렬 곱 모양 규칙부터 떠올려 봅시다.

```python
import torch

# 세로 벡터 하나 × 가로 벡터 하나 = 표 전체 (외적)
a = torch.tensor([[1.0], [2.0], [3.0]])      # (3, 1)
b = torch.tensor([[10.0, 20.0, 30.0, 40.0]]) # (1, 4)
표 = a @ b                                    # (3, 4): 숫자 7개로 12개짜리 표를 만든다
print(표)
print("랭크:", torch.linalg.matrix_rank(표).item())

torch.manual_seed(0)
B, A = torch.randn(896, 8), torch.randn(8, 896)
print("(896, 8) @ (8, 896) 의 랭크:", torch.linalg.matrix_rank(B @ A).item())

# 가중치 하나를 통째로 고칠 때와 작은 행렬 두 개로 고칠 때의 숫자 개수
d = 896                                       # Qwen2.5-0.5B의 은닉 크기
print(f"통째로: {d * d:,}개")
for r in [1, 4, 8, 16, 64]:
    print(f"랭크 {r:2}: {r * (d + d):7,}개 ({r * (d + d) / (d * d):.1%})")
```

```text
tensor([[ 10.,  20.,  30.,  40.],
        [ 20.,  40.,  60.,  80.],
        [ 30.,  60.,  90., 120.]])
랭크: 1
(896, 8) @ (8, 896) 의 랭크: 8
통째로: 802,816개
랭크  1:   1,792개 (0.2%)
랭크  4:   7,168개 (0.9%)
랭크  8:  14,336개 (1.8%)
랭크 16:  28,672개 (3.6%)
랭크 64: 114,688개 (14.3%)
```

`(3, 1) @ (1, 4)`는 `(3, 4)` 표가 됩니다. 숫자 7개로 숫자 12개짜리 표를 만든 거예요. 다만 결과를 보면 모든 줄이 첫 줄의 1배, 2배, 3배일 뿐입니다. 이렇게 "서로 독립인 줄이 몇 개인가"를 **랭크(rank)** 라고 해요. 이 표는 랭크가 1입니다. 마찬가지로 `(896, 8) @ (8, 896)`은 896 × 896 크기지만 랭크가 8을 넘을 수 없어요. 가운데의 8이 통로처럼 좁아서, 그 폭만큼만 정보가 지나가기 때문입니다.

LoRA는 "모델을 새 일에 맞게 고칠 때 필요한 변화는 이렇게 **랭크가 낮은** 행렬로도 충분하다"는 관찰에서 출발했습니다. 그러면 숫자가 크게 줄어요. 은닉 크기 896짜리 가중치 하나를 통째로 고치면 802,816개를 학습해야 하지만, 랭크 8이면 `8 × (896 + 896)` = 14,336개, 1.8%만 학습하면 됩니다.

### LoRA 층을 손으로 만들기

6장의 `nn.Module`로 LoRA 층을 직접 만들어 보겠습니다. 원래 `nn.Linear`를 받아 얼리고, 옆에 `A`와 `B`를 붙여요.

```python
import torch
from torch import nn


class LoRA선형층(nn.Module):
    """얼린 nn.Linear 옆에 작은 행렬 두 개(A, B)를 붙인 층."""

    def __init__(self, 원래: nn.Linear, r: int = 4, alpha: int = 8) -> None:
        super().__init__()
        self.원래 = 원래
        self.원래.requires_grad_(False)                  # 원래 가중치는 얼린다 (6장 6.4절)
        self.A = nn.Parameter(torch.randn(r, 원래.in_features) * 0.01)   # 작은 무작위 값
        self.B = nn.Parameter(torch.zeros(원래.out_features, r))       # 0에서 시작
        self.배율 = alpha / r

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.원래(x) + (x @ self.A.T @ self.B.T) * self.배율


torch.manual_seed(0)
원래 = nn.Linear(64, 64)
층 = LoRA선형층(원래, r=4)
x = torch.randn(5, 64)
print("처음에는 원래 층과 출력이 같은가:", torch.allclose(층(x), 원래(x)))
for 이름, p in 층.named_parameters():
    print(f"{이름:14} {tuple(p.shape)!s:10} 학습함={p.requires_grad}")
학습 = sum(p.numel() for p in 층.parameters() if p.requires_grad)
전체 = sum(p.numel() for p in 층.parameters())
print(f"학습하는 숫자 {학습:,}개 / 전체 {전체:,}개")
```

```text
처음에는 원래 층과 출력이 같은가: True
A              (4, 64)    학습함=True
B              (64, 4)    학습함=True
원래.weight      (64, 64)   학습함=False
원래.bias        (64,)      학습함=False
학습하는 숫자 512개 / 전체 4,672개
```

`forward`는 원래 층의 출력에 `x @ A.T @ B.T`(입력을 랭크 r의 좁은 통로로 줄였다가 다시 펴는 길)를 더합니다. 6장에서 본 `nn.Linear`의 계산 `x @ weight.T`와 같은 모양이에요. 눈여겨볼 곳은 세 군데입니다.

- **`B`는 0에서 시작합니다.** 그래서 처음에는 `B @ A`가 0이고, LoRA를 붙인 층의 출력이 원래 층과 똑같아요(`True`). 학습을 시작하는 순간 모델이 망가지지 않고, 원래 실력에서 출발해 조금씩 고쳐 나갑니다.
- **`A`는 작은 무작위 값입니다.** 둘 다 0이면 어떻게 될까요? 5장의 연쇄 법칙으로 따져 보면 `B`의 기울기에는 `A`가 곱해지고 `A`의 기울기에는 `B`가 곱해져서, 둘 다 0이면 기울기도 영원히 0이에요. 한쪽만 0으로 둬야 학습이 시작됩니다.
- **배율 `alpha / r`**: 랭크를 바꿔도 고치는 세기가 크게 달라지지 않도록 곱하는 숫자입니다. 보통 `alpha`를 `r`의 1~2배로 둬요.

이 작은 층에서도 학습하는 숫자는 512개, 전체 4,672개의 11% 정도입니다. 층이 클수록 이 비율은 훨씬 작아져요.

### 정말 낮은 랭크로 배워질까?

정답을 알고 있는 장난감 문제로 확인해 보겠습니다. 원래 층에 "랭크 2짜리 변화"를 더한 층을 정답으로 만들어 두고, LoRA로 그 변화를 배울 수 있는지 랭크를 바꿔 가며 봅니다.

```python
import torch
from torch import nn


class LoRA선형층(nn.Module):
    """얼린 nn.Linear 옆에 작은 행렬 두 개(A, B)를 붙인 층 (앞 예제와 같음)."""

    def __init__(self, 원래: nn.Linear, r: int, alpha: int) -> None:
        super().__init__()
        self.원래 = 원래.requires_grad_(False)
        self.A = nn.Parameter(torch.randn(r, 원래.in_features) * 0.01)
        self.B = nn.Parameter(torch.zeros(원래.out_features, r))
        self.배율 = alpha / r

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.원래(x) + (x @ self.A.T @ self.B.T) * self.배율


torch.manual_seed(0)
원래 = nn.Linear(64, 64)
# 목표: 원래 가중치에 "랭크 2짜리 변화"를 더한 층 (예제용으로 만든 정답)
진짜_변화 = torch.randn(64, 2) @ torch.randn(2, 64) * 0.1
x = torch.randn(512, 64)
with torch.no_grad():
    y = x @ (원래.weight + 진짜_변화).T + 원래.bias

for r in [1, 2, 4]:
    torch.manual_seed(1)
    층 = LoRA선형층(원래, r=r, alpha=r)                       # 배율 1로 맞춰 비교
    옵티마이저 = torch.optim.Adam([층.A, 층.B], lr=0.01)
    for 단계 in range(1, 1501):
        손실 = nn.functional.mse_loss(층(x), y)
        옵티마이저.zero_grad()
        손실.backward()
        옵티마이저.step()
    배운_변화 = 층.배율 * 층.B @ 층.A
    오차 = (배운_변화 - 진짜_변화).norm() / 진짜_변화.norm()
    print(f"r={r}: 손실 {손실.item():.6f}, 배운 변화와 진짜 변화의 상대 오차 {오차.item():.3f}")

# 다 배운 뒤에는 W + 배율·(B @ A)를 미리 더해 보통 층 하나로 합칠 수 있다
with torch.no_grad():
    합친 = nn.Linear(64, 64)
    합친.weight.copy_(원래.weight + 층.배율 * 층.B @ 층.A)
    합친.bias.copy_(원래.bias)
    print("합친 층과 LoRA 층의 출력이 같은가:", torch.allclose(합친(x), 층(x), atol=1e-5))
```

```text
r=1: 손실 0.502039, 배운 변화와 진짜 변화의 상대 오차 0.658
r=2: 손실 0.000000, 배운 변화와 진짜 변화의 상대 오차 0.000
r=4: 손실 0.000000, 배운 변화와 진짜 변화의 상대 오차 0.000
합친 층과 LoRA 층의 출력이 같은가: True
```

진짜 변화의 랭크가 2이니, 랭크 1인 LoRA는 손실이 0.502에서 더 내려가지 못하고 배운 변화도 진짜와 66%나 어긋납니다. 통로가 너무 좁은 거예요. 랭크 2와 4는 손실이 0이 되고, 배운 변화가 진짜 변화와 거의 정확히 같아졌습니다. 원래 가중치 4,096개는 한 번도 건드리지 않고, `A`와 `B`만 고쳐서 얻은 결과예요.

마지막 줄도 중요합니다. 다 배운 뒤에는 `W + 배율 × (B @ A)`를 미리 계산해 **보통 `nn.Linear` 하나로 합칠** 수 있어요. 합친 층의 출력은 LoRA 층과 같습니다. 그래서 LoRA로 학습한 모델은 배포할 때 추가 계산이 전혀 없습니다. 이것이 LoRA가 널리 쓰이는 또 하나의 이유예요.

> **Q. 랭크는 얼마로 정하면 되나요?**
> 정답은 데이터로 정하지만, LLM 미세조정에서는 4~16에서 시작하는 경우가 많습니다. 말투나 답의 형식처럼 바꿀 것이 단순하면 작은 랭크로 충분하고, 새로운 일을 많이 가르칠수록 큰 랭크가 도움이 돼요. 다만 위 실험처럼 필요한 만큼을 넘으면 더 좋아지지 않고 학습할 숫자만 늘어납니다. 8장처럼 검증 데이터로 몇 가지를 비교해 고르세요.

## 14.8 peft로 LLM에 LoRA 붙이기

손으로 만든 `LoRA선형층`을 모델의 선형층 수백 개에 하나씩 끼워 넣을 수도 있지만, `peft` 라이브러리가 그 일을 해 줍니다. 어느 층에 붙일지, 랭크는 얼마인지 설정만 적으면 돼요.

```python
import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

이름 = "Qwen/Qwen2.5-0.5B-Instruct"
토크나이저 = AutoTokenizer.from_pretrained(이름)
모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()
입력 = 토크나이저("LoRA를 붙여도 처음에는 출력이 같을까?", return_tensors="pt")
with torch.no_grad():
    붙이기_전 = 모델(**입력).logits

설정 = LoraConfig(
    r=8,                                                   # 작은 행렬의 랭크
    lora_alpha=16,                                         # 배율 = lora_alpha / r = 2
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # 어텐션의 선형층 네 개
    task_type="CAUSAL_LM",
)
모델 = get_peft_model(모델, 설정)
모델.print_trainable_parameters()

층0 = 모델.base_model.model.model.layers[0].self_attn
print(층0.k_proj)

# 손으로 세어 보기: 층마다 r × (입력 + 출력)
손계산 = sum(8 * (층.in_features + 층.out_features)
           for 층 in [층0.q_proj.base_layer, 층0.k_proj.base_layer,
                     층0.v_proj.base_layer, 층0.o_proj.base_layer]) * 24
print(f"손으로 센 LoRA 숫자: {손계산:,}개")

모델.eval()
with torch.no_grad():
    붙인_뒤 = 모델(**입력).logits
print("붙이기 전후 출력이 같은가:", torch.allclose(붙이기_전, 붙인_뒤))
```

```text
trainable params: 1,081,344 || all params: 495,114,112 || trainable%: 0.2184
lora.Linear(
  (base_layer): Linear(in_features=896, out_features=128, bias=True)
  (lora_dropout): ModuleDict(
    (default): Dropout(p=0.05, inplace=False)
  )
  (lora_A): ModuleDict(
    (default): Linear(in_features=896, out_features=8, bias=False)
  )
  (lora_B): ModuleDict(
    (default): Linear(in_features=8, out_features=128, bias=False)
  )
  (lora_embedding_A): ParameterDict()
  (lora_embedding_B): ParameterDict()
  (lora_magnitude_vector): ModuleDict()
)
손으로 센 LoRA 숫자: 1,081,344개
붙이기 전후 출력이 같은가: True
```

`target_modules`에 이름을 적은 선형층만 LoRA 층으로 바뀝니다. 여기서는 트랜스포머 블록마다 있는 어텐션의 네 선형층, 즉 쿼리(`q_proj`)·키(`k_proj`)·값(`v_proj`)을 만드는 층과 출력(`o_proj`) 층을 골랐어요. 12장에서 직접 만든 어텐션의 그 부품들입니다.

`print_trainable_parameters()`를 보면 학습하는 숫자는 1,081,344개, 전체의 0.22%예요. 5억 개 중 108만 개만 고치는 겁니다. 바뀐 `k_proj`를 찍어 보면 원래 층(`base_layer`)을 감싸고 옆에 `lora_A`(896 → 8), `lora_B`(8 → 128)가 붙어 있죠. 앞에서 손으로 만든 구조 그대로이고, `lora_dropout`은 8장 8.3절의 드롭아웃을 LoRA 쪽 입력에만 거는 것입니다.

손으로도 세어 봤습니다. 층마다 `r × (입력 + 출력)`이니 첫 블록의 네 층은 `8 × (896 + 896) + 8 × (896 + 128) × 2 + 8 × (896 + 896)` = 45,056개이고, 블록이 24개라 1,081,344개입니다. `peft`가 센 숫자와 정확히 같아요. 키와 값의 출력이 896이 아니라 128인 것은 14.6절에서 본 대로 키·값 헤드가 2개(2 × 64)뿐이기 때문입니다. 마지막 줄은 LoRA를 붙이기 전과 후의 출력이 똑같다는 확인이에요. `B`가 0에서 시작하는 덕분입니다.

> **Q. `target_modules`는 어떻게 고르나요?**
> 모델 구조를 `print(모델)`로 찍어 보면 선형층들의 이름이 나옵니다. 이 장처럼 어텐션 층만 고르는 것이 가장 가볍고, 피드포워드 층(Qwen에서는 `gate_proj`, `up_proj`, `down_proj`)까지 넣으면 학습할 숫자가 늘어나는 대신 더 많은 것을 바꿀 수 있어요. 이름은 모델마다 다르니(GPT-2는 `c_attn` 등) 새 모델을 쓸 때는 꼭 찍어 보고 정하세요.

## 14.9 실습: 1권 도우미로 미세조정하기

### 목표와 데이터

마지막으로 이 장의 모델을 우리 일에 맞게 고쳐 보겠습니다. 목표는 "이 책 1권의 내용을 묻는 질문에, 짧게 답하고 끝에 `(참고: 1권 N장)`을 붙이는 도우미"예요. 학습 데이터는 이 책에서 직접 만든 **예제용** 질문과 답 42쌍이고, 학습에 쓰지 않은 시험 문답 6쌍을 따로 두었습니다. 시험 문답 중 넷은 학습 문답과 같은 내용을 다르게 묻고, 둘(f-string, 정규 표현식)은 학습 문답에 아예 없는 주제예요. 8장처럼 "본 적 없는 문제도 잘 푸는가"를 확인하려는 겁니다.

1권 14장에서 배운 대로 데이터는 모듈 하나에 담아 두겠습니다. 아래 내용을 `일권문답.py`로 저장하세요.

```python
"""LoRA 실습용 지시-응답 데이터: 1권 내용에 대한 질문과 답 (이 책에서 직접 만든 예제용 데이터)."""

시스템 = "너는 파이썬 입문서의 질문에 짧게 답하는 도우미야."

# 학습용 (질문, 답) 짝 42개. 답은 모두 "참고: 1권 N장"으로 끝나게 맞췄다.
학습_문답 = [
    ("변수란 무엇인가요?", "값에 붙이는 이름표예요. `나이 = 20`처럼 등호로 이름과 값을 묶어 두고 이름으로 다시 꺼내 씁니다. (참고: 1권 2장)"),
    ("파이썬에서 문자열은 어떻게 만드나요?", "글자를 작은따옴표나 큰따옴표로 감싸면 됩니다. 여러 줄이면 따옴표 세 개로 감싸요. (참고: 1권 2장)"),
    ("type 함수는 무엇을 알려 주나요?", "값의 자료형을 알려 줍니다. `type(3.14)`는 float를 돌려줘요. (참고: 1권 2장)"),
    ("7 // 2와 7 % 2의 결과는 무엇인가요?", "`7 // 2`는 몫인 3, `7 % 2`는 나머지인 1입니다. (참고: 1권 3장)"),
    ("정수끼리 / 로 나누면 결과도 정수인가요?", "아니요. `/`는 언제나 실수를 돌려줘서 `6 / 3`은 2.0입니다. 몫만 원하면 `//`를 씁니다. (참고: 1권 3장)"),
    ("==와 is는 어떻게 다른가요?", "`==`는 값이 같은지, `is`는 같은 물건(객체)인지를 묻습니다. (참고: 1권 3장)"),
    ("if 문은 어떻게 쓰나요?", "`if 조건:`처럼 조건 뒤에 콜론을 찍고, 실행할 문장을 들여 써서 씁니다. (참고: 1권 4장)"),
    ("elif는 언제 쓰나요?", "조건이 여러 개일 때 if 다음에 이어서 다른 조건을 차례로 검사할 때 씁니다. (참고: 1권 4장)"),
    ("for 문과 while 문은 어떻게 다른가요?", "for는 정해진 묶음을 처음부터 끝까지 돌고, while은 조건이 참인 동안 계속 돕니다. (참고: 1권 5장)"),
    ("break와 continue의 차이는 무엇인가요?", "break는 반복을 완전히 끝내고, continue는 이번 차례만 건너뛰고 다음 차례로 갑니다. (참고: 1권 5장)"),
    ("range(5)는 어떤 숫자를 만드나요?", "0부터 4까지 정수 다섯 개를 만듭니다. 끝 값 5는 들어가지 않아요. (참고: 1권 5장)"),
    ("리스트와 튜플의 차이는 무엇인가요?", "리스트는 만든 뒤에도 바꿀 수 있고, 튜플은 한번 만들면 바꿀 수 없습니다. (참고: 1권 6장)"),
    ("리스트 a에서 a[1:3]은 무엇을 꺼내나요?", "1번부터 3번 앞까지, 즉 1번과 2번 항목을 새 리스트로 꺼냅니다. (참고: 1권 6장)"),
    ("리스트 컴프리헨션이란 무엇인가요?", "`[x * 2 for x in 숫자]`처럼 반복과 리스트 만들기를 한 줄로 쓰는 문법이에요. (참고: 1권 6장)"),
    ("딕셔너리란 무엇인가요?", "키와 값을 짝지어 담는 자료형입니다. 키로 값을 바로 찾을 수 있어요. (참고: 1권 7장)"),
    ("딕셔너리에 없는 키를 오류 없이 읽으려면 어떻게 하나요?", "`get` 메서드를 쓰면 키가 없을 때 오류 대신 None이나 정해 둔 기본값을 돌려줍니다. (참고: 1권 7장)"),
    ("집합(set)의 특징은 무엇인가요?", "순서가 없고 같은 값을 한 번만 담습니다. 중복을 없앨 때 편해요. (참고: 1권 7장)"),
    ("dataclass는 무엇을 해 주나요?", "필드만 적으면 `__init__`과 `__repr__` 같은 메서드를 자동으로 만들어 줍니다. (참고: 1권 8장)"),
    ("Pydantic은 언제 쓰나요?", "들어온 데이터의 자료형과 값을 검사하고 알맞게 바꿀 때 씁니다. (참고: 1권 8장)"),
    ("함수는 어떻게 만드나요?", "`def` 뒤에 이름과 괄호를 쓰고, 들여 쓴 본문에서 `return`으로 결과를 돌려줍니다. (참고: 1권 9장)"),
    ("기본값 매개변수란 무엇인가요?", "`def 인사(이름=\"손님\")`처럼 값을 넘기지 않으면 대신 쓸 값을 정해 둔 매개변수예요. (참고: 1권 9장)"),
    ("*args와 **kwargs는 무엇인가요?", "`*args`는 위치 인자를 튜플로, `**kwargs`는 키워드 인자를 딕셔너리로 모아 받습니다. (참고: 1권 9장)"),
    ("재귀 함수란 무엇인가요?", "자기 자신을 다시 부르는 함수입니다. 멈추는 조건을 꼭 넣어야 해요. (참고: 1권 9장)"),
    ("lambda는 무엇인가요?", "이름 없이 한 줄로 만드는 작은 함수입니다. `lambda x: x * 2`처럼 씁니다. (참고: 1권 10장)"),
    ("map과 filter는 무엇을 하나요?", "map은 모든 항목에 함수를 적용하고, filter는 조건을 만족하는 항목만 남깁니다. (참고: 1권 10장)"),
    ("데코레이터란 무엇인가요?", "함수를 받아 기능을 덧붙인 새 함수를 돌려주는 함수로, 함수 위에 `@이름`을 붙여 씁니다. (참고: 1권 10장)"),
    ("클래스와 객체는 어떤 관계인가요?", "클래스는 설계도이고, 객체는 그 설계도로 만든 실제 물건입니다. (참고: 1권 11장)"),
    ("메서드의 self는 무엇인가요?", "메서드를 부른 객체 자신을 가리키는 첫 번째 매개변수예요. (참고: 1권 11장)"),
    ("__init__ 메서드는 언제 실행되나요?", "객체를 만들 때 자동으로 실행되어 처음 값을 채웁니다. (참고: 1권 11장)"),
    ("파일을 안전하게 여는 방법은 무엇인가요?", "`with open(...) as f:`로 열면 블록이 끝날 때 파일이 저절로 닫힙니다. (참고: 1권 12장)"),
    ("try와 except는 무엇에 쓰나요?", "오류가 날 수 있는 코드를 try에 넣고, 오류가 나면 except에서 처리합니다. (참고: 1권 12장)"),
    ("pathlib은 무엇에 쓰나요?", "파일 경로를 객체로 다룹니다. `Path(\"data\") / \"a.txt\"`처럼 경로를 이어 붙여요. (참고: 1권 12장)"),
    ("상속이란 무엇인가요?", "기존 클래스의 기능을 물려받아 새 클래스를 만드는 방법입니다. `class 자식(부모):`처럼 씁니다. (참고: 1권 13장)"),
    ("super()는 무엇에 쓰나요?", "부모 클래스의 메서드를 부를 때 씁니다. 자식의 `__init__`에서 `super().__init__()`을 자주 불러요. (참고: 1권 13장)"),
    ("모듈이란 무엇인가요?", "함수와 클래스를 담아 둔 파이썬 파일로, `import`로 불러 씁니다. (참고: 1권 14장)"),
    ("패키지는 모듈과 어떻게 다른가요?", "패키지는 여러 모듈을 폴더 하나로 묶은 것입니다. (참고: 1권 14장)"),
    ("제너레이터란 무엇인가요?", "`yield`로 값을 하나씩 만들어 주는 함수입니다. 모든 값을 한꺼번에 메모리에 올리지 않아요. (참고: 1권 15장)"),
    ("반복자(iterator)란 무엇인가요?", "`next()`를 부를 때마다 다음 값을 하나씩 주는 객체입니다. (참고: 1권 15장)"),
    ("SQLite는 무엇인가요?", "파일 하나에 저장되는 가벼운 데이터베이스로, 파이썬에 `sqlite3` 모듈이 들어 있습니다. (참고: 1권 18장)"),
    ("FastAPI는 무엇인가요?", "파이썬으로 웹 API를 빠르게 만드는 프레임워크입니다. (참고: 1권 19장)"),
    ("pandas의 DataFrame은 무엇인가요?", "행과 열로 된 표 데이터를 다루는 자료형입니다. (참고: 1권 20장)"),
    ("uv는 무엇인가요?", "파이썬과 패키지를 설치하고 프로젝트 환경을 관리하는 도구예요. `uv add`로 패키지를 더합니다. (참고: 1권 1장)"),
]

# 학습에 쓰지 않은 문답: 위 내용을 다르게 묻거나(앞의 넷), 아예 없는 주제(뒤의 둘)
시험_문답 = [
    ("튜플은 값을 바꿀 수 있나요?", "아니요. 튜플은 한번 만들면 바꿀 수 없습니다. 바꿔야 하면 리스트를 씁니다. (참고: 1권 6장)"),
    ("with 문으로 파일을 열면 무엇이 좋은가요?", "블록이 끝나면 파일이 저절로 닫혀서 닫기를 잊을 걱정이 없습니다. (참고: 1권 12장)"),
    ("yield는 무엇을 하나요?", "값을 하나 내보내고 그 자리에서 멈췄다가, 다음 값을 달라고 하면 이어서 실행합니다. (참고: 1권 15장)"),
    ("부모 클래스의 메서드를 자식 클래스에서 부르려면 어떻게 하나요?", "`super().메서드이름()`처럼 super()를 거쳐 부릅니다. (참고: 1권 13장)"),
    ("f-string은 무엇인가요?", "문자열 앞에 f를 붙이고 중괄호 안에 변수를 넣어 값을 끼워 넣는 문법입니다. (참고: 1권 2장)"),
    ("정규 표현식은 무엇인가요?", "글자의 규칙(패턴)을 적어 문자열을 찾거나 바꾸는 방법으로, `re` 모듈로 씁니다. (참고: 1권 17장)"),
]
```

실습의 여러 예제가 같은 준비 코드를 쓰니, 8장의 `학습도구.py`처럼 모듈로 모아 둡니다. 아래 내용을 `문답도우미.py`로 저장하세요.

```python
"""14.9절 실습에서 함께 쓰는 준비 코드."""
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from 일권문답 import 시스템

모델_이름 = "Qwen/Qwen2.5-0.5B-Instruct"
어댑터_경로 = "data/lora_1권도우미"


def 불러오기() -> tuple:
    """토크나이저와 float32 모델을 불러온다. 결과를 재현하기 쉽게 CPU에서 쓴다."""
    토크나이저 = AutoTokenizer.from_pretrained(모델_이름)
    모델 = AutoModelForCausalLM.from_pretrained(모델_이름, dtype=torch.float32).eval()
    return 토크나이저, 모델


def 프롬프트(토크나이저, 질문: str) -> str:
    """시스템 지시와 질문을 채팅 템플릿에 맞춘 글로 만든다."""
    대화 = [{"role": "system", "content": 시스템}, {"role": "user", "content": 질문}]
    return 토크나이저.apply_chat_template(대화, tokenize=False, add_generation_prompt=True)


def 예제_만들기(토크나이저, 질문: str, 답: str) -> tuple[torch.Tensor, torch.Tensor]:
    """입력 번호와 정답 번호를 만든다. 질문 부분의 정답은 -100으로 가려 손실에서 뺀다."""
    앞 = 토크나이저(프롬프트(토크나이저, 질문), add_special_tokens=False)["input_ids"]
    뒤 = 토크나이저(답 + "<|im_end|>", add_special_tokens=False)["input_ids"]
    return torch.tensor(앞 + 뒤), torch.tensor([-100] * len(앞) + 뒤)


def 답하기(모델, 토크나이저, 질문: str, 최대: int = 60) -> str:
    """탐욕 디코딩(반복 억제 1.1)으로 답을 만든다."""
    입력 = 토크나이저(프롬프트(토크나이저, 질문), return_tensors="pt", add_special_tokens=False)
    with torch.no_grad():
        결과 = 모델.generate(**입력, max_new_tokens=최대, do_sample=False,
                             repetition_penalty=1.1)      # 모델 기본값의 반복 억제는 켜 둔다
    return 토크나이저.decode(결과[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True)


def 평가(모델, 토크나이저, 문답: list[tuple[str, str]]) -> tuple[float, float, float]:
    """정답을 보여 주며(교사 강요) 세 가지를 잰다.

    답 전체의 평균 손실, '1권 N장'의 N 자리 평균 손실, N을 1등으로 맞힌 비율.
    """
    손실합, 번호손실합, 맞힘 = 0.0, 0.0, 0
    for 질문, 답 in 문답:
        입력, 정답 = 예제_만들기(토크나이저, 질문, 답)
        with torch.no_grad():
            출력 = 모델(input_ids=입력[None], labels=정답[None])
        손실합 += 출력.loss.item()
        # 답 속 "1권 N장"의 N이 몇 번째 토큰인지 찾는다 (숫자는 한 글자씩 토큰이 된다)
        시작 = (정답 != -100).nonzero()[0].item()
        조각 = 토크나이저(답, add_special_tokens=False, return_offsets_mapping=True)
        처음, 끝 = re.search(r"1권 (\d+)장", 답).span(1)
        자리 = [시작 + i for i, (s, e) in enumerate(조각["offset_mapping"])
                if s < 끝 and e > 처음]
        점수 = 출력.logits[0, [j - 1 for j in 자리]]          # 그 토큰을 맞혀야 하는 자리의 점수
        번호손실합 += torch.nn.functional.cross_entropy(점수, 입력[자리]).item()
        맞힘 += bool((점수.argmax(dim=-1) == 입력[자리]).all())
    n = len(문답)
    return 손실합 / n, 번호손실합 / n, 맞힘 / n
```

함수 다섯 개가 들어 있습니다.

- **`불러오기`**: 14.1절과 같습니다. 결과를 재현하기 쉽도록 이 실습은 CPU에서 돌려요. 모델이 작고 데이터가 적어서 CPU로도 충분합니다.
- **`프롬프트`**: 14.4절의 채팅 템플릿으로 시스템 지시와 질문을 하나의 글로 만듭니다.
- **`예제_만들기`**: 학습 예제 하나를 만듭니다. 질문 부분과 답 부분의 번호를 이어 붙이되, 정답 번호에서 질문 부분은 **-100**으로 가려요. 교차 엔트로피 손실(6장 6.5절)은 정답이 -100인 자리를 계산에서 빼도록 정해져 있어서(`ignore_index=-100`이 기본값), 모델은 질문을 따라 쓰는 법이 아니라 **답을 쓰는 법만** 배웁니다. 답 끝에는 `<|im_end|>`를 붙여 "답이 끝나면 멈춘다"까지 배우게 했어요.
- **`답하기`**: 14.4절과 같이 반복 억제(1.1)를 켠 탐욕 디코딩으로 답을 만듭니다.
- **`평가`**: 정답을 한 토큰씩 보여 주며(이를 **교사 강요**라고 해요) 세 가지를 잽니다. 답 전체의 평균 손실, 그중 "1권 N장"의 **N 자리**만의 손실, 그리고 N 자리에서 1등으로 고른 숫자가 정답과 같은 비율입니다. 장 번호를 따로 재는 이유는 곧 결과에서 드러나요. N이 몇 번째 토큰인지는 토크나이저의 `return_offsets_mapping`(토큰마다 원래 글의 몇 번째 글자부터 몇 번째까지인지)으로 찾았습니다.

### 미세조정 전

먼저 고치기 전의 실력을 재 둡니다. 비교할 기준선이 없으면 나중에 좋아졌는지 알 수 없으니까요.

```python
from 문답도우미 import 답하기, 불러오기, 평가
from 일권문답 import 시험_문답, 학습_문답

토크나이저, 모델 = 불러오기()
print(f"학습 문답 {len(학습_문답)}개, 시험 문답 {len(시험_문답)}개")
for 질문, _ in 시험_문답[:3]:
    첫줄 = 답하기(모델, 토크나이저, 질문).strip().splitlines()[0]      # 길어서 첫 줄만
    print(f"Q. {질문}\nA. {첫줄}")

for 이름, 문답 in [("학습", 학습_문답), ("시험", 시험_문답)]:
    손실, 번호손실, 맞힘 = 평가(모델, 토크나이저, 문답)
    print(f"[미세조정 전] {이름} 문답: 답 손실 {손실:.3f}, "
          f"장 번호 자리 손실 {번호손실:.3f}, 장 번호 맞힘 {맞힘:.0%}")
```

```text
학습 문답 42개, 시험 문답 6개
Q. 튜플은 값을 바꿀 수 있나요?
A. 네, 템플을 사용하여 값을 변경할 수 있습니다. 예를 들어, 다음과 같은 코드를 작성하면 `a`와 `b`의 값이 서로 바뀝니다:
Q. with 문으로 파일을 열면 무엇이 좋은가요?
A. with 문은 파일을 항상 닫아주어야 합니다. 이로 인해 파일이 닫히지 않으면 오류를 발생시킵니다. 따라서 파일을 닫아주는 코드를 작성해야 합니다.
Q. yield는 무엇을 하나요?
A. yield는 Python에서 함수를 호출하거나 반복할 때 사용하는 특별한 기능입니다. 
[미세조정 전] 학습 문답: 답 손실 2.782, 장 번호 자리 손실 2.179, 장 번호 맞힘 10%
[미세조정 전] 시험 문답: 답 손실 2.974, 장 번호 자리 손실 2.024, 장 번호 맞힘 0%
```

답이 길어서 첫 줄만 보였는데, 질문 셋 모두 틀렸습니다. 튜플을 바꿀 수 있다고 하고("템플"이라는 오타까지 냈어요), with 문은 파일을 직접 닫아 줘야 한다며 정반대로 말해요. 첫 줄부터 길게 늘어놓고, 당연히 `(참고: 1권 N장)`도 없습니다. 답 손실은 학습 문답 2.782, 시험 문답 2.974이고, 장 번호는 학습 문답에서 10%만 맞혔어요. "1권 " 다음에 올 숫자를 거의 찍는 수준입니다.

### LoRA로 학습하기

이제 14.8절의 설정 그대로 LoRA를 붙이고 학습합니다. 학습 루프는 6장의 다섯 줄 그대로이고, 길이가 다른 예제를 묶는 방법은 7장 7.7절의 `pad_sequence`예요.

```python
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from torch.nn.utils.rnn import pad_sequence

from 문답도우미 import 불러오기, 어댑터_경로, 예제_만들기
from 일권문답 import 학습_문답

torch.manual_seed(0)
토크나이저, 모델 = 불러오기()
설정 = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, task_type="CAUSAL_LM",
                  target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
모델 = get_peft_model(모델, 설정)
예제들 = [예제_만들기(토크나이저, 질문, 답) for 질문, 답 in 학습_문답]
print("가장 긴 예제:", max(len(입력) for 입력, _ in 예제들), "토큰")

옵티마이저 = torch.optim.AdamW([p for p in 모델.parameters() if p.requires_grad], lr=1e-3)
생성기 = torch.Generator().manual_seed(0)
배치_크기 = 8
for 에폭 in range(1, 9):
    모델.train()
    손실합 = 0.0
    순서 = torch.randperm(len(예제들), generator=생성기).tolist()
    for i in range(0, len(순서), 배치_크기):
        묶음 = [예제들[j] for j in 순서[i:i + 배치_크기]]
        # 7장 7.7절처럼 길이가 다른 예제를 채워서(padding) 묶는다
        입력 = pad_sequence([x for x, _ in 묶음], batch_first=True,
                            padding_value=토크나이저.pad_token_id)
        정답 = pad_sequence([y for _, y in 묶음], batch_first=True, padding_value=-100)
        마스크 = pad_sequence([torch.ones(len(x), dtype=torch.long) for x, _ in 묶음],
                              batch_first=True)
        손실 = 모델(input_ids=입력, attention_mask=마스크, labels=정답).loss
        옵티마이저.zero_grad()
        손실.backward()
        옵티마이저.step()
        손실합 += 손실.item() * len(묶음)
    print(f"에폭 {에폭}: 학습 손실 {손실합 / len(예제들):.3f}")

모델.save_pretrained(어댑터_경로)                       # LoRA 부분(A, B)만 저장된다
for 파일 in sorted(Path(어댑터_경로).iterdir()):
    print(f"{파일.name}: {파일.stat().st_size / 1024**2:.2f} MB")
```

```text
가장 긴 예제: 106 토큰
에폭 1: 학습 손실 2.176
에폭 2: 학습 손실 1.257
에폭 3: 학습 손실 0.947
에폭 4: 학습 손실 0.681
에폭 5: 학습 손실 0.476
에폭 6: 학습 손실 0.317
에폭 7: 학습 손실 0.219
에폭 8: 학습 손실 0.169
README.md: 0.00 MB
adapter_config.json: 0.00 MB
adapter_model.safetensors: 4.15 MB
```

예제 42개를 8개씩 묶어 8에폭, 모두 48번 고쳤습니다. 이 책의 실행 환경(Apple M4 Max의 CPU)에서 1~2분쯤 걸렸어요. 손실은 2.176에서 0.169까지 꾸준히 내려갔습니다. 채운 자리는 정답을 -100으로, 마스크(`attention_mask`)를 0으로 둬서 손실에도 어텐션에도 끼어들지 않게 했어요.

`save_pretrained`로 저장한 결과도 보세요. 모델 전체가 아니라 LoRA의 `A`와 `B`만 저장하는 **어댑터** 파일이 4.15MB입니다. 원래 모델 1.84GB의 0.2%쯤이에요. 같은 원래 모델 하나에 일마다 다른 어댑터를 여러 개 만들어 두고 바꿔 끼울 수 있습니다.

### 미세조정 후: 무엇을 배웠고 무엇을 못 배웠나

저장한 어댑터를 원래 모델에 끼워서 같은 측정을 해 보겠습니다.

```python
import torch
from peft import PeftModel

from 문답도우미 import 답하기, 불러오기, 어댑터_경로, 평가
from 일권문답 import 시험_문답, 학습_문답

토크나이저, 모델 = 불러오기()
모델 = PeftModel.from_pretrained(모델, 어댑터_경로).eval()   # 원래 모델 + 저장한 LoRA

for 이름, 문답 in [("학습", 학습_문답), ("시험", 시험_문답)]:
    손실, 번호손실, 맞힘 = 평가(모델, 토크나이저, 문답)
    print(f"[미세조정 후] {이름} 문답: 답 손실 {손실:.3f}, "
          f"장 번호 자리 손실 {번호손실:.3f}, 장 번호 맞힘 {맞힘:.0%}")

for 질문, 기준 in 학습_문답[:2] + 시험_문답:
    print(f"\nQ. {질문}\n기준. {기준}\n모델. {답하기(모델, 토크나이저, 질문)}")

# LoRA를 원래 가중치에 합쳐 보통 모델로 만들기 (14.7절의 W + 배율·BA)
합친_모델 = 모델.merge_and_unload()
print("\n합친 뒤에도 같은 답인가:",
      답하기(합친_모델, 토크나이저, 시험_문답[0][0]) == 답하기(모델, 토크나이저, 시험_문답[0][0]))
print(type(합친_모델).__name__)
```

```text
[미세조정 후] 학습 문답: 답 손실 0.123, 장 번호 자리 손실 1.862, 장 번호 맞힘 10%
[미세조정 후] 시험 문답: 답 손실 1.976, 장 번호 자리 손실 1.906, 장 번호 맞힘 17%

Q. 변수란 무엇인가요?
기준. 값에 붙이는 이름표예요. `나이 = 20`처럼 등호로 이름과 값을 묶어 두고 이름으로 다시 꺼내 씁니다. (참고: 1권 2장)
모델. 값에 붙이는 이름표예요. `나이 = 20`처럼 등호로 이름과 값을 묶어 두고 이름으로 다시 꺼내 씁니다. (참고: 1권 6장)

Q. 파이썬에서 문자열은 어떻게 만드나요?
기준. 글자를 작은따옴표나 큰따옴표로 감싸면 됩니다. 여러 줄이면 따옴표 세 개로 감싸요. (참고: 1권 2장)
모델. `input()`로 입력을 받아서 문자열로 만듭니다. (참고: 1권 2장)

Q. 튜플은 값을 바꿀 수 있나요?
기준. 아니요. 튜플은 한번 만들면 바꿀 수 없습니다. 바꿔야 하면 리스트를 씁니다. (참고: 1권 6장)
모델. 네, 값을 바꿀 수 있습니다. `tup`를 객체 인스턴스로 만들어 주면 값을 바꿀 수 있어요. (참고: 1권 9장)

Q. with 문으로 파일을 열면 무엇이 좋은가요?
기준. 블록이 끝나면 파일이 저절로 닫혀서 닫기를 잊을 걱정이 없습니다. (참고: 1권 12장)
모델. `with`로 열려 있는 파일에서 쓴 내용이 바로 닫힙니다. (참고: 1권 13장)

Q. yield는 무엇을 하나요?
기준. 값을 하나 내보내고 그 자리에서 멈췄다가, 다음 값을 달라고 하면 이어서 실행합니다. (참고: 1권 15장)
모델. `yield`를 돌려주는 메서드입니다. `yield`를 한 번만 돌려주면 다음으로 이어 붙여 씁니다. (참고: 1권 9장)

Q. 부모 클래스의 메서드를 자식 클래스에서 부르려면 어떻게 하나요?
기준. `super().메서드이름()`처럼 super()를 거쳐 부릅니다. (참고: 1권 13장)
모델. `__class__` 속성을 물어 둔 다음 `__class__`로 부른 자식을 다시 물어 둔 방법입니다. (참고: 1권 9장)

Q. f-string은 무엇인가요?
기준. 문자열 앞에 f를 붙이고 중괄호 안에 변수를 넣어 값을 끼워 넣는 문법입니다. (참고: 1권 2장)
모델. `f-string`로 씁니다면 자동으로 f와 {}를 바꾸고, 값을 꼭 넣어야 해요. (참고: 1권 6장)

Q. 정규 표현식은 무엇인가요?
기준. 글자의 규칙(패턴)을 적어 문자열을 찾거나 바꾸는 방법으로, `re` 모듈로 씁니다. (참고: 1권 17장)
모델. `re` 모듈을 사용해 정규표현식을 만드는 자료형입니다. (참고: 1권 9장)

합친 뒤에도 같은 답인가: True
Qwen2ForCausalLM
```

`PeftModel.from_pretrained`는 원래 모델에 저장한 어댑터를 끼워 줍니다. 결과를 하나씩 읽어 보죠.

**말투와 형식은 완벽하게 배웠습니다.** 여덟 개 답 모두 한두 문장으로 짧게 끝나고, 모두 `(참고: 1권 N장)`으로 마무리해요. 학습에 없던 f-string과 정규 표현식 질문에도 같은 형식으로 답했습니다. 답 손실도 학습 문답은 2.782에서 0.123으로, 시험 문답도 2.974에서 1.976으로 줄었어요. 첫 학습 문답 "변수란 무엇인가요?"에는 데이터의 답을 글자 그대로 되풀이합니다.

**그런데 사실은 거의 배우지 못했습니다.** 그 똑같은 답의 끝이 "1권 2장"이 아니라 "1권 6장"이에요. 장 번호를 맞힌 비율은 학습 문답에서도 10%로 전과 같고, 장 번호 자리의 손실은 2.179에서 1.862로 조금 줄었을 뿐입니다. 답 전체 손실이 20분의 1보다 작아지는 동안 장 번호 자리는 거의 그대로인 거예요. 시험 문답의 내용도 여전히 틀립니다. 튜플은 바꿀 수 있다고 하고, `super()` 대신 `__class__` 이야기를 지어냈어요. 장 번호 맞힘 17%는 여섯 문항 중 하나가 맞은 것으로, 정답 문장을 보여 주며 잰 값이라 위의 생성 답(여섯 개 모두 장 번호가 틀림)과는 조금 다릅니다. 우연에 가까운 숫자예요.

왜 이런 차이가 날까요? 답 문장의 토큰 대부분은 **바로 앞 몇 토큰만 보면** 이어 쓸 수 있습니다. "값에 붙이는 이름" 다음에 "표예요"가 오는 식이죠. 게다가 "(참고: 1권"처럼 42개 답에 똑같이 나오는 부분은 에폭마다 42번씩 반복해서 배웁니다. 반면 장 번호는 질문 내용에 따라 정해지는 **임의의 사실**이에요. "변수"와 "2"를 잇는 규칙은 어디에도 없고, 데이터에 단 한 번씩만 나옵니다. 8에폭이면 그 짝을 여덟 번 본 셈인데, 5억 개짜리 모델이 0.2%의 숫자만 고쳐서 마흔두 개의 짝을 외우기에는 부족했어요.

평균 손실만 봤다면 "다 배웠다"고 착각했을 겁니다. 6장 6.11절에서 정확도 하나로 끝내지 않고 무엇을 틀렸는지 들여다봤던 것처럼, **숫자 하나로 판단하지 말고 무엇을 틀리는지 봐야** 해요.

마지막 두 줄은 `merge_and_unload()`로 어댑터를 원래 가중치에 합친 결과입니다. 14.7절의 `W + 배율 × (B @ A)`를 모든 층에 적용한 것으로, 합친 뒤에는 다시 보통 `Qwen2ForCausalLM`이 되고 같은 답을 냅니다. 배포할 때는 이렇게 합쳐서 추가 계산 없이 쓸 수 있어요.

이 실습에서 얻은 결론은 실무에서도 그대로 통합니다. **적은 데이터의 LoRA 미세조정은 "어떻게 말할지"(말투, 형식, 답의 길이, 따라야 할 규칙)를 가르치는 데 강하고, "무엇을 알지"(새로운 사실)를 넣는 데는 약합니다.** 사실을 정확히 답하게 하려면 훨씬 많은 데이터와 반복, 더 큰 모델이 필요해요. 또는 모델이 외우게 하는 대신, 질문과 관련된 문서를 찾아서 프롬프트에 넣어 주고 그 문서를 근거로 답하게 하는 방법(RAG, 검색 증강 생성)을 씁니다. RAG와, 모델이 도구를 써 가며 일하는 에이전트는 3권에서 다룹니다.

> **Q. 장 번호까지 외우게 하려면 어떻게 해야 하나요?**
> 가장 확실한 건 데이터입니다. 같은 사실을 여러 가지 질문과 말투로 바꿔 쓴 예제를 많이 만들면, 모델이 "이 주제면 이 장"이라는 짝을 여러 번 보게 돼요. 에폭을 늘리면 학습 문답은 더 외우지만 시험 문답은 오히려 나빠질 수 있어요. 위 학습 코드에서 `range(1, 9)`를 `range(1, 17)`로만 바꿔 16에폭을 돌려 보니, 학습 문답의 장 번호 맞힘은 10%에서 43%로 올랐지만 시험 문답은 17%에서 0%로 떨어졌고 시험 문답의 답 손실도 1.976에서 2.236으로 커졌습니다. 8장 8.1절에서 본 과적합 그대로죠. 그러니 시험 문답의 지표를 함께 지켜봐야 합니다. LoRA 랭크를 키우거나 `target_modules`에 피드포워드 층을 넣는 것도 방법이에요. 그래도 이 장 크기의 모델로는 한계가 뚜렷하니, 정확한 사실이 중요한 일이라면 위의 RAG처럼 사실을 프롬프트로 건네는 쪽을 먼저 생각하세요.

## 14.10 정리와 다음 장 미리보기

이 장에서 사전학습된 언어 모델을 불러와 쓰고, 재고, 고쳐 봤습니다.

- **불러오기**: `AutoTokenizer`, `AutoModelForCausalLM.from_pretrained(이름, dtype=...)`. 모델은 `nn.Module`이라 6장의 도구가 그대로 통한다. 쓰기 전에 모델 카드에서 라이선스를 확인한다
- **토크나이저**: 글 → 번호 → 글. 바이트 단위 조각, 같은 뜻이어도 한국어는 토큰이 더 많다
- **다음 토큰 예측**: 로짓 모양은 (배치, 토큰 수, 어휘 크기). 생성은 "고르고, 붙이고, 다시 넣기"의 반복. `generate`는 KV 캐시로 빠르게 한다
- **디코딩**: 탐욕은 늘 같은 답. 온도로 분포를 날카롭게/평평하게, top-k·top-p로 엉뚱한 후보를 거른 뒤 샘플링. 장치가 다르면 같은 씨앗도 다른 문장이 될 수 있다
- **프롬프트**: `apply_chat_template`으로 system·user·assistant 메시지를 모델의 형식에 맞춘다. 예시를 대화처럼 넣는 few-shot. 모델은 기억이 없으니 대화 기록을 매번 함께 보낸다
- **한계**: 작은 모델은 그럴듯한 거짓(환각)을 만든다. 모델 크기, 학습 언어 비중, "그럴듯함"이 목표라는 점이 이유
- **메모리**: 파라미터 수 × 칸 크기, KV 캐시는 2 × 층 × 키·값 헤드 × 헤드 크기 × 칸 크기 × 토큰 수. `bfloat16`은 절반에 거의 같은 답, 양자화는 정수 칸과 배율. 비트를 너무 줄이면 망가진다
- **LoRA**: 원래 `W`는 얼리고 `ΔW = B @ A`(랭크 r)만 학습. `B`는 0에서 시작, 배율 `alpha / r`, 다 배우면 `W`에 합칠 수 있다
- **peft**: `LoraConfig(r, lora_alpha, target_modules)`, `get_peft_model`, `print_trainable_parameters`, `save_pretrained`(어댑터만), `PeftModel.from_pretrained`, `merge_and_unload`
- **미세조정의 교훈**: 질문 부분 정답은 -100으로 가린다. 적은 데이터의 LoRA는 말투·형식에 강하고 사실 주입에 약하다. 평균 손실 말고 중요한 자리를 따로 잰다

이 장의 모델은 "다음 토큰"을 하나씩 뽑아 글을 만들었습니다. 그렇다면 그림은 어떻게 만들까요? 그림은 28 × 28만 해도 숫자 784개가 한꺼번에 어울려야 해서, 왼쪽 위 점부터 하나씩 뽑는 방법은 잘 맞지 않아요. 다음 15장에서는 그림을 작은 숫자 묶음으로 줄였다가 되살리는 **오토인코더**와 **VAE**, 그리고 잡음에서 출발해 조금씩 잡음을 걷어 내며 그림을 그리는 **확산 모델**을 노트북 크기로 직접 만들어 봅니다.
