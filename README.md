# Daniel B Chatbot

Chatbot con estilo de Daniel B basado en conversaciones reales de WhatsApp.

## Despliegue en Render

1. Ve a https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Conecta tu repo de GitHub: `danielbernalanz/piti-chatbot`
4. Configuración automática (detectada desde render.yaml):
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Antes de desplegar, añade la variable de entorno:
   - **OPENCODE_ZEN_KEY** → tu API key de OpenCode
6. Click **Create Web Service**

## Local

```bash
pip install -r requirements.txt
python app.py
```

Luego abre http://localhost:5000
