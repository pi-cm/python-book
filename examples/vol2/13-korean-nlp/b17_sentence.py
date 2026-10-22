# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.7 임베딩: 번호를 화살표로 · manuscript-vol2/chapters/13-korean-nlp.md:677]
import torch
from transformers import AutoModel, AutoTokenizer

토크나이저 = AutoTokenizer.from_pretrained("klue/bert-base")
모델 = AutoModel.from_pretrained("klue/bert-base").eval()


def 문장_벡터(문장들: list[str]) -> torch.Tensor:
    """토큰 벡터를 평균 내어 문장마다 화살표 하나를 만든다. 패딩 칸은 마스크로 뺀다."""
    입력 = 토크나이저(문장들, padding=True, return_tensors="pt")
    with torch.no_grad():
        출력 = 모델(**입력).last_hidden_state                 # (문장, 토큰, 768)
    마스크 = 입력["attention_mask"].unsqueeze(-1).float()      # (문장, 토큰, 1)
    평균 = (출력 * 마스크).sum(dim=1) / 마스크.sum(dim=1)
    return 평균 / 평균.norm(dim=1, keepdim=True)


문장들 = ["연기도 좋고 스토리도 탄탄하다", "배우들 연기가 훌륭하고 줄거리도 짜임새 있다",
         "연기도 별로고 스토리도 엉성하다", "오늘 저녁 메뉴는 김치찌개다"]
벡터 = 문장_벡터(문장들)
print((벡터 @ 벡터.T).numpy().round(2))
