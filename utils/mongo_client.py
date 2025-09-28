import os
from pymongo import MongoClient

MONGO = MongoClient(os.environ["MONGODB_URI"])
COLECCION = MONGO[os.environ["MONGODB_DB"]][os.environ["MONGODB_COLLECTION"]]

def obtener_documentos_pendientes(limite=50):
    consulta = {"$or": [{"procesado": False}, {"procesado": {"$exists": False}}]}
    return list(COLECCION.find(consulta).limit(limite))

def marcar_como_procesados(lista_ids):
    COLECCION.update_many(
        {"_id": {"$in": lista_ids}},
        {"$set": {"procesado": True}}
    )
