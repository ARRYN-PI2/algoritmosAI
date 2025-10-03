import json, os, numpy as np
from numpy.linalg import norm
from embedding_service.embedder import embed  # usa tu mismo modelo

RESULTS_PATH = "data/resultados.json"
OUTPUT_PATH = "data/test_results.json"

def cos(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (norm(a) * norm(b)))

# 1) Cargar embeddings
with open(RESULTS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)["results"]

print(f"[info] productos con embedding: {len(data)}")

# 2) Consultas de prueba
consultas = {
    "comunes": [
        "Televisor LG 55 pulgadas 4K",
        "Samsung 65 pulgadas UHD",
        "Televisor barato 43 pulgadas",
        "Smart TV Sony 50 pulgadas",
        "Televisor TCL 32 pulgadas económico"
    ],
    "poco_comunes": [
        "Pantalla curva para videojuegos",
        "Televisor compatible con Alexa",
        "Mini TV portátil de 14 pulgadas",
        "Televisor resistente al agua",
        "Pantalla holográfica 3D"
    ]
}

def rank(consulta_vec, topk=5):
    scores = []
    for p in data:
        s = cos(consulta_vec, p["embedding"])
        scores.append({
            "score": round(s, 3),
            "id": p["id"],
            "texto": p["texto"][:200]
        })
    return sorted(scores, key=lambda x: x["score"], reverse=True)[:topk]

# 3) Ejecutar búsquedas
resultados = {"consultas": {}}
for tipo, qs in consultas.items():
    resultados["consultas"][tipo] = []
    for q in qs:
        qv = embed(q)
        top = rank(qv, topk=5)
        resultados["consultas"][tipo].append({
            "consulta": q,
            "top5": top
        })

# 4) Heurísticas para pares
def heuristic_brand(text):
    for b in ["LG","Samsung","Sony","TCL","Hisense","Xiaomi","Philips"]:
        if b.lower() in text.lower():
            return b
    return "?"

def heuristic_inches(text):
    import re
    m = re.search(r'(\d{2})\s*(\"|pulg|pulgadas)', text.lower())
    return int(m.group(1)) if m else None

pairs_pos, pairs_neg = [], []
for i in range(len(data)):
    bi, si = heuristic_brand(data[i]["texto"]), heuristic_inches(data[i]["texto"])
    for j in range(i+1, len(data)):
        bj, sj = heuristic_brand(data[j]["texto"]), heuristic_inches(data[j]["texto"])
        if bi == "?" or bj == "?" or si is None or sj is None:
            continue
        sim = cos(data[i]["embedding"], data[j]["embedding"])
        if bi == bj and abs(si - sj) <= 2:
            pairs_pos.append(sim)
        elif bi != bj and abs(si - sj) >= 8:
            pairs_neg.append(sim)

def stats(arr):
    return (float(np.mean(arr)) if arr else None,
            float(np.median(arr)) if arr else None,
            len(arr))

mp, medp, npairs_p = stats(pairs_pos)
mn, medn, npairs_n = stats(pairs_neg)

# 5) Precisión general
# Umbral inicial = 0.70 (similares)
umbral = 0.70
tp = sum(1 for s in pairs_pos if s >= umbral)  # verdaderos positivos
fn = sum(1 for s in pairs_pos if s < umbral)   # falsos negativos
tn = sum(1 for s in pairs_neg if s < umbral)   # verdaderos negativos
fp = sum(1 for s in pairs_neg if s >= umbral)  # falsos positivos
total = tp + tn + fp + fn
precision_general = round(100 * (tp + tn) / total, 2) if total > 0 else None

resultados["estadisticas"] = {
    "positivos": {"n": npairs_p, "mean": mp, "median": medp},
    "negativos": {"n": npairs_n, "mean": mn, "median": medn},
    "umbrales_sugeridos": {
        "similar": "cos >= 0.70",
        "dudoso": "0.50 <= cos < 0.70",
        "diferente": "cos < 0.50"
    },
    "precision_general": f"{precision_general}%"
}

# 6) Guardar salida en JSON
os.makedirs("data", exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"\n✅ Resultados guardados en {OUTPUT_PATH}")
print(f"[info] Precisión general: {precision_general}%")
