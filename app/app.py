from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import re
import logging
from functools import wraps
from datetime import timedelta
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pollux:pollux123@localhost/flexifitness'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# Chave secreta para sessões
app.secret_key = '28782878'
app.permanent_session_lifetime = timedelta(minutes=15)

with app.app_context():
    db.create_all()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    perfil = db.relationship('Perfil', backref='usuario', uselist=False)

class Perfil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idade = db.Column(db.Integer)
    peso = db.Column(db.Float)
    sexo = db.Column(db.String(10))
    alergias = db.Column(db.String(200))
    dieta = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

# Função de verificação de autenticação
def verifica_autenticacao(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        else:
            flash('Você deve fazer login para acessar esta página.', 'Você deve fazer login para acessar esta página.')
            return redirect(url_for('login'))
    return decorador

@app.route('/dashboard/meu-perfil', methods=['GET', 'POST'])
@verifica_autenticacao
def meu_perfil():
    user_id = session['user_id']
    usuario = Usuario.query.get(user_id)

    if usuario.perfil:
        flash('Você já possui um perfil cadastrado.', 'Você já possui um perfil cadastrado.')
        logging.info('Você já possui um perfil cadastrado. %s', usuario.username)
        return render_template('perfil.html', usuario=usuario)

    if request.method == 'POST':
        idade = request.form.get('idade')
        peso = request.form.get('peso')
        sexo = request.form.get('sexo')
        alergias = request.form.get('alergias')
        dieta = request.form.get('dieta')

        perfil = Perfil(idade=idade, peso=peso, sexo=sexo, alergias=alergias, dieta=dieta)

        usuario.perfil = perfil  # Associe o perfil ao usuário
        db.session.commit()

        flash('Perfil criado com sucesso!', 'success')
        return redirect(url_for('meu_perfil'))

    return render_template('perfil.html', usuario=usuario)

@app.route('/salvar-perfil', methods=['POST'])
def salvar_perfil():
    # Recupere os dados do perfil do formulário enviado
    idade = request.form.get('idade')
    peso = request.form.get('peso')
    sexo = request.form.get('sexo')
    alergias = request.form.get('alergias')
    dieta = request.form.get('dieta')

    # Faça o processamento dos dados, como validações e salvamento no banco de dados

    # Redirecione o usuário de volta para a página de perfil ou outra página relevante
    return redirect(url_for('perfil'))

# Configurar o log para escrever em um arquivo
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s [%(levelname)s] - %(message)s')

@app.route('/')
def index():
    logging.info('Rota "/" foi acessada.')
    return render_template('index.html')

## Função para verificar se uma senha atende aos critérios mínimos
def senha_atende_aos_criterios(senha):
    # Pelo menos uma letra maiúscula
    if not re.search(r'[A-Z]', senha):
        return False

    # Pelo menos uma letra minúscula
    if not re.search(r'[a-z]', senha):
        return False

    # Pelo menos um caractere especial (você pode definir sua própria lista de caracteres especiais)
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        return False

    # Pelo menos 8 caracteres de comprimento (ou o comprimento mínimo que você deseja)
    if len(senha) < 8:
        return False

    return True

# Função para verificar se um e-mail é válido
def is_valid_email(email):
    # Padrão de expressão regular para verificar o formato de e-mail
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# Rota de registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        try:
            # Verifique se a senha e a confirmação de senha coincidem
            if password != confirm_password:
                flash('As senhas não coincidem. Tente novamente.', 'As senhas não coincidem. Tente novamente.')
                return redirect(url_for('registro'))

            # Verifique se a senha atende aos critérios mínimos
            if not senha_atende_aos_criterios(password):
                flash('A senha deve conter pelo menos uma letra maiúscula, uma letra minúscula, um caractere especial e ter pelo menos 8 caracteres de comprimento.', 'A senha deve conter pelo menos uma letra maiúscula, uma letra minúscula, um caractere especial e ter pelo menos 8 caracteres de comprimento.')
                return redirect(url_for('registro'))

            # Verifique se o e-mail é válido
            if not is_valid_email(email):
                flash('O endereço de e-mail não é válido. Tente novamente.', 'O endereço de e-mail não é válido. Tente novamente.')
                return redirect(url_for('registro'))

            # Verifique se o usuário ou o email já existem no banco de dados
            existing_user = Usuario.query.filter_by(username=username).first()
            existing_email = Usuario.query.filter_by(email=email).first()

            if existing_user:
                flash('Nome de usuário já existe. Escolha outro.', 'Nome de usuário já existe. Escolha outro.')
                return redirect(url_for('registro'))
            elif existing_email:
                flash('Este e-mail já está registrado. Tente outro.', 'Este e-mail já está registrado. Tente outro.')
                return redirect(url_for('registro'))

            # Criptografe a senha antes de armazenar no banco de dados
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Crie um novo usuário e adicione ao banco de dados
            novo_usuario = Usuario(username=username, email=email, password=hashed_password)
            db.session.add(novo_usuario)
            db.session.commit()

            # Registro bem-sucedido
            logging.info('Registro bem-sucedido para o usuário: %s', username)
            flash('Conta criada com sucesso! Você pode fazer login agora.', 'Conta criada com sucesso! Você pode fazer login agora.')
            return redirect(url_for('login'))
        except Exception as e:
            logging.warning('Erro no registro: %s', str(e))
            flash('Ocorreu um erro no registro. Tente novamente mais tarde.', 'Ocorreu um erro no registro. Tente novamente mais tarde.')
            return redirect(url_for('registro'))

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Usuario.query.filter_by(email=email).first()

        try:
            if user:
                if bcrypt.check_password_hash(user.password, password):
                    # Login bem-sucedido
                    logging.info('Login bem-sucedido para o usuário: %s', user.username)
                    session['user_id'] = user.id
                    flash('Login bem-sucedido!', 'Login bem-sucedido!')
                    app.logger.info('User session: %s', session)
                    return redirect(url_for('dashboard'))
                else:
                    # Senha incorreta
                    logging.warning('Senha incorreta para o usuário: %s', user.username)
                    flash('Senha incorreta. Tente novamente.', 'Senha incorreta. Tente novamente.')
            else:
                # Usuário não encontrado
                logging.warning('Usuário não encontrado para o email: %s', email)
                flash('Usuário não encontrado. Verifique seu email.', 'Usuário não encontrado. Verifique seu email.')
        except Exception as e:
            logging.warning('Erro no login: %s', str(e))
            flash(str(e), 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'Você precisa fazer login para acessar esta página.')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

# Routes for the Dashboard page
@app.route('/dashboard/treinos')
def treinos():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'Você precisa fazer login para acessar esta página.')
        return redirect(url_for('login'))
    
    return render_template('treinos.html')

@app.route('/dashboard/dietas')
def dietas():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'Você precisa fazer login para acessar esta página.')
        return redirect(url_for('login'))
    
    return render_template('dietas.html')

@app.route('/dashboard/receitas')
def receitas():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'Você precisa fazer login para acessar esta página.')
        return redirect(url_for('login'))
    
    return render_template('receitas.html')


# Rota de logout
@app.route('/logout')
def logout():
    if 'user_id' in session:
        user = Usuario.query.get(session['user_id'])
        if user:
            logging.info('Usuário desconectado: %s', user.username)
        session.clear()
    flash('Você foi desconectado com sucesso.', 'Você foi desconectado com sucesso.')
    return redirect(url_for('login'))

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

@app.route('/termos-de-servico')
def termos_de_servico():
    logging.info('Rota "/termos-de-servico" foi acessada.')
    return render_template('termos-de-servico.html')

if __name__ == '__main__':
    app.run()
