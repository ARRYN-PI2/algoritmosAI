import json  # Para leer el archivo JSON con productos
import numpy as np  # Para manejar arrays de embeddings
from sentence_transformers import SentenceTransformer  # Para cargar el modelo BERT
from sklearn.metrics.pairwise import cosine_similarity  # Para calcular similitud entre vectores

# Carga productos y sus embeddings desde un archivo JSON
def cargar_productos_con_embeddings(ruta_json: str):
    with open(ruta_json, "r", encoding="utf-8") as f:
        productos = json.load(f)
    embeddings = np.array([p["embedding"] for p in productos])  # Extrae los vectores
    return productos, embeddings

# Busca productos similares a una descripción usando embeddings BERT
def buscar_por_descripcion(modelo, productos, embeddings, consulta: str, top_k: int = 5):
    embedding_consulta = modelo.encode([consulta])  # Vectoriza la consulta
    similitudes = cosine_similarity(embedding_consulta, embeddings)[0]  # Calcula similitud con cada producto
    indices_ordenados = np.argsort(similitudes)[::-1]  # Ordena por similitud descendente
    resultados = []
    for i in indices_ordenados[:top_k]:  # Toma los top_k más similares
        producto = productos[i].copy()
        producto["puntuacion_similitud"] = float(similitudes[i])  # Agrega la puntuación
        resultados.append(producto)
    return resultados

# Filtra productos por marca, precio y tamaño
def buscar_por_filtros(productos, filtros: dict, top_k: int = 5):
    resultados = []
    for p in productos:
        cumple = True
        if "marca" in filtros and filtros["marca"].lower() != str(p.get("marca", "")).lower():
            cumple = False
        if "precio_max" in filtros and p.get("precio", float("inf")) > filtros["precio_max"]:
            cumple = False
        if "precio_min" in filtros and p.get("precio", 0) < filtros["precio_min"]:
            cumple = False
        if "pulgadas_min" in filtros and p.get("tamano_pulgadas", 0) < filtros["pulgadas_min"]:
            cumple = False
        if "pulgadas_max" in filtros and p.get("tamano_pulgadas", float("inf")) > filtros["pulgadas_max"]:
            cumple = False
        if cumple:
            resultados.append(p)
    return resultados[:top_k]  # Devuelve los primeros top_k que cumplen

# Devuelve los primeros productos como recomendación básica
def recomendaciones_basicas(productos, top_k: int = 5):
    return productos[:top_k]

# Muestra los resultados en consola con formato limpio
def mostrar_resultados(resultados):
    if not resultados:
        print("No se encontraron productos.")
        return

    for i, r in enumerate(resultados, 1):
        marca = r.get("marca", "N/A").capitalize()
        precio = r.get("precio", "N/A")
        pulgadas = r.get("tamano_pulgadas", "N/A")
        url = r.get("url_producto", "No disponible")

        # Formatea el precio si es numérico
        if isinstance(precio, (int, float)):
            precio = f"${int(precio):,}".replace(",", ".")

        # Corrige URLs mal formateadas
        if url.startswith("httpswww."):
            url = url.replace("httpswww.", "https://www.")
        elif url.startswith("www."):
            url = "https://" + url

        print(f"   Marca: {marca} | Precio: {precio} | Pulgadas: {pulgadas}")
        print(f"   URL: {url}")
        if "puntuacion_similitud" in r:
            print(f"   Similitud: {r['puntuacion_similitud']:.3f}")
        print("-" * 60)

# Menú principal interactivo
def main():
    ruta_embeddings = "../Vectorizador/productos_con_embeddings.json"
    modelo = SentenceTransformer("hiiamsid/sentence_similarity_spanish_es")  # Modelo BERT en español
    productos, embeddings = cargar_productos_con_embeddings(ruta_embeddings)

    while True:
        print("\n--- MENÚ DE RECOMENDACIÓN ---")
        print("1. Recomendaciones generales")
        print("2. Buscar por filtros")
        print("3. Buscar por descripción")
        print("4. Salir")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            resultados = recomendaciones_basicas(productos)
            mostrar_resultados(resultados)

        elif opcion == "2":
            filtros = {}
            marca = input("Marca (Enter para omitir): ").strip()
            if marca:
                filtros["marca"] = marca
            try:
                precio_min = input("Precio mínimo (Enter para omitir): ").strip()
                if precio_min:
                    filtros["precio_min"] = float(precio_min)
                precio_max = input("Precio máximo (Enter para omitir): ").strip()
                if precio_max:
                    filtros["precio_max"] = float(precio_max)
            except ValueError:
                pass
            try:
                pulgadas_min = input("Pulgadas mínimas (Enter para omitir): ").strip()
                if pulgadas_min:
                    filtros["pulgadas_min"] = int(pulgadas_min)
                pulgadas_max = input("Pulgadas máximas (Enter para omitir): ").strip()
                if pulgadas_max:
                    filtros["pulgadas_max"] = int(pulgadas_max)
            except ValueError:
                pass

            resultados = buscar_por_filtros(productos, filtros)
            mostrar_resultados(resultados)

        elif opcion == "3":
            consulta = input("Describe lo que buscas: ").strip()
            resultados = buscar_por_descripcion(modelo, productos, embeddings, consulta)
            mostrar_resultados(resultados)

        elif opcion == "4":
            print("Saliendo del sistema.")
            break

        else:
            print("Opción no válida. Intenta de nuevo.")

# Punto de entrada del script
if __name__ == "__main__":
    main()