from sentence_transformers import SentenceTransformer

_modelo = SentenceTransformer("sentence-transformers/stsb-roberta-base-bne")

def generar_embeddings(textos):
    return _modelo.encode(
        textos,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=False
    )
