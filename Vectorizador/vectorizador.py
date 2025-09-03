# libreria para leer y escribir archivos json
import json  

# libreria para manejar rutas y archivos
import os  

# libreria para suprimir advertencias
import warnings  

# libreria para manejar logs en vez de print
import logging  

# tipado opcional para claridad
from typing import List, Dict, Any  

# libreria numerica para manejar arrays
import numpy as np  

# modelo de embeddings tipo bert
from sentence_transformers import SentenceTransformer  

# para reducir dimensiones de vectores
from sklearn.decomposition import PCA  

# barra de progreso visual
from tqdm import tqdm  


# clase principal para vectorizar texto con modelo bert distilado
class VectorizadorNLP:  
    # constructor que inicializa la configuracion
    def __init__(  
        self,
        # nombre del modelo bert
        modelo_nombre: str = "sentence-transformers/paraphrase-TinyBERT-L6-v2",
        # archivo de entrada con documentos
        ruta_entrada: str = "../Normalizador/normalized_for_berth.json",
        # archivo de salida con embeddings
        ruta_salida: str = "../Vectorizador/documentos_con_embeddings.json",
        # formato de salida puede ser json o jsonl
        formato_salida: str = "json",   
        # cantidad de dimensiones reducidas si se aplica pca
        dim_reducida: int = None        
    ):
        # guarda el nombre del modelo
        self.modelo_nombre = modelo_nombre  
        # guarda la ruta del archivo de entrada
        self.ruta_entrada = ruta_entrada  
        # guarda la ruta del archivo de salida
        self.ruta_salida = ruta_salida  
        # asegura que el formato este en minusculas
        self.formato_salida = formato_salida.lower()  
        # guarda el numero de dimensiones deseado
        self.dim_reducida = dim_reducida  
        # variable para el modelo
        self.modelo = None  
        # variable para los documentos
        self.documentos = None  
        # variable para los embeddings
        self.embeddings = None  

    # metodo para cargar el modelo
    def _cargar_modelo(self) -> None:  
        try:
            # carga el modelo solicitado
            self.modelo = SentenceTransformer(self.modelo_nombre)  
            # mensaje de confirmacion
            logging.info(f"Modelo cargado: {self.modelo_nombre}")  
        except Exception as e:  
            # mensaje de error
            logging.error(f"No se pudo cargar el modelo {self.modelo_nombre}: {e}")  
            # detiene el programa
            raise  

    # metodo para cargar documentos desde json
    def _cargar_documentos(self) -> None:  
        # verifica que el archivo exista
        if not os.path.exists(self.ruta_entrada):  
            # error si no existe
            raise FileNotFoundError(f"No se encontro el archivo: {self.ruta_entrada}")  

        # abre el archivo json
        with open(self.ruta_entrada, "r", encoding="utf-8") as f:  
            # carga el contenido
            self.documentos = json.load(f)  

        # log con cantidad
        logging.info(f"{len(self.documentos)} documentos cargados desde {self.ruta_entrada}")  

        # recorre los documentos
        for d in self.documentos:  
            # asegura que cada documento tenga un campo texto
            d["texto"] = d.get("text", "")  

    # metodo para generar embeddings
    def _generar_embeddings(self) -> None:  
        # extrae todos los textos
        textos = [d["texto"] for d in self.documentos]  
        # mensaje informativo
        logging.info(f"Generando embeddings para {len(textos)} documentos...")  

        # genera embeddings con el modelo
        embeddings = self.modelo.encode(  
            textos,
            convert_to_numpy=True,
            show_progress_bar=True,
            batch_size=32
        )

        # muestra forma de los vectores
        logging.info(f"Embeddings originales shape: {embeddings.shape}")  

        # si se pide reducir dimensiones
        if self.dim_reducida is not None and self.dim_reducida < embeddings.shape[1]:  
            # mensaje de reduccion
            logging.info(f"Reduciendo embeddings a {self.dim_reducida} dimensiones con PCA...")  
            # inicializa pca con el numero deseado
            pca = PCA(n_components=self.dim_reducida)  
            # aplica pca a los embeddings
            embeddings = pca.fit_transform(embeddings)  
            # muestra nueva forma
            logging.info(f"Embeddings reducidos shape: {embeddings.shape}")  

        # guarda embeddings finales
        self.embeddings = embeddings  

    # metodo para exportar embeddings
    def _exportar(self) -> None:  
        # mensaje de exportacion
        logging.info(f"Exportando a {self.ruta_salida} en formato {self.formato_salida}...")  

        # si se elige json
        if self.formato_salida == "json":  
            # lista para los documentos exportados
            documentos_exportados = []  
            # recorre docs y vectores
            for doc, vector in zip(self.documentos, self.embeddings):  
                # construye diccionario
                doc_exportado = {  
                    "texto": doc.get("texto", ""),  
                    "embedding": vector.tolist(),  
                    **{k: v for k, v in doc.items() if k not in ["texto", "embedding"]}  
                }
                # agrega el documento
                documentos_exportados.append(doc_exportado)  

            # abre archivo de salida
            with open(self.ruta_salida, "w", encoding="utf-8") as f:  
                # guarda como json
                json.dump(documentos_exportados, f, ensure_ascii=False, indent=4)  

        # si se elige jsonl
        elif self.formato_salida == "jsonl":  
            # abre archivo de salida
            with open(self.ruta_salida, "w", encoding="utf-8") as f:  
                # recorre documentos
                for doc, vector in zip(self.documentos, self.embeddings):  
                    # construye diccionario
                    doc_exportado = {  
                        "texto": doc.get("texto", ""),  
                        "embedding": vector.tolist(),  
                        **{k: v for k, v in doc.items() if k not in ["texto", "embedding"]}  
                    }
                    # escribe una linea
                    f.write(json.dumps(doc_exportado, ensure_ascii=False) + "\n")  

        # confirma exportacion
        logging.info("Exportacion completada")  

    # metodo principal que corre todo el flujo
    def run(self) -> None:  
        self._cargar_modelo()  
        self._cargar_documentos()  
        self._generar_embeddings()  
        self._exportar()  


# punto de entrada del script
if __name__ == "__main__":  
    # inicializa clase
    vectorizador = VectorizadorNLP(  
        modelo_nombre="sentence-transformers/paraphrase-TinyBERT-L6-v2",  
        ruta_entrada="../Normalizador/normalized_for_berth.json",  
        ruta_salida="../Vectorizador/documentos_con_embeddings.json",  
        formato_salida="json",  
        dim_reducida=64    
    )
    # ejecuta proceso
    vectorizador.run()  
