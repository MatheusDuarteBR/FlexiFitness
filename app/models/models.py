from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    perfil = db.relationship('Perfil', backref='usuario', uselist=False)

class Perfil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primeiro_nome = db.Column(db.String(50))
    sobrenome = db.Column(db.String(50))
    celular = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    cep = db.Column(db.String(10))
    idade = db.Column(db.Integer)
    peso = db.Column(db.Float)
    altura = db.Column(db.Float)
    sexo = db.Column(db.String(10))
    estado = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Dieta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cafe_manha = db.Column(db.String(200))
    lanche_manha = db.Column(db.String(200))
    almoco = db.Column(db.String(200))
    cafe_tarde = db.Column(db.String(200))
    janta = db.Column(db.String(200))
    ceia = db.Column(db.String(200))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('dashboard_user.id'), nullable=False)

# Adicione o relacionamento na tabela Usuario
class Dashboard_user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String(10), nullable=False)
    nivel_atividade = db.Column(db.String(20), nullable=False)
    objetivo = db.Column(db.String(10), nullable=False)
    tipo_atividade = db.Column(db.String(50), nullable=False)
    dietas = db.relationship('Dieta', backref='usuario', lazy=True)

class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=True)
    refeicao = db.Column(db.String(20), nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    imagem = db.Column(db.String(255))
    tempo_de_preparo = db.Column(db.String(50))
    ingredientes = db.Column(db.Text)
    modo_de_preparo = db.Column(db.Text)