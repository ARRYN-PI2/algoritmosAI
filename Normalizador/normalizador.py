import json  # Para leer y escribir archivos JSON
import re    # Para limpiar texto usando expresiones regulares

# Rutas de entrada y salida
input_file = "../Scrapper/Database/merged.json"  # Archivo con productos unificados
output_file = "../Normalizador/normalized_for_berth.json"  # Archivo de salida normalizado

# Campos que se van a procesar
text_fields = ["nombre", "marca", "resolucion", "pagina_fuente"]  # Campos de texto relevantes
numeric_fields = ["precio", "tamano_pulgadas", "calificacion"]     # Campos numéricos que se convertirán a texto
url_field = "url_producto"  # Campo de URL que se incluirá como texto

# Función para limpiar texto: elimina HTML, símbolos raros y normaliza a minúsculas
def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.strip().lower()  # Elimina espacios y pasa a minúsculas
    text = re.sub(r"<[^>]+>", "", text)  # Elimina etiquetas HTML
    text = re.sub(r"[^\w\s.,-]", "", text)  # Elimina símbolos no deseados
    return text

# Función que normaliza un producto para uso con modelos BERT
def normalize_for_berth(product):
    parts = []  # Lista que acumula los fragmentos de texto

    # Procesa campos de texto
    for field in text_fields:
        value = product.get(field)
        if value:
            parts.append(clean_text(value))  # Limpia y agrega el valor

    # Procesa campos numéricos convirtiéndolos a texto
    for field in numeric_fields:
        value = product.get(field)
        if value is not None:
            try:
                parts.append(str(round(float(value), 2)))  # Redondea a 2 decimales y convierte a string
            except Exception:
                continue  # Si hay error, lo ignora

    # Agrega la URL si está disponible
    url = product.get(url_field)
    if url:
        parts.append(clean_text(url))

    # Copia el producto original y agrega el campo 'text' unificado
    producto_normalizado = product.copy()
    producto_normalizado["text"] = " | ".join(parts)  # Une todos los fragmentos con separador

    return producto_normalizado

# Carga los productos desde el archivo JSON
with open(input_file, "r", encoding="utf-8") as f:
    products = json.load(f)

# Aplica la normalización a cada producto
normalized_for_berth = [normalize_for_berth(p) for p in products]

# Guarda el resultado en un nuevo archivo JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(normalized_for_berth, f, ensure_ascii=False, indent=4)

# Mensaje final con cantidad de productos procesados
print(f"Normalización para BERT completada. {len(normalized_for_berth)} productos procesados.")