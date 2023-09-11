from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pollux:pollux123@localhost/flexifitness'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Chave secreta para sessões
app.secret_key = '28782878'

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# Defina a classe do modelo de usuário (se já não estiver definida)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Rota de registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Verifique se a senha e a confirmação de senha coincidem
        if password != confirm_password:
            flash('As senhas não coincidem. Tente novamente.', 'danger')
            return redirect(url_for('registro'))

        # Verifique se o usuário ou o email já existem no banco de dados
        existing_user = Usuario.query.filter_by(username=username).first()
        existing_email = Usuario.query.filter_by(email=email).first()

        if existing_user:
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
            return redirect(url_for('registro'))
        elif existing_email:
            flash('Este e-mail já está registrado. Tente outro.', 'danger')
            return redirect(url_for('registro'))
        else:
            # Criptografe a senha antes de armazenar no banco de dados
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Crie um novo usuário e adicione ao banco de dados
            novo_usuario = Usuario(username=username, email=email, password=hashed_password)
            db.session.add(novo_usuario)
            db.session.commit()

            flash('Conta criada com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Usuario.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('dashboard'))  # Redirecionar para a página de dashboard após o login

        flash('Credenciais inválidas. Tente novamente.', 'danger')
    return render_template('login.html')


# Rota de teste de conexão com o banco de dados
@app.route('/db')
def teste_conexao_db():
    try:
        # Execute uma consulta para listar todos os usuários
        usuarios = Usuario.query.all()
        if usuarios:
            return 'Conexão com o banco de dados estabelecida com sucesso!'
        else:
            return 'Não há usuários registrados no banco de dados.'
    except Exception as e:
        return f'Erro ao conectar com o banco de dados: {str(e)}'

if __name__ == '__main__':
    app.run()


