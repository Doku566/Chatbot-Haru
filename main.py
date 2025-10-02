from flask import Flask, request, jsonify, render_template
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)

# --- Intenciones ---
intents = {
    "escuela": ["clases", "escuela", "estudiante", "profesor", "tareas"],
    "tecnologia": ["software", "tecnologia", "app", "programa", "sistema"],
    "investigacion": ["investigacion", "proyecto", "tesis", "laboratorio", "paper"],
    "hotel": ["hotel", "habitacion", "reservar hotel", "check in", "check out"],
    "restaurante": ["restaurante", "mesa", "reservar mesa", "comida", "cena"],
    "mantenimiento": ["computadora", "pc", "mantenimiento", "reparar", "servicio tecnico"]
}

respuestas = {
    "escuela": "📚 Puedo ayudarte con información de la escuela o clases.",
    "tecnologia": "💻 Soy experto en tecnología y software.",
    "investigacion": "🔬 Te ayudo con investigación y proyectos académicos.",
    "hotel": "🏨 Puedo ayudarte con reservaciones de hotel. ¿A qué nombre hacemos la reservación?",
    "restaurante": "🍽️ Hagamos una reservación en restaurante. ¿A qué nombre?",
    "mantenimiento": "🛠️ Servicio de mantenimiento de computadoras. ¿Qué problema tienes?",
    "desconocido": "🤖 No entendí. Puedo ayudarte con Escuela, Tecnología, Investigación, Hotel, Restaurante o Mantenimiento."
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

# --- Bot de categorías y reservaciones ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    user_id = "default"

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

    intent = clasificar_intencion(mensaje)
    if intent in ["hotel", "restaurante"]:
        user_sessions[user_id] = {"tipo": intent}

    respuesta = respuestas.get(intent, respuestas["desconocido"])
    return jsonify({"respuesta": respuesta})

# --- Bot IA conversacional liviano local ---
model_name = "microsoft/DialoGPT-small"  # modelo pequeño (~100MB)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

device = torch.device("cpu")
model.to(device)
tokenizer.pad_token = tokenizer.eos_token

@app.route("/chat-ia", methods=["POST"])
def chat_ia():
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    user_id = "default"

    if user_id not in user_sessions:
        user_sessions[user_id] = {"historial": []}

    historial = user_sessions[user_id]["historial"]
    contexto = " ".join(historial[-4:] + [f"Usuario: {mensaje}"])

    try:
        inputs = tokenizer.encode(contexto + " Bot:", return_tensors="pt").to(device)
        outputs = model.generate(
            inputs,
            max_new_tokens=50,  # rápido y ligero
            pad_token_id=tokenizer.pad_token_id,
            do_sample=True,
            top_p=0.9,
            temperature=0.7,
        )
        respuesta = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "Bot:" in respuesta:
            respuesta = respuesta.split("Bot:")[-1].strip()
        respuesta = respuesta.split("\n")[0].strip()

        historial.append(f"Usuario: {mensaje}")
        historial.append(f"Bot: {respuesta}")

    except Exception as e:
        print("Error del modelo:", e)
        respuesta = "❌ Error al comunicarse con el bot."

    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
