from flask import Flask, request, jsonify, render_template
import random
import re

app = Flask(__name__)

# --- Categorías y palabras clave ---
intents = {
    "escuela": ["clases", "escuela", "estudiante", "profesor", "tareas"],
    "tecnologia": ["software", "tecnologia", "app", "programa", "sistema"],
    "investigacion": ["investigacion", "proyecto", "tesis", "laboratorio", "paper"],
    "hotel": ["hotel", "habitacion", "reservar hotel", "check in", "check out"],
    "restaurante": ["restaurante", "mesa", "reservar mesa", "comida", "cena"],
    "mantenimiento": ["computadora", "pc", "mantenimiento", "reparar", "servicio tecnico"]
}

# --- Respuestas simuladas IA Beta ---
responses_beta = {
    "escuela": [
        "📚 Estoy en modo Beta, pero puedo ayudarte con información escolar.",
        "🤖 Beta AI: Recuerda entregar tus tareas a tiempo.",
        "📖 Beta dice: Si tienes dudas de clase, pregunta y te ayudaré."
    ],
    "tecnologia": [
        "💻 Beta AI: La tecnología avanza rápido, ¿quieres aprender algo nuevo?",
        "🤖 Puedo darte tips de software y apps, aunque estoy en Beta.",
        "⚙️ Beta: Recomiendo mantener tu sistema actualizado."
    ],
    "investigacion": [
        "🔬 Beta AI: Puedo sugerir ideas para tu proyecto o tesis.",
        "📄 Beta: Recuerda documentar todo tu laboratorio.",
        "🧪 Beta dice: La investigación requiere paciencia y curiosidad."
    ],
    "hotel": [
        "🏨 Beta AI: Hagamos una reservación de hotel. ¿A qué nombre?",
        "🤖 Beta: Puedo ayudarte a confirmar tu habitación.",
        "📅 Beta: ¿Qué fecha necesitas la reservación?"
    ],
    "restaurante": [
        "🍽️ Beta AI: Hagamos una reservación de mesa. ¿A qué nombre?",
        "🤖 Beta: Puedo ayudarte a elegir el mejor restaurante.",
        "📌 Beta: No olvides revisar el horario de atención."
    ],
    "mantenimiento": [
        "🛠️ Beta AI: Puedo guiarte para arreglar tu computadora.",
        "💻 Beta dice: Revisa primero las conexiones y cables.",
        "🔧 Beta: Describe el problema y te doy instrucciones."
    ],
    "desconocido": [
        "🤖 Beta AI: No entendí bien, pero puedo ayudarte con escuela, tecnología, investigación, hotel, restaurante o mantenimiento.",
        "💡 Beta: Intenta preguntarme algo diferente.",
        "❓ Beta AI: Estoy aprendiendo, intenta reformular tu pregunta."
    ]
}

# --- Estado de la sesión ---
user_sessions = {}

# --- Función para clasificar intención ---
def clasificar_intencion(texto):
    texto = texto.lower()
    for intent, keywords in intents.items():
        for palabra in keywords:
            if re.search(r"\b" + re.escape(palabra) + r"\b", texto):
                return intent
    return "desconocido"

# --- Frontend ---
@app.route("/")
def home():
    return render_template("index.html")

# --- Bot general ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    user_id = "default"

    # Manejo de sesiones para reservaciones
    if user_id in user_sessions:
        session = user_sessions[user_id]
        if "nombre" not in session:
            session["nombre"] = mensaje
            return jsonify({"respuesta": "Perfecto 👍, ¿qué fecha necesitas la reservación?"})
        elif "fecha" not in session:
            session["fecha"] = mensaje
            return jsonify({"respuesta": "Anotado 📅. ¿A qué hora?"})
        elif "hora" not in session:
            session["hora"] = mensaje
            respuesta_final = f"✅ Reservación confirmada para {session['nombre']} el {session['fecha']} a las {session['hora']}."
            del user_sessions[user_id]
            return jsonify({"respuesta": respuesta_final})

    # Clasificar intención y responder
    intent = clasificar_intencion(mensaje)
    respuesta = random.choice(responses_beta.get(intent, responses_beta["desconocido"]))
    if intent in ["hotel", "restaurante"]:
        user_sessions[user_id] = {"tipo": intent}
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
