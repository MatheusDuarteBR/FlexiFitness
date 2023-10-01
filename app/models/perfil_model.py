from app import db

class Perfil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primeiro_nome = db.Column(db.String(50))
    sobrenome = db.Column(db.String(50))
    celular = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    cep = db.Column(db.String(10))
    idade = db.Column(db.Integer)
    peso = db.Column(db.Float)
    sexo = db.Column(db.String(10))
    estado = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))