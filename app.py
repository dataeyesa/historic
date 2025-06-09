from flask import Flask
import os

app = Flask(__name__)

@app.route('/ping')
def ping():
    return {"status": "ok", "message": "API Historico conectada correctamente ✅"}

# 🔁 Esto permite que Render detecte correctamente el puerto
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)