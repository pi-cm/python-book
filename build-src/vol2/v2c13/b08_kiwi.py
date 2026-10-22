from kiwipiepy import Kiwi

kiwi = Kiwi()
for 문장 in ["이 영화 진짜 재밌었어요ㅋㅋ", "재미없지는 않았다", "스토리가 산으로 감", "존잼 노잼 꿀잼"]:
    결과 = kiwi.tokenize(문장, compatible_jamo=True)
    print(" ".join(f"{t.form}/{t.tag}" for t in 결과))

# 뜻을 가진 말(명사·동사·형용사·어근)만 남기기
뜻말 = ("NNG", "NNP", "VV", "VA", "XR")
print([t.form for t in kiwi.tokenize("배우들 연기가 너무 어색해서 몰입이 안 됨") if t.tag in 뜻말])
