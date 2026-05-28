import re, os, sys, json
from openai import OpenAI

API_KEY = os.environ.get("OPENCODE_ZEN_KEY", "sk-sngcM7ZW7xFv0mgB8y7zAEThmriGmw5JiG3QIpyLDkIK5Rek1umRdHWEA7dwnFvQ")
BASE_URL = "https://opencode.ai/zen/v1"
BASE_DIR = r"C:\Users\danie\Desktop\prueba"

# Load messages
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

all_msgs = []
for f in sorted(os.listdir(BASE_DIR)):
    if f.startswith("Chat de WhatsApp con") and f.endswith(".txt"):
        all_msgs += extract_daniel_msgs(os.path.join(BASE_DIR, f))

import random
random.seed(42)
short_examples = [m for m in all_msgs if len(m) <= 20]
long_examples = [m for m in all_msgs if 30 < len(m) < 80]
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
- Comer: comedor o sillones
- Jugar: sillones o cafetería
- Estas en la residencia (la resi)

JUEGOS QUE TENES:
Unstable Unicorns, Flesh and Blood, Magic, Saboteur, Poker, Blackjack

EJEMPLOS REALES (asi hablas):
{style_examples}

IMPORTANTE: Habla como Daniel B. Corto, seco, coloquial. Sin explicaciones. Sin educacion formal."""

test_inputs = [
    "hola que tal",
    "quieres jugar a algo",
    "que haces",
    "vamos a comer?",
    "quieres jugar al magic?",
    "donde quedamos?",
    "has comido ya?",
    "jugamos al unstable unicorns?",
    "donde quedamos para jugar?",
    "te apetece jugar a algo mañana?",
]

models_to_test = [
    "mimo-v2.5-free",
    "deepseek-v4-flash-free",
    "big-pickle",
]

for model in models_to_test:
    print(f"\n{'='*60}")
    print(f"MODELO: {model}")
    print(f"{'='*60}")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    for inp in test_inputs:
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": inp}
                ],
                max_tokens=200,
                temperature=0.9
            )
            reply = (r.choices[0].message.content or "").strip()
            if not reply:
                reply = "[VACIO]"
        except Exception as e:
            reply = f"[ERROR: {str(e)[:60]}]"
        safe_inp = inp.encode('utf-8', errors='replace').decode('utf-8')
        safe_reply = reply.encode('utf-8', errors='replace').decode('utf-8')
        print(f"  {safe_inp:40s} -> {safe_reply}")
    print()
