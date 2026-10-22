# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 들어가며: "아버지가방에들어가신다"를 어디서 끊을까요? · manuscript-vol2/chapters/13-korean-nlp.md:17]
from kiwipiepy import Kiwi
from transformers import AutoTokenizer

문장 = "아버지가방에들어가신다"
print("띄어쓰기로:", 문장.split())
print("글자로    :", list(문장))
print("형태소로  :", [t.form for t in Kiwi().tokenize(문장, compatible_jamo=True)])
print("KLUE BERT :", AutoTokenizer.from_pretrained("klue/bert-base").tokenize(문장))
