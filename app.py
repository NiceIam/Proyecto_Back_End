from flask import Flask
from models import db
from routes import main  # Importa el Blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "clave_secreta_super_segura"

db.init_app(app)

# Registrar el Blueprint de rutas
app.register_blueprint(main)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crea las tablas si no existen
    app.run(host="0.0.0.0", port=5000, debug=True)
