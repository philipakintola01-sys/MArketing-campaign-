from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Agent Media Team is Alive!"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()
