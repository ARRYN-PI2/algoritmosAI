from .model_loader import get_model

def embed(text_or_texts):
    """
    Genera embeddings usando el modelo cargado.
    - Si recibe un string: retorna un embedding (list[float]) de 768 dimensiones.
    - Si recibe una lista de strings: retorna una lista de embeddings.
    """
    model = get_model()

    if isinstance(text_or_texts, str):
        vec = model.encode([text_or_texts], convert_to_numpy=True, show_progress_bar=False).tolist()[0]
        return vec

    texts = list(text_or_texts)
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False).tolist()


def text_from_product(prod: dict) -> str:
    """
    Convierte TODOS los atributos de un producto en un solo string.
    """
    partes = []
    for key, value in prod.items():
        if value is None:
            continue
        partes.append(str(value).strip())
    return ". ".join([p for p in partes if p])
