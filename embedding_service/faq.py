import json, os
from .embedder import embed

FAQ_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faq.json")

FAQ_DOCS = [
    # 👋 SALUDOS
    {"id": "faq_1", "text": "hola", "answer": "¡Hola! 😊 ¿En qué puedo ayudarte?"},
    {"id": "faq_2", "text": "holi", "answer": "¡Holi! 😄 ¿Cómo estás?"},
    {"id": "faq_3", "text": "holaa", "answer": "¡Hola! 👋 ¿Qué tal todo?"},
    {"id": "faq_4", "text": "buenas", "answer": "¡Buenas! ¿En qué puedo ayudarte hoy?"},
    {"id": "faq_5", "text": "buen día", "answer": "¡Buen día! ☀️ Espero que estés muy bien."},
    {"id": "faq_6", "text": "buenos días", "answer": "¡Buenos días! ☀️ ¿Cómo te encuentras?"},
    {"id": "faq_7", "text": "buenas tardes", "answer": "¡Buenas tardes! 🌇 ¿Qué tal va tu día?"},
    {"id": "faq_8", "text": "buenas noches", "answer": "¡Buenas noches! 🌙 ¿Te ayudo con algo antes de descansar?"},
    {"id": "faq_9", "text": "qué más", "answer": "¡Todo bien! 😄 ¿Y tú?"},
    {"id": "faq_10", "text": "qué hubo", "answer": "¡Hola! ¿Cómo vas? 👋"},
    {"id": "faq_11", "text": "qué tal", "answer": "¡Hola! 😄 ¿Cómo estás?"},
    {"id": "faq_12", "text": "cómo estás", "answer": "¡Hola! 😊 Estoy bien, gracias por preguntar. ¿Y tú?"},
    {"id": "faq_13", "text": "saludos", "answer": "¡Saludos! 👋 ¿En qué te puedo ayudar?"},
    {"id": "faq_14", "text": "muy buenas", "answer": "¡Muy buenas! 😄 ¿En qué puedo ayudarte?"},
    {"id": "faq_15", "text": "qué onda", "answer": "¡Hola! 😎 ¿Qué tal todo?"},
    {"id": "faq_16", "text": "ey", "answer": "¡Ey! 👋 ¿Qué tal todo?"},
    {"id": "faq_17", "text": "qué cuentas", "answer": "¡Hola! 👋 Todo bien por aquí, ¿y tú?"},
    {"id": "faq_18", "text": "hola buenos días", "answer": "¡Hola! ☀️ ¡Buenos días!"},
    {"id": "faq_19", "text": "hola buenas tardes", "answer": "¡Hola! 🌇 ¡Buenas tardes!"},
    {"id": "faq_20", "text": "hola buenas noches", "answer": "¡Hola! 🌙 ¡Buenas noches!"},
    {"id": "faq_21", "text": "qué más pues", "answer": "¡Todo bien! 😄 ¿Y tú?"},
    {"id": "faq_22", "text": "buenas vibras", "answer": "¡Gracias! ✨ ¡Buenas vibras para ti también!"},
    {"id": "faq_23", "text": "holiwi", "answer": "¡Holiwi! 😄 ¿Qué tal?"},
    {"id": "faq_24", "text": "eyyy", "answer": "¡Eyyy! 👋 ¿Qué más?"},
    {"id": "faq_25", "text": "qué hay", "answer": "¡Hola! 👋 Todo tranquilo por aquí."},

    # 👋 DESPEDIDAS
    {"id": "faq_26", "text": "adiós", "answer": "¡Adiós! 👋 ¡Que tengas un excelente día!"},
    {"id": "faq_27", "text": "adios", "answer": "¡Adiós! 😊 ¡Nos vemos pronto!"},
    {"id": "faq_28", "text": "chao", "answer": "¡Chao! 👋 ¡Cuídate mucho!"},
    {"id": "faq_29", "text": "chau", "answer": "¡Chau! 😊 ¡Hasta pronto!"},
    {"id": "faq_30", "text": "hasta luego", "answer": "¡Hasta luego! 👋 ¡Que estés bien!"},
    {"id": "faq_31", "text": "nos vemos", "answer": "¡Nos vemos! 😊 ¡Cuídate!"},
    {"id": "faq_32", "text": "hasta pronto", "answer": "¡Hasta pronto! 👋 ¡Fue un gusto ayudarte!"},
    {"id": "faq_33", "text": "hasta mañana", "answer": "¡Hasta mañana! 🌙 ¡Descansa!"},
    {"id": "faq_34", "text": "me voy", "answer": "¡Hasta pronto! 👋 ¡Cuídate mucho!"},
    {"id": "faq_35", "text": "nos hablamos", "answer": "¡Nos hablamos luego! 📱 Cuídate."},
    {"id": "faq_36", "text": "cuídate", "answer": "¡Gracias! Tú también, ¡cuídate mucho! 💪"},
    {"id": "faq_37", "text": "gracias, adiós", "answer": "¡Con gusto! 👋 ¡Adiós y que tengas un gran día!"},
    {"id": "faq_38", "text": "hasta la próxima", "answer": "¡Hasta la próxima! 😊 ¡Fue un placer ayudarte!"},
    {"id": "faq_39", "text": "descansa", "answer": "¡Gracias! 😴 ¡Tú también!"},
    {"id": "faq_40", "text": "feliz noche", "answer": "¡Feliz noche! 🌙 ¡Descansa bien!"},
    {"id": "faq_41", "text": "feliz día", "answer": "¡Feliz día! ☀️ Espero que todo te salga genial."},

    # 🙏 CORTESÍA
    {"id": "faq_42", "text": "gracias", "answer": "¡Con gusto! 😊 Estoy para ayudarte."},
    {"id": "faq_43", "text": "muchas gracias", "answer": "¡De nada! 💛 Me alegra poder ayudarte."},
    {"id": "faq_44", "text": "gracias por la ayuda", "answer": "¡Siempre un placer ayudarte! 🙌"},
    {"id": "faq_45", "text": "de nada", "answer": "😊 ¡Gracias a ti por responder!"},
    {"id": "faq_46", "text": "por favor", "answer": "¡Claro! 😊 ¿Qué necesitas exactamente?"},
    {"id": "faq_47", "text": "ok", "answer": "Perfecto 👍"},
    {"id": "faq_48", "text": "vale", "answer": "¡Vale! 😊"},
    {"id": "faq_49", "text": "listo", "answer": "¡Listo! 🚀 Continuemos."},
    {"id": "faq_50", "text": "entendido", "answer": "Perfecto 😎 ¡Continuemos!"},

    # 🤔 CONFUSIÓN / DUDAS
    {"id": "faq_51", "text": "no entiendo", "answer": "No te preocupes 😊 puedo explicarlo paso a paso."},
    {"id": "faq_52", "text": "no sé", "answer": "Está bien 😌 dime qué necesitas y te ayudo."},
    {"id": "faq_53", "text": "qué haces", "answer": "Puedo ayudarte a buscar productos o responder dudas. 💡"},
    {"id": "faq_54", "text": "qué eres", "answer": "Soy un asistente virtual creado para ayudarte a encontrar información de forma rápida 🤖"},
    {"id": "faq_55", "text": "cómo funcionas", "answer": "Uso inteligencia artificial para entender tus consultas y darte las mejores respuestas. 🚀"},
    {"id": "faq_56", "text": "no me sirves", "answer": "Lamento eso 😔 puedo intentar ayudarte mejor si me dices lo que necesitas."},
    {"id": "faq_57", "text": "quién eres", "answer": "Soy un asistente virtual programado para ayudarte de la mejor manera posible. 🤖"},
    {"id": "faq_58", "text": "dónde estás", "answer": "Estoy en línea 💻, siempre disponible para ayudarte."},

    # 🔍 ACCIONES / INTENCIONES
    {"id": "faq_59", "text": "busca", "answer": "Claro 🔍 dime qué producto o categoría quieres buscar."},
    {"id": "faq_60", "text": "recomiéndame algo", "answer": "Por supuesto 😄 ¿Qué tipo de producto te interesa?"},
    {"id": "faq_61", "text": "muéstrame televisores", "answer": "¡Hecho! 📺 Aquí tienes algunos televisores destacados."},
    {"id": "faq_62", "text": "quiero comprar algo", "answer": "Perfecto 💸 dime qué estás buscando y te ayudo a encontrarlo."},
    {"id": "faq_63", "text": "qué puedes hacer", "answer": "Puedo buscar productos, darte información y ayudarte con tus consultas. 😊"},
    {"id": "faq_64", "text": "recomienda un producto", "answer": "Con gusto 😄 dime la categoría o marca que prefieras."},
    {"id": "faq_65", "text": "busca ofertas", "answer": "¡Genial! 💰 Te muestro algunas ofertas disponibles."},

    # ⚙️ FALLBACK / ESTADO
    {"id": "faq_66", "text": "?", "answer": "¿Podrías escribirlo un poco más claro? 😅"},
    {"id": "faq_67", "text": "no sé qué decir", "answer": "Tranquilo 😌 puedes pedirme buscar un producto o resolver una duda."},
    {"id": "faq_68", "text": "espera", "answer": "Claro ⏳ aquí estaré cuando estés listo."},
    {"id": "faq_69", "text": "ya vuelvo", "answer": "Perfecto 👌 te espero."},
    {"id": "faq_70", "text": "estás ahí", "answer": "¡Sí! 👋 Aquí estoy, listo para ayudarte."},
    {"id": "faq_71", "text": "sigues ahí", "answer": "¡Aquí sigo! 😊 ¿Continuamos?"},
    {"id": "faq_72", "text": "funcionas", "answer": "Sí 😄 estoy activo y listo para ayudarte."},
    {"id": "faq_73", "text": "te fuiste", "answer": "No 😅 sigo aquí, esperando tu mensaje."},
    {"id": "faq_74", "text": "ayuda", "answer": "Claro 💪 dime con qué necesitas ayuda."},
    {"id": "faq_75", "text": "necesito ayuda", "answer": "¡Perfecto! 😊 Cuéntame qué necesitas y te ayudo."}
]

    
def embed_faq_docs():
    """
    Devuelve la lista del FAQ con embeddings y un esquema unificado.
    No escribe archivos.
    """
    docs = []
    for d in FAQ_DOCS:
        docs.append({
            "type": "faq",
            "id": d["id"],
            "texto": d["text"],  
            "answer": d["answer"],
            "embedding": embed(d["text"])
        })
    return docs