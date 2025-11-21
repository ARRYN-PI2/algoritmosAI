import json, os, numpy as np
from numpy.linalg import norm
from embedding_service.embedder import embed  # usa tu mismo modelo

# -----------------------------
# Paths (solo índice unificado)
# -----------------------------
UNIFIED_INDEX_PATH = "data/index_unificado.json"
OUTPUT_PATH = "data/test_results.json"

# -----------------------------
# Utils
# -----------------------------
def cos(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (norm(a) * norm(b)))

def load_unified():
    with open(UNIFIED_INDEX_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)["results"]
    faq = [d for d in docs if d.get("type") == "faq"]
    prods = [d for d in docs if d.get("type") == "product"]
    return faq, prods

def compute_metrics(tp, fn, tn, fp):
    total = tp + fn + tn + fp
    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    accuracy = (tp + tn) / total if total > 0 else None
    f1 = (2*precision*recall)/(precision+recall) if (precision is not None and recall is not None and (precision+recall)>0) else None
    return {
        "tp": tp, "fn": fn, "tn": tn, "fp": fp, "total": total,
        "precision_%": round(precision*100,2) if precision is not None else None,
        "recall_%": round(recall*100,2) if recall is not None else None,
        "accuracy_%": round(accuracy*100,2) if accuracy is not None else None,
        "f1_%": round(f1*100,2) if f1 is not None else None
    }

# -----------------------------
# 1) Cargar índice unificado
# -----------------------------
FAQ, PRODS = load_unified()
print(f"[info] FAQ: {len(FAQ)} | Productos: {len(PRODS)} | Total: {len(FAQ)+len(PRODS)}")

# -----------------------------
# 2) Pruebas de ranking (productos)
# -----------------------------
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

def rank_products(qv, topk=5):
    scores = []
    for p in PRODS:
        s = cos(qv, p["embedding"])
        scores.append({
            "score": round(s, 3),
            "id": p.get("id"),
            "texto": p.get("texto","")[:200]
        })
    return sorted(scores, key=lambda x: x["score"], reverse=True)[:topk]

resultados = {"consultas": {}}
for tipo, qs in consultas.items():
    resultados["consultas"][tipo] = []
    for q in qs:
        qv = embed(q)
        top = rank_products(qv, topk=5)
        resultados["consultas"][tipo].append({"consulta": q, "top5": top})

# -----------------------------
# 3) Heurísticas para pares (productos)
# -----------------------------
def heuristic_brand(text):
    for b in ["LG","Samsung","Sony","TCL","Hisense","Xiaomi","Philips","Hyundai","Kalley","Challenger","Caixun","Exclusiv"]:
        if b.lower() in text.lower():
            return b
    return "?"

def heuristic_inches(text):
    import re
    m = re.search(r'(\d{2,3})\s*(\"|pulg|pulgadas)', text.lower())
    return int(m.group(1)) if m else None

pairs_pos, pairs_neg = [], []
for i in range(len(PRODS)):
    bi, si = heuristic_brand(PRODS[i]["texto"]), heuristic_inches(PRODS[i]["texto"])
    for j in range(i+1, len(PRODS)):
        bj, sj = heuristic_brand(PRODS[j]["texto"]), heuristic_inches(PRODS[j]["texto"])
        if bi == "?" or bj == "?" or si is None or sj is None:
            continue
        sim = cos(PRODS[i]["embedding"], PRODS[j]["embedding"])
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

umbral_prod = 0.70
tp = sum(1 for s in pairs_pos if s >= umbral_prod)
fn = sum(1 for s in pairs_pos if s < umbral_prod)
tn = sum(1 for s in pairs_neg if s < umbral_prod)
fp = sum(1 for s in pairs_neg if s >= umbral_prod)
total = tp + tn + fp + fn
accuracy_prod = round(100 * (tp + tn) / total, 2) if total > 0 else None

# -----------------------------
# 4) Evaluación del FAQ (detección)
# -----------------------------
faq_threshold = 0.78  # ajustable

faq_queries_pos = [
    "hola", "buenas tardes", "buenas noches", "chao",
    "gracias", "ayuda", "no entiendo", "qué puedes hacer"
]
faq_queries_neg = [
    "televisor lg 55 pulgadas 4k",
    "samsung 65 pulgadas uhd",
    "smart tv sony 50 pulgadas",
    "televisor tcl 32 pulgadas económico",
    "soporte tv 55 pulgadas pared",
]

def best_faq_score(query: str):
    qv = embed(query)
    best = -1.0
    best_item = None
    for d in FAQ:
        s = cos(qv, d["embedding"])
        if s > best:
            best = s
            best_item = d
    return best, best_item

# Positivos
tp_faq, fn_faq = 0, 0
pos_examples = []
for q in faq_queries_pos:
    s, item = best_faq_score(q)
    if s >= faq_threshold:
        tp_faq += 1
        pos_examples.append({"q": q, "score": round(s,3), "match": item.get("texto"), "answer": item.get("answer")})
    else:
        fn_faq += 1
        pos_examples.append({"q": q, "score": round(s,3), "pred":"NO_MATCH"})

# Negativos
tn_faq, fp_faq = 0, 0
neg_examples = []
for q in faq_queries_neg:
    s, item = best_faq_score(q)
    if s >= faq_threshold:
        fp_faq += 1
        neg_examples.append({"q": q, "score": round(s,3), "false_match": item.get("texto")})
    else:
        tn_faq += 1
        neg_examples.append({"q": q, "score": round(s,3), "pred":"NO_MATCH"})

metrics_faq = compute_metrics(tp_faq, fn_faq, tn_faq, fp_faq)

# -----------------------------
# 5) Guardar salida
# -----------------------------
resultados["estadisticas"] = {
    "productos": {
        "positivos": {"n": npairs_p, "mean": mp, "median": medp},
        "negativos": {"n": npairs_n, "mean": mn, "median": medn},
        "umbrales_sugeridos": {
            "similar": "cos >= 0.70",
            "dudoso": "0.50 <= cos < 0.70",
            "diferente": "cos < 0.50"
        },
        "accuracy_%": accuracy_prod
    },
    "faq": {
        "threshold": faq_threshold,
        "metricas": metrics_faq,
        "ejemplos_positivos": pos_examples[:10],
        "ejemplos_negativos": neg_examples[:10]
    }
}

os.makedirs("data", exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"\n✅ Resultados guardados en {OUTPUT_PATH}")
print(f"[info] Productos -> accuracy: {accuracy_prod}% | pares+: {npairs_p} | pares-: {npairs_n}")
print(f"[info] FAQ(th={faq_threshold}) -> {metrics_faq}")
