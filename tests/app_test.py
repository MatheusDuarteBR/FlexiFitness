# tests/test_app.py

import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Mova a criação do objeto Flask e SQLAlchemy para fora da classe de teste
app = Flask(__name__)
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(app)

class TestApp(unittest.TestCase):

    def setUp(self):
        # Use o contexto de aplicação Flask para criar e configurar o banco de dados
        with app.app_context():
            db.create_all()

        self.app = app.test_client()

    def tearDown(self):
        # Limpe o banco de dados após cada teste
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_registro_sucesso(self):
        data = {
            'username': 'novousuario',
            'email': 'novousuario@example.com',
            'password': 'Senha123!',
            'confirm_password': 'Senha123!'
        }
        response = self.app.post('/registro', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn (b'Conta criada com sucesso. Voce pode fazer o login agora!', response.data)

    def test_registro_senhas_diferentes(self):
        data = {
            'username': 'novousuario',
            'email': 'novousuario@example.com',
            'password': 'Senha123!',
            'confirm_password': 'Senha456!'
        }
        response = self.app.post('/registro', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'As senhas n\xc3\xa3o coincidem. Tente novamente.', response.data)

    def test_registro_senha_fraca(self):
        data = {
            'username': 'novousuario',
            'email': 'novousuario@example.com',
            'password': 'senhafraca',
            'confirm_password': 'senhafraca'
        }
        response = self.app.post('/registro', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'A senha deve conter pelo menos uma letra mai\xc3\xbascula, uma letra min\xc3\xbascula, um caractere especial e ter pelo menos 8 caracteres de comprimento.', response.data)

    def test_registro_email_invalido(self):
        data = {
            'username': 'novousuario',
            'email': 'emailinvalido',
            'password': 'Senha123!',
            'confirm_password': 'Senha123!'
        }
        response = self.app.post('/registro', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'O endere\xc3\xa7o de e-mail n\xc3\xa3o \xc3\xa9 v\xc3\xa1lido. Tente novamente.', response.data)

    def test_registro_usuario_existente(self):
        # Registra um usuário para simular um usuário já existente
        self.app.post('/registro', data={
            'username': 'novousuario',
            'email': 'novousuario@example.com',
            'password': 'Senha123!',
            'confirm_password': 'Senha123!'
        }, follow_redirects=True)

        # Tenta registrar o mesmo usuário novamente
        data = {
            'username': 'novousuario',
            'email': 'novousuario2@example.com',
            'password': 'Senha123!',
            'confirm_password': 'Senha123!'
        }
        response = self.app.post('/registro', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Nome de usu\xc3\xa1rio j\xc3\xa1 existe. Escolha outro.', response.data)

    def test_registro_email_existente(self):
        # Registra um usuário para simular um e-mail já existente
        self.app.post('/registro', data={
            'username': 'novousuario',
            'email': 'novousuario@example.com',
            'password': 'Senha123!',
            'confirm_password': 'Senha123!'
        }, follow_redirects=True)

        # Tenta registrar um novo usuário com o mesmo e-mail
        data = {
            'username': 'novousuario2',
            'email': 'novousuario@example.com',
            'password': 'Senha123!',
            'confirm_password': 'Senha123!'
        }
        response = self.app.post('/registro', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Este e-mail j\xc3\xa1 est\xc3\xa1 registrado. Tente outro.', response.data)

if __name__ == '__main__':
    unittest.main()
