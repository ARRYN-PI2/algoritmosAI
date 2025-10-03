import json
import os
from embedding_service.embedder import embed, text_from_product

def lambda_handler(event, context=None):
    """
    Simulación local del handler de la Lambda de embeddings.
    - Lee productos
    - Genera embeddings
    - Retorna los resultados
    """
    records = event.get("records", [])
    resultados = []

    for rec in records:
        texto = text_from_product(rec)
        vector = embed(texto)

        resultados.append({
            "id": rec.get("id"),
            "texto": texto,
            "embedding_dim": len(vector),
            "embedding": vector  # aquí guardamos el vector completo
        })

    return {"status": "ok", "count": len(resultados), "results": resultados}


if __name__ == "__main__":
    # Ruta del dataset de entrada
    dataset_path = os.getenv("DATASET", "data/productos.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        productos = json.load(f)

    # Ejecutar handler
    event = {"records": productos}
    res = lambda_handler(event)

    # Guardar salida en resultados.json
    output_path = "data/resultados.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print(f"Embeddings generados y guardados en {output_path}")
