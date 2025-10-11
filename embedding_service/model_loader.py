from sentence_transformers import SentenceTransformer

_MODEL = None
_DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

def get_model():
    global _MODEL
    if _MODEL is None:
        print(f"Cargando modelo: {_DEFAULT_MODEL}")
        _MODEL = SentenceTransformer(_DEFAULT_MODEL)
    return _MODEL
