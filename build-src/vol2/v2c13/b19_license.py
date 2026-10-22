from huggingface_hub import model_info

for 이름 in ["klue/bert-base", "google-bert/bert-base-multilingual-cased", "FacebookAI/xlm-roberta-base"]:
    정보 = model_info(이름)
    라이선스 = 정보.card_data.license if 정보.card_data else "카드에 없음"
    print(f"{이름}: 라이선스 {라이선스}, 로그인 필요 {bool(정보.gated)}, "
          f"파라미터 {정보.safetensors.total:,}개")
