import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import system_prompt, MODEL, client

test_inputs = [
    "hola que tal",
    "Piti, que haces",
    "Daniel, vamos a comer?",
    "quieres jugar al magic?",
    "como hago un select en sql?",
    "trabaja negro",
    "te apetece jugar a algo mañana?",
    "eres una ia",
    "Piti, jugamos al league?",
    "Daniel, jugamos al unstable unicorns?",
]

models_to_test = [
    MODEL,
    "deepseek-v4-flash-free",
]

for model in models_to_test:
    print(f"\n{'='*60}")
    print(f"MODELO: {model}")
    print(f"{'='*60}")
    c = client  # reuse from app
    for inp in test_inputs:
        try:
            r = c.chat.completions.create(
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
        print(f"  {inp:40s} -> {reply}")
