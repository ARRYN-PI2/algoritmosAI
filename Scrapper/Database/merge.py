import json  # Módulo para leer y escribir archivos JSON
import re    # Módulo para trabajar con expresiones regulares

# Función que extrae el número de pulgadas desde un texto como "55 pulgadas" o '55"'
def extraer_pulgadas(texto):
    if not texto: return None  # Si el texto está vacío, retorna None
    match = re.search(r'(\d+)', str(texto))  # Busca el primer número en el texto
    return int(match.group(1)) if match else None  # Retorna el número como entero

# Función que extrae la resolución desde la primera línea del campo 'detalles_adicionales'
def extraer_resolucion(detalles):
    if not detalles: return None  # Si no hay detalles, retorna None
    primera_linea = detalles.strip().split("\n")[0]  # Toma la primera línea del texto
    # Verifica si contiene alguna palabra clave de resolución
    if any(x in primera_linea.upper() for x in ["4K", "FULL HD", "FHD", "UHD", "HD"]):
        return primera_linea  # Si contiene resolución, la retorna
    return None  # Si no contiene resolución, retorna None

# Carga los datos desde el archivo JSON de Alkosto
with open("../Alkosto/alkosto.json", "r", encoding="utf-8") as f:
    alkosto_data = json.load(f)

# Carga los datos desde el archivo JSON de Falabella
with open("../Falabella/falabella.json", "r", encoding="utf-8") as f:
    falabella_data = json.load(f)

productos_unificados = []  # Lista donde se almacenarán todos los productos normalizados

# Procesa cada producto del archivo de Alkosto
for p in alkosto_data["productos"]:
    productos_unificados.append({
        "nombre": p.get("nombre"),  # Nombre del producto
        "precio": p.get("precio", 0.0),  # Precio, por defecto 0.0 si no existe
        "tamano_pulgadas": p.get("tamano_pulgadas"),  # Tamaño en pulgadas
        "calificacion": p.get("calificacion"),  # Calificación del producto
        "marca": p.get("marca"),  # Marca del producto
        "resolucion": p.get("resolucion"),  # Resolución si está disponible
        "pagina_fuente": p.get("pagina_fuente", "Alkosto"),  # Fuente del producto
        "url_producto": p.get("url_producto")  # URL del producto
    })

# Procesa cada producto del archivo de Falabella
for p in falabella_data:
    productos_unificados.append({
        "nombre": p.get("titulo"),  # Nombre del producto
        "precio": p.get("precio_valor", 0.0),  # Precio, por defecto 0.0 si no existe
        "tamano_pulgadas": extraer_pulgadas(p.get("tamaño")),  # Extrae pulgadas del campo 'tamaño'
        "calificacion": p.get("calificacion") if p.get("calificacion") != "N/A" else None,  # Normaliza calificación
        "marca": p.get("marca"),  # Marca del producto
        "resolucion": extraer_resolucion(p.get("detalles_adicionales")),  # Extrae resolución desde detalles
        "pagina_fuente": p.get("fuente", "Falabella"),  # Fuente del producto
        "url_producto": p.get("link")  # URL del producto
    })

# Guarda el resultado unificado en un nuevo archivo JSON
with open("merged.json", "w", encoding="utf-8") as f:
    json.dump(productos_unificados, f, indent=4, ensure_ascii=False)

# Muestra en consola cuántos productos se han unificado
print(f"Se han unificado {len(productos_unificados)} productos en merged.json")