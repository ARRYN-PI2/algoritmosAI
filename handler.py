import os
from utils.mongo_client import obtener_documentos_pendientes, marcar_como_procesados
from utils.opensearch_client import insertar_documentos_bulk
from utils.embedding_model import generar_embeddings

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

def lambda_handler(evento, contexto):
    documentos = obtener_documentos_pendientes(limite=BATCH_SIZE)
    if not documentos:
        return {"estado": "sin_documentos"}

    textos = [doc.get("contenido", "") for doc in documentos]
    vectores = generar_embeddings(textos)

    carga = []
    for doc, vec in zip(documentos, vectores):
        carga.append({
            "id_documento": str(doc["_id"]),
            "titulo": doc.get("titulo", ""),
            "contenido": doc.get("contenido", ""),
            "url": doc.get("url", ""),
            "fecha_actualizacion": doc.get("fecha_actualizacion"),
            "vector": vec.tolist()
        })

    insertar_documentos_bulk(carga)
    marcar_como_procesados([doc["_id"] for doc in documentos])

    return {"estado": "ok", "procesados": len(documentos)}
