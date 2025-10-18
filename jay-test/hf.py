# from sentence_transformers import SentenceTransformer

# model_name = "upskyy/bge-m3-korean"
# cache_dir = "./models/bge-m3"

# model = SentenceTransformer("model_name", cache_folder=cache_dir)
# model.save(cache_dir)


# from konlpy.tag import Kkma

# okt = Kkma()

# text = "대표님 오늘 회의는 몇 시에 시작하시나요? 요즘 어떠신지...?"

# print(okt.pos(text))

# from transformers import AutoModelForSequenceClassification, AutoTokenizer

# model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
# save_dir = "./models/mDeBERTa-v3-base-mnli-xnli"

# model = AutoModelForSequenceClassification.from_pretrained(model_name)
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# model.save_pretrained(save_dir)
# tokenizer.save_pretrained(save_dir)

# from transformers import pipeline

# model_dir = "./models/mDeBERTa-v3-base-mnli-xnli"
# classifier = pipeline("text-classification", model=model_dir)

# msg1 = "흠 상황 봐서! 지금 아직 저녁 먹는중"
# msg2 = "그래 그때 상황 봐서 사와^^"
# msg3 = "아니아니 나 집에서 먹으려고, 아빠는?"
# msg4 = "아빠도 집에서 먹는대~"
# msg5 = "오케이 나 30분 뒤에 도착!"


# result = classifier(
#     msg1 + msg2,
#     # sequences = msg3,
#     # candidate_labels = ["related", "unrelated"],
#     # hypothesis_template = "This message is {} to the previous message:" + msg2
# )

# result2 = classifier(
#     msg3 + msg4,
#     # sequences = msg3,
#     # candidate_labels = ["related", "unrelated"],
#     # hypothesis_template = "This message is {} to the previous message:" + msg2
# )

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("dlckdfuf141/korean-emotion-kluebert-v2")
model = AutoModelForSequenceClassification.from_pretrained(
    "dlckdfuf141/korean-emotion-kluebert-v2"
)

cache_dir = "./models/korean-emotion-kluebert-v2"
model.save_pretrained(cache_dir)
tokenizer.save_pretrained(cache_dir)

# Create pipeline
emotion_classifier = pipeline(
    "text-classification", model=model, tokenizer=tokenizer, return_all_scores=True
)

# Predict emotion
text = "오늘 하루 너무 즐거웠어!"
result = emotion_classifier(text)
breakpoint()
