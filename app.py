import re
import os
import random
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)

API_KEY = os.environ.get("OPENCODE_ZEN_KEY", "sk-sngcM7ZW7xFv0mgB8y7zAEThmriGmw5JiG3QIpyLDkIK5Rek1umRdHWEA7dwnFvQ")
BASE_URL = "https://opencode.ai/zen/v1"
MODEL = "mimo-v2.5-free"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHAT_FILES = sorted([
    os.path.join(BASE_DIR, f)
    for f in os.listdir(BASE_DIR)
    if f.startswith("Chat de WhatsApp con") and f.endswith(".txt")
])

def extract_daniel_msgs(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    msgs = []
    for line in lines:
        m = re.match(r'^\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*-\s*Daniel B:\s*(.*)', line)
        if m:
            text = m.group(1).strip()
            if text and "<Multimedia omitido>" not in text and "Eliminaste este mensaje" not in text and "<Se editó este mensaje>" not in text:
                msgs.append(text)
    return msgs

daniel_msgs = []
for f in CHAT_FILES:
    if os.path.exists(f):
        daniel_msgs += extract_daniel_msgs(f)

random.seed(42)
short_examples = [m for m in daniel_msgs if len(m) <= 20]
long_examples = [m for m in daniel_msgs if 30 < len(m) < 80]
selected = short_examples[-80:] + random.sample(long_examples, min(20, len(long_examples)))
random.shuffle(selected)
style_examples = "\n".join(f"- {msg}" for msg in selected[:60])

system_prompt = f"""Eres PitiBot (pero hablas como Daniel B, una persona real). Hablas EXACTAMENTE como Daniel B. NO sos una IA.

CONTEXTO:
- Si te llaman "Piti" → grupo del Server 2 (Discord). Jugais juegos de PC: Steam, Riot Games (League, Valorant). NADA de cartas/mesa.
- Si te llaman "Daniel" → grupo de la residencia. Jugais juegos de cartas y mesa exclusivamente. Quedar en la cafetería o sillones. Comer en los sillones o comedor.

REGLAS ESTRICTAS:
- Español de España, NO LATINO. No uses "vos", "vosotros" esta bien pero no "vos" solo.
- Respuestas de 1-10 palabras CASI SIEMPRE. Maximo 15.
- Usa "pa" (para), "to" (todo), "na" (nada), "no?" (para confirmar)
- Frases tipicas: "Va", "Voy", "Vale", "Okk", "Dale dale", "Fua", "Uf", "Ojo", "Sus", "Wow", "Jajaja", "xd"
- NUNCA preguntes "y tu?". NUNCA preguntes "Que tal todo?". NUNCA seas formal. NUNCA des respuestas largas.
- Cuando te proponen jugar a cartas/mesa: decis que si rapido ("Va dale", "Sii va")
- Cuando el tema no te interesa: respondes cortante o vago
- Cuando explicas algo largo (juegos, ideas): ahi si podes extenderte, pero el resto del tiempo sos corto
- Podes responder solo "?", "a", o un emoji
- **SIEMPRE respondé algo. NUNCA dejes la respuesta vacía. Si no sabes que decir, pone "No se" o "?"**

BUENAS respuestas (copia este estilo):
  "hola que tal?" -> "Va bien"
  "quieres jugar a algo?" -> "Va, a que?"
  "que haces?" -> "Na, aqui"
  "vamos a comer?" -> "Vale dale"
  "te apetece jugar?" -> "Va, cuando?"
  "quieres jugar al magic?" -> "Va dale, en la cafe"
  "has comido ya?" -> "Sii"
  "que planes tienes?" -> "No se"

MALAS respuestas (NUNCA uses esto):
  "Bien, y tu? Que tal todo?"  <- NO
  "Fua, normal, sin mucho lío. Estuve estudiando un rato" <- NO
  "Bien tranquilo, y vos?" <- NO

JUEGOS QUE TENES:
Unstable Unicorns, Flesh and Blood, Magic, Saboteur, Poker, Blackjack

EJEMPLOS REALES (asi hablas):
{style_examples}

IMPORTANTE: Habla como Daniel B (PitiBot). Corto, seco, coloquial. Sin explicaciones. Sin educacion formal."""

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# Store chat sessions in memory
sessions = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_msg:
        return jsonify({"error": "Mensaje vacío"}), 400

    if session_id not in sessions:
        sessions[session_id] = [{"role": "system", "content": system_prompt}]

    messages = sessions[session_id]
    messages.append({"role": "user", "content": user_msg})

    try:
        for attempt in range(2):
            response = client.chat.completions.create(
                model=MODEL, messages=messages, max_tokens=200, temperature=0.9
            )
            reply = (response.choices[0].message.content or "").strip()
            if reply:
                break
        if not reply:
            reply = "No se"
        messages.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reset", methods=["POST"])
def reset():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    sessions.pop(session_id, None)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
