from app import db

# Defina a classe do modelo de usuário (se já não estiver definida)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Perfil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idade = db.Column(db.Integer)
    peso = db.Column(db.Float)
    sexo = db.Column(db.String(10))
    alergias = db.Column(db.String(200))
    dieta = db.Column(db.String(20))