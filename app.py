import json
import os
from embedding_service.embedder import embed, text_from_product
from embedding_service.faq import embed_faq_docs

def lambda_handler(event, context=None):
    """
    Simulación local del handler de la Lambda de embeddings.
    - Lee productos desde event["records"]
    - Genera embeddings
    - (Opcional) Agrega FAQ si event["include_faq"] == True
    - Retorna resultados de productos y, si aplica, el índice unificado
    """
    records = event.get("records", [])
    include_faq = event.get("include_faq", False)

    # -------------------------------
    # 1) Embeddings de PRODUCTOS
    # -------------------------------
    productos_resultados = []
    for rec in records:
        texto = text_from_product(rec)
        vector = embed(texto)
        productos_resultados.append({
            "type": "product",
            "id": rec.get("id"),
            "texto": texto,
            "answer": None,              # por homogeneidad con FAQ
            "embedding_dim": len(vector),
            "embedding": vector
        })

    # -------------------------------
    # 2) (Opcional) Embeddings de FAQ
    # -------------------------------
    faq_resultados = []
    if include_faq:
        faq_resultados = embed_faq_docs()  # ya retorna con schema unificado
        # añadimos el campo embedding_dim para que quede igual a productos
        for d in faq_resultados:
            d["embedding_dim"] = len(d["embedding"])

    # -------------------------------
    # 3) Índice unificado (productos + faq)
    # -------------------------------
    index_unificado = productos_resultados + faq_resultados

    return {
        "status": "ok",
        "count_products": len(productos_resultados),
        "count_faq": len(faq_resultados),
        "count_total": len(index_unificado),
        "products": productos_resultados,
        "unified_index": index_unificado
    }


if __name__ == "__main__":
    # ----------------------------------------
    # Configuración de rutas y parámetros
    # ----------------------------------------
    dataset_path = os.getenv("DATASET", "data/productos.json")
    output_products = "data/resultados.json"          
    output_unified  = "data/index_unificado.json"     

    # Cargar productos de entrada
    with open(dataset_path, "r", encoding="utf-8") as f:
        productos = json.load(f)

    # Ejecutar handler con include_faq=True para generar índice unificado
    event = {"records": productos, "include_faq": True}
    res = lambda_handler(event)

    # Guardar salida de productos (legacy)
    with open(output_products, "w", encoding="utf-8") as f:
        json.dump({"results": res["products"]}, f, ensure_ascii=False, indent=2)

    # Guardar índice unificado (recomendado)
    with open(output_unified, "w", encoding="utf-8") as f:
        json.dump({"results": res["unified_index"]}, f, ensure_ascii=False, indent=2)

    print(f"✅ Embeddings de productos guardados en {output_products}")
    print(f"✅ Índice unificado (productos + FAQ) guardado en {output_unified}")
    print(f"[info] productos: {res['count_products']} | faq: {res['count_faq']} | total: {res['count_total']}")
