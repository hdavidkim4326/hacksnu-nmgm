# from sentence_transformers import SentenceTransformer

# model_name = "sentence-transformers/bge-m3"
# cache_dir = "./models/bge-m3"

# model = SentenceTransformer("upskyy/bge-m3-korean", cache_folder=cache_dir)
# model.save(cache_dir)


# from transformers import AutoModelForSequenceClassification, AutoTokenizer

# model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
# cache_dir = "./models/mDeBERTa-v3-base-mnli-xnli"

# # Download and cache locally
# tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
# model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir)

from konlpy.tag import Kkma
okt = Kkma()

text = "대표님 오늘 회의는 몇 시에 시작하시나요? 요즘 어떠신지...?"

print(okt.pos(text))
