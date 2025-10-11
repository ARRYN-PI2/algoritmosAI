# embedding_service/embedder.py
from .model_loader import get_model
import re

# ----------------------------------------------
# 1) Generación de embeddings
# ----------------------------------------------
def embed(text_or_texts):
    """
    Genera embeddings usando el modelo cargado con SentenceTransformer.
    - Si recibe un string: retorna un embedding (list[float]) de 768 dimensiones.
    - Si recibe una lista de strings: retorna una lista de embeddings.
    """
    model = get_model()

    # Caso 1: texto único
    if isinstance(text_or_texts, str):
        vec = model.encode(
            [text_or_texts],
            convert_to_numpy=True,
            show_progress_bar=False
        ).tolist()[0]
        return vec

    # Caso 2: lista de textos
    texts = list(text_or_texts)
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False).tolist()


# ----------------------------------------------
# 2) Generador de texto a partir de un producto
# ----------------------------------------------
def _norm(s):
    """Limpia espacios y puntos duplicados."""
    if not s:
        return ""
    s = str(s).strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\.\s*\.", ".", s)
    return s


def _parse_price_from_text(precio_texto):
    """
    Extrae valor numérico de cadenas tipo 'COP 7.299.900' o '$ 899,900 COP'.
    """
    if not precio_texto:
        return None
    txt = str(precio_texto)
    m = re.search(r"(\d[\d\.\, ]+)", txt)
    if not m:
        return None
    digits = m.group(1)
    digits = digits.replace(".", "").replace(",", "").replace(" ", "")
    try:
        return int(digits)
    except Exception:
        return None


def _price_tier(valor):
    """
    Determina la categoría del precio (en COP):
      - < 1.500.000 → económico / buen precio
      - 1.500.000 - 6.999.999 → precio medio
      - ≥ 7.000.000 → gama alta
    """
    if valor is None:
        return None
    if valor < 1_500_000:
        return "económico / buen precio"
    if valor >= 7_000_000:
        return "gama alta"
    return "precio medio"


def _format_money(valor, moneda="COP"):
    """Formatea un número con separador de miles (puntos)."""
    if valor is None:
        return None
    try:
        s = f"{valor:,}".replace(",", ".")
    except Exception:
        s = str(valor)
    return f"{s} {moneda}" if moneda else s


def text_from_product(prod: dict) -> str:
    """
    Crea una descripción natural del producto combinando sus principales atributos:
      1. Título
      2. Marca + tamaño + precio + etiqueta de rango + calificación
      3. Descripción / detalles
      4. Link de la fuente

    Ejemplo de salida:
      'Televisor HYUNDAI 32 pulgadas LED Hd Básico HYLED3241D.
       Marca: HYUNDAI | Tamaño: 32" | Precio: 726.900 COP (económico / buen precio)
       | Calificación: No tiene Calificación | Opiniones: 0.
       Descripción: Lleva a casa fácil y rápido Televisor HYUNDAI 32" pulgadas LED Hd Básico...
       Más info: https://www.exito.com/...'
    """
    # ---- Extracción de atributos principales ----
    titulo = _norm(prod.get("titulo") or prod.get("title") or "")
    marca = _norm(prod.get("marca") or "")
    moneda = _norm(prod.get("moneda") or "COP")
    precio_valor = prod.get("precio_valor")
    if precio_valor is None:
        precio_valor = _parse_price_from_text(prod.get("precio_texto"))
    detalles = _norm(prod.get("detalles_adicionales") or prod.get("descripcion") or "")
    link = _norm(prod.get("link") or prod.get("url") or "")
    tam = _norm(prod.get("tamaño") or prod.get("tamano") or prod.get("size") or "")
    calif = _norm(prod.get("calificacion") or "")
    nops = _norm(prod.get("numero_opiniones") or prod.get("opiniones") or "")

    partes = []

    # ---- 1) Título ----
    if titulo:
        partes.append(titulo)

    # ---- 2) Marca + info técnica ----
    info_line = []
    if marca:
        info_line.append(f"Marca: {marca}")
    if tam:
        info_line.append(f"Tamaño: {tam}")

    if precio_valor is not None:
        etiqueta = _price_tier(precio_valor)
        precio_fmt = _format_money(precio_valor, moneda)
        if etiqueta:
            info_line.append(f"Precio: {precio_fmt} ({etiqueta})")
        else:
            info_line.append(f"Precio: {precio_fmt}")
    else:
        ptxt = _norm(prod.get("precio_texto") or "")
        if ptxt:
            info_line.append(f"Precio: {ptxt}")

    if calif:
        info_line.append(f"Calificación: {calif}")
    if nops:
        info_line.append(f"Opiniones: {nops}")

    if info_line:
        partes.append(" | ".join(info_line))

    # ---- 3) Descripción ----
    if detalles:
        if not detalles.lower().startswith("descripción"):
            partes.append(f"Descripción: {detalles}")
        else:
            partes.append(detalles)

    # ---- 4) Fuente / link ----
    if link:
        partes.append(f"Más info: {link}")

    # ---- Ensamblado final ----
    texto = ". ".join([p for p in partes if p])
    texto = re.sub(r"\.\s*\.\s*", ". ", texto).strip()
    return texto
