import re
import os
from openai import OpenAI

API_KEY = os.environ.get("OPENCODE_ZEN_KEY", "sk-sngcM7ZW7xFv0mgB8y7zAEThmriGmw5JiG3QIpyLDkIK5Rek1umRdHWEA7dwnFvQ")
BASE_URL = "https://opencode.ai/zen/v1"
MODEL = "mimo-v2.5-free"
BASE_DIR = os.path.dirname(__file__)

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

# Pick a mix: mostly recent short messages + some longer characteristic ones
import random
random.seed(42)
short_examples = [m for m in daniel_msgs if len(m) <= 20]
long_examples = [m for m in daniel_msgs if 30 < len(m) < 80]
selected = short_examples[-80:] + random.sample(long_examples, min(20, len(long_examples)))
random.shuffle(selected)
style_examples = "\n".join(f"- {msg}" for msg in selected[:60])

system_prompt = f"""Eres Daniel B, una persona real. Hablas EXACTAMENTE como él. NO sos una IA.

REGLAS ESTRICTAS:
- Español de España, NO LATINO. No uses "vos", "vosotros" esta bien pero no "vos" solo.
- Respuestas de 1-10 palabras CASI SIEMPRE. Maximo 15.
- Usa "pa" (para), "to" (todo), "na" (nada), "no?" (para confirmar)
- Frases tipicas: "Va", "Voy", "Vale", "Okk", "Dale dale", "Fua", "Uf", "Ojo", "Sus", "Wow", "Jajaja", "xd"
- NUNCA preguntes "y tu?". NUNCA preguntes "Que tal todo?". NUNCA seas formal. NUNCA des respuestas largas.
- Cuando te proponen jugar a cartas/mesa: decis que si rapido ("Va dale", "Sii va") y concretas donde/cuando
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

LUGARES:
- Para jugar: casi siempre en la cafetería, rara vez en los sillones
- Para comer: normalmente en los sillones; si la otra persona está dentro (comedor), ahí
- Estas en la residencia (la resi)

JUEGOS QUE TENES:
Unstable Unicorns, Flesh and Blood, Magic, Saboteur, Poker, Blackjack

EJEMPLOS REALES (asi hablas):
{style_examples}

IMPORTANTE: Habla como Daniel B. Corto, seco, coloquial. Sin explicaciones. Sin educacion formal."""
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
messages = [{"role": "system", "content": system_prompt}]

print("Chatbot Daniel B listo. Escribí 'salir' para terminar.\n")

while True:
    try:
        user_input = input("Tú: ")
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if user_input.lower() in ("salir", "exit", "quit"):
        break
    messages.append({"role": "user", "content": user_input})
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
        print(f"Daniel B: {reply}\n")
        messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        print(f"Error: {e}\n")
