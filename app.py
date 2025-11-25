from flask import Flask
from database import init_db
from routes import bp

app = Flask(__name__)

app.register_blueprint(bp)



if __name__ == '__main__':
  
    init_db()
    print("Servidor URL Tracker iniciado en puerto 5000")
    app.run(debug=True, port=5000)