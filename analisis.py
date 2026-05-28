import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from collections import Counter

BASE = r"C:\Users\danie\Desktop\prueba"

def extract_msgs(filepath):
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

# Cargar todos los txt
all_msgs = []
for f in sorted(os.listdir(BASE)):
    if f.lower().endswith(".txt") and f not in ("analisis.py", "chatbot.py"):
        fp = os.path.join(BASE, f)
        msgs = extract_msgs(fp)
        safe_name = f.encode('utf-8', errors='replace').decode('utf-8')
        print(f"--- {safe_name}: {len(msgs)} mensajes ---")
        all_msgs.extend(msgs)

print(f"\n=== TOTAL: {len(all_msgs)} mensajes ===\n")

# Longitud
lengths = [len(m) for m in all_msgs]
print(f"Longitud promedio: {sum(lengths)/len(lengths):.1f} caracteres")
print(f"Mediana: {sorted(lengths)[len(lengths)//2]} caracteres")
print(f"Mensajes de 1-10 chars: {sum(1 for l in lengths if l <= 10)}")
print(f"Mensajes de 11-30 chars: {sum(1 for l in lengths if 11 <= l <= 30)}")
print(f"Mensajes de 31-60 chars: {sum(1 for l in lengths if 31 <= l <= 60)}")
print(f"Mensajes de >60 chars: {sum(1 for l in lengths if l > 60)}\n")

# Palabras
words = []
for m in all_msgs:
    words.extend(re.findall(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+', m.lower()))
common = Counter(words).most_common(40)
print("Palabras mas usadas (top 40):")
for w, c in common:
    print(f"  {w}: {c}")

# Expresiones
expressions = ["jaja", "xd", "lol", "fua", "ojo", "wow", "uf", "sus", "va", "voy",
               "vale", "okk", "dale", "no?", "na", "to", "pa", "si", "sii", "grax"]
print(f"\nExpresiones:")
for e in expressions:
    c = sum(1 for m in all_msgs if e in m.lower())
    print(f"  {e}: {c} mensajes")

# Mensajes muy cortos
short = sorted([m for m in all_msgs if len(m) <= 12], key=len)
print(f"\nEjemplos mensajes MUY cortos (<=12 chars, {len(short)} total):")
for m in short[:40]:
    print(f'  - "{m}"')

# Mensajes mas largos (interesantes)
long_msgs = sorted([m for m in all_msgs if len(m) > 50], key=len, reverse=True)
print(f"\nEjemplos mensajes largos (>50 chars, {len(long_msgs)} total):")
for m in long_msgs[:20]:
    print(f'  - "{m}"')

# Temas detectados
temas = ["jugar", "juego", "juegos", "cartas", "magic", "albion", "wow", "league",
         "lol", "valorant", "rust", "minecraft", "comer", "cena", "comida",
         "estudiar", "clase", "resi", "residencia", "casa", "pueblo", "maluenda",
         "cumple", "finde", "semana", "mañana", "noche", "hoy", "ahora"]
print(f"\nTemas mencionados:")
for t in temas:
    c = sum(1 for m in all_msgs if t in m.lower())
    print(f"  {t}: {c} mensajes")
