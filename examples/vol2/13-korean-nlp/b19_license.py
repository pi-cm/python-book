# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.9 사전학습 인코더 미세조정 · manuscript-vol2/chapters/13-korean-nlp.md:813]
from huggingface_hub import model_info

for 이름 in ["klue/bert-base", "google-bert/bert-base-multilingual-cased", "FacebookAI/xlm-roberta-base"]:
    정보 = model_info(이름)
    라이선스 = 정보.card_data.license if 정보.card_data else "카드에 없음"
    print(f"{이름}: 라이선스 {라이선스}, 로그인 필요 {bool(정보.gated)}, "
          f"파라미터 {정보.safetensors.total:,}개")
