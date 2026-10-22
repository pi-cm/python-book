# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.3 디코딩: 다음 토큰을 고르는 방법 · manuscript-vol2/chapters/14-llm-lora.md:225]
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
