import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from app.app import db, app
from app.app import Usuario


class RouteTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        # db.init_app(self.app) - Remova esta chamada, já que db já foi inicializado
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_user(self):
        user = Usuario(username='testuser', password='testpassword@123')  # Adapte aos campos do seu modelo
        db.session.add(user)
        db.session.commit()

    def login(self, username, password):
        tester = self.app.test_client(self)
        return tester.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_home_page(self):
        tester = self.app.test_client(self)
        response = tester.get('/')
        self.assertEqual(response.status_code, 200)

    def test_registration_page(self):
        tester = self.app.test_client(self)
        response = tester.get('/registro')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        tester = self.app.test_client(self)
        response = tester.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_page(self):
        self.login('testuser', 'testpassword@123')
        tester = self.app.test_client(self)
        response = tester.get('/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_recipes_page(self):
        self.login('testuser', 'testpassword@123')
        tester = self.app.test_client(self)
        response = tester.get('/dashboard/receitas')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_profile_page(self):
        self.login('testuser', 'testpassword@123')
        tester = self.app.test_client(self)
        response = tester.get('/dashboard/meu-perfil')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_messages_page(self):
        self.login('testuser', 'testpassword@123')
        tester = self.app.test_client(self)
        response = tester.get('/dashboard/mensagens')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_trainings_page(self):
        self.login('testuser', 'testpassword@123')
        tester = self.app.test_client(self)
        response = tester.get('/dashboard/treinos')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_diets_page(self):
        self.login('testuser', 'testpassword@123')
        tester = self.app.test_client(self)
        response = tester.get('/dashboard/dietas')
        self.assertEqual(response.status_code, 200)

    def test_generate_diet_page(self):
        self.login('testuser', 'testpassword@123')
        tester = self.app.test_client(self)
        response = tester.get('/gerar_dieta')
        self.assertEqual(response.status_code, 200)

    def test_diet_details_page(self):
        self.login('testuser', 'testpassword@123')
        tester = self.app.test_client(self)
        response = tester.get('/detalhes_dietas')
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        tester = self.app.test_client(self)
        response = tester.get('/logout')
        self.assertEqual(response.status_code, 302)  # Assuming this redirects to another page

    def test_db_page(self):
        tester = self.app.test_client(self)
        response = tester.get('/db')
        self.assertEqual(response.status_code, 200)

    def test_terms_of_service_page(self):
        tester = self.app.test_client(self)
        response = tester.get('/termos-de-servico')
        self.assertEqual(response.status_code, 200)

    def test_add_bulking_page(self):
        tester = self.app.test_client(self)
        response = tester.get('/adicionar-bulking')
        self.assertEqual(response.status_code, 200)

    def test_add_cutting_page(self):
        tester = self.app.test_client(self)
        response = tester.get('/adicionar-cutting')
        self.assertEqual(response.status_code, 200)

    # Test for the PDF generation route
    # Note: This is a placeholder test. You'll need to adjust it based on the actual functionality.
    def test_generate_pdf(self):
        tester = self.app.test_client(self)
        # Assuming you need to replace `1` with a valid `receita_id`
        response = tester.get('/gerar_pdf/1')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
