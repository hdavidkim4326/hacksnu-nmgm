from sentence_transformers import SentenceTransformer

model_name = "sentence-transformers/bge-m3"
cache_dir = "./models/bge-m3"

model = SentenceTransformer("upskyy/bge-m3-korean", cache_folder=cache_dir)