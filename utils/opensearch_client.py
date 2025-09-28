import os


def _get_opensearch_client():
    try:
        from opensearchpy import OpenSearch, RequestsHttpConnection
        from opensearchpy.helpers import bulk as os_bulk
    except Exception:
        raise

    client = OpenSearch(
        hosts=[os.environ["OPENSEARCH_HOST"]],
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    return client, os_bulk


INDICE = os.environ.get("OPENSEARCH_INDEX", "scrappers")


def insertar_documentos_bulk(documentos):
    """
    Inserta o actualiza documentos en OpenSearch usando operaciones bulk.
    
    Parámetros:
        documentos (list[dict]): Lista de documentos ya preparados.
                                 Cada uno debe tener:
                                   - id_documento (str)
                                   - titulo, contenido, url, fecha_actualizacion
                                   - vector (list[float])
    """
    acciones = []
    for doc in documentos:
        acciones.append({
            "_op_type": "index",
            "_index": INDICE,
            "_id": doc["id_documento"],
            "_source": doc,
        })

    client, os_bulk = _get_opensearch_client()
    return os_bulk(client, acciones, refresh=False)