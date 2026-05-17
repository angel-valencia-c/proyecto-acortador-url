import os
from flask import Flask
from dotenv import load_dotenv
from database import init_db
from routes import bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-key-insegura")

app.register_blueprint(bp)

if __name__ == '__main__':
    init_db()
    debug = os.getenv("DEBUG", "False").lower() == "true"
    print("Servidor URL Tracker iniciado en puerto 5000")
    app.run(debug=debug, port=5000)