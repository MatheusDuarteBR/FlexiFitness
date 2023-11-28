from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from flask_bcrypt import Bcrypt
import re
import logging
from functools import wraps
from datetime import timedelta
from flask_migrate import Migrate
from io import BytesIO
from reportlab.lib.pagesizes import letter
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from weasyprint import HTML
from dotenv import load_dotenv
import os
from flask_wtf.csrf import CSRFProtect


load_dotenv()

DEBUG = os.getenv("DEBUG")
USERNAME= 'pollux'
PASSWORD = os.getenv("PASSWORD")
SERVER = os.getenv("SERVER")
DB = os.getenv("DB")
SECRET_KEY = os.getenv("SECRET_KEY")

# Adicione logs para debug
print(f"DEBUG: {DEBUG}")
print(f"USERNAME: {USERNAME}")
print(f"PASSWORD: {PASSWORD}")
print(f"SERVER: {SERVER}")
print(f"DB: {DB}")
print(f"SECRET_KEY: {SECRET_KEY}")

SQLALCHEMY_DATABASE_URI = f"postgresql://{USERNAME}:{PASSWORD}@{SERVER}/{DB}"
SQLALCHEMY_TRACK_MODIFICATIONS = True

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
db.init_app(app)
csrf = CSRFProtect(app)

# Chave secreta para sessões
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(minutes=55)

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

class Dieta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    objetivo = db.Column(db.String(50), nullable=False)
    nivel_atividade = db.Column(db.String(20), nullable=False)
    calorias_diarias = db.Column(db.Integer, nullable=False)
    proteinas_diarias = db.Column(db.Float, nullable=False)
    gorduras_diarias = db.Column(db.Float, nullable=False)
    carboidratos_diarios = db.Column(db.Float, nullable=False)
    refeicoes = db.relationship('Refeicao', secondary='dieta_refeicao', backref='dietas')

class Refeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    proteinas = db.Column(db.Float, nullable=False)
    gorduras = db.Column(db.Float, nullable=False)
    carboidratos = db.Column(db.Float, nullable=False)

class DietaRefeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dieta_id = db.Column(db.Integer, db.ForeignKey('dieta.id'), nullable=False)
    refeicao_id = db.Column(db.Integer, db.ForeignKey('refeicao.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/gerar_pdf/<int:receita_id>', methods=['GET'])
def gerar_pdf(receita_id):
    receita = Receita.query.get(receita_id)

    html_template = render_template('template.html', receita=receita)
    pdf = HTML(string=html_template).write_pdf()

    buffer = BytesIO(pdf)

    response = make_response(buffer.read())
    response.mimetype = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={receita.nome}.pdf'

    return response

@app.route('/dashboard/receitas', methods=['GET'])
def receitas():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'Você precisa fazer login para acessar esta página.')
        return redirect(url_for('login'))

    categoria_filtrada = request.args.get('categoria', default=None, type=str)
    refeicao_filtrada = request.args.get('refeicao', default=None, type=str)
    calorias_max = request.args.get('calorias_max', default=None, type=int)

    # Aqui você recupera todas as receitas
    query = Receita.query

    # Filtragem com base nos parâmetros
    if categoria_filtrada:
        query = query.filter_by(categoria=categoria_filtrada)

    if refeicao_filtrada:
        query = query.filter_by(refeicao=refeicao_filtrada)

    if calorias_max is not None:
        query = query.filter(Receita.calorias <= calorias_max)

    receitas = query.all()

    return render_template('receitas.html', receitas=receitas)

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
@csrf.exempt
@verifica_autenticacao
def meu_perfil():
    user_id = session['user_id']
    usuario = Usuario.query.get(user_id)

    if usuario.perfil:
        flash('Você já possui um perfil cadastrado.', 'Você já possui um perfil cadastrado.')
        logging.info('Você já possui um perfil cadastrado. %s', usuario.username)
        return render_template('perfil.html', usuario=usuario)

    if request.method == 'POST':
        primeiro_nome = request.form.get('primeiro_nome')
        sobrenome = request.form.get('sobrenome')
        celular = request.form.get('celular')
        endereco = request.form.get('endereco')
        cep = request.form.get('cep')
        idade = request.form.get('idade')
        peso = request.form.get('peso')
        sexo = request.form.get('sexo')
        estado = request.form.get('estado')

        perfil = Perfil(
            primeiro_nome=primeiro_nome,
            sobrenome=sobrenome,
            celular=celular,
            endereco=endereco,
            cep=cep,
            idade=idade,
            peso=peso,
            sexo=sexo,
            estado=estado
        )

        usuario.perfil = perfil
        db.session.commit()

        flash('Perfil criado com sucesso!', 'success')
        return redirect(url_for('meu_perfil'))

    return render_template('perfil.html', usuario=usuario)

@app.route('/dashboard/mensagens')
def mensagens():
    return render_template('mensagem.html')

@app.route('/')
def index():
    logging.info('Rota "/" foi acessada.')
    return render_template('index.html')

## Função para verificar se uma senha atende aos critérios mínimos
def senha_atende_aos_criterios(senha):
    if not re.search(r'[A-Z]', senha):
        return False

    if not re.search(r'[a-z]', senha):
        return False

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        return False

    if len(senha) < 8:
        return False

    return True

# Função para verificar se um e-mail é válido
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

@app.route('/registro', methods=['GET', 'POST'])
@csrf.exempt
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
@csrf.exempt
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
    user_id = session['user_id']
    usuario = Usuario.query.get(user_id)
    
    return render_template('dashboard.html', usuario=usuario)


# Routes for the Dashboard page
@app.route('/dashboard/treinos')
def treinos():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'Você precisa fazer login para acessar esta página.')
        return redirect(url_for('login'))
    
    return render_template('treinos.html')

#########==================DIETAS_START=================#########


@app.route('/dashboard/dietas', methods=['GET', 'POST'])
@csrf.exempt
def dietas():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'Você precisa fazer login para acessar esta página.')
        return redirect(url_for('login'))
    return render_template('dietas.html')

@app.route('/gerar_dieta', methods=['POST'])
@csrf.exempt
def gerar_dieta():
    if request.method == 'POST':
        dados_formulario = request.form

        objetivo = dados_formulario['objetivo']
        nivel_atividade = dados_formulario['nivel_atividade']

        # Lógica de cálculo de dieta (exemplo simplificado)
        calorias_diarias = calcular_calorias_diarias(objetivo, nivel_atividade)
        proteinas_diarias = calcular_proteinas_diarias(calorias_diarias)
        gorduras_diarias = calcular_gorduras_diarias(calorias_diarias)
        carboidratos_diarios = calcular_carboidratos_diarios(calorias_diarias)

        # Adiciona a dieta ao banco de dados
        nova_dieta = Dieta(
            objetivo=objetivo,
            nivel_atividade=nivel_atividade,
            calorias_diarias=calorias_diarias,
            proteinas_diarias=proteinas_diarias,
            gorduras_diarias=gorduras_diarias,
            carboidratos_diarios=carboidratos_diarios
        )
        db.session.add(nova_dieta)
        db.session.commit()

        # Adicione refeições à dieta (exemplo: adicione refeições associadas a essa dieta)
        adicionar_refeicoes_a_dieta(nova_dieta)

        flash('Dieta gerada com sucesso!', 'success')
        return redirect(url_for('dietas'))

def calcular_calorias_diarias(objetivo, nivel_atividade):
    # Lógica de cálculo de calorias diárias (exemplo simplificado)
    if objetivo == 'emagrecimento':
        fator_objetivo = 0.8
    elif objetivo == 'hipertrofia':
        fator_objetivo = 1.2
    else:
        fator_objetivo = 1.0

    if nivel_atividade == 'sedentario':
        fator_atividade = 1.2
    elif nivel_atividade == 'moderado':
        fator_atividade = 1.5
    else:
        fator_atividade = 1.8

    calorias_diarias = 2000  # Substitua pelo cálculo real
    return int(calorias_diarias * fator_objetivo * fator_atividade)

def calcular_proteinas_diarias(calorias_diarias):
    # Lógica de cálculo de proteínas diárias (exemplo simplificado)
    return int(calorias_diarias * 0.3 / 4)  # 30% das calorias diárias de proteínas, 4 calorias por grama

def calcular_gorduras_diarias(calorias_diarias):
    # Lógica de cálculo de gorduras diárias (exemplo simplificado)
    return int(calorias_diarias * 0.25 / 9)  # 25% das calorias diárias de gorduras, 9 calorias por grama

def calcular_carboidratos_diarios(calorias_diarias):
    # Lógica de cálculo de carboidratos diários (exemplo simplificado)
    return int(calorias_diarias * 0.45 / 4)  # 45% das calorias diárias de carboidratos, 4 calorias por grama

def adicionar_refeicoes_a_dieta(dieta):
    # Adiciona refeições à dieta (exemplo simplificado)
    refeicao1 = Refeicao(nome='Café da Manhã', calorias=400, proteinas=20, gorduras=15, carboidratos=60)
    refeicao2 = Refeicao(nome='Almoço', calorias=600, proteinas=30, gorduras=20, carboidratos=80)
    refeicao3 = Refeicao(nome='Lanche da Tarde', calorias=200, proteinas=10, gorduras=5, carboidratos=30)
    refeicao4 = Refeicao(nome='Jantar', calorias=500, proteinas=25, gorduras=18, carboidratos=70)

    dieta.refeicoes.extend([refeicao1, refeicao2, refeicao3, refeicao4])
    db.session.commit()

@app.route('/detalhes_dietas', methods=['GET'])
def detalhes_dietas():
    # Consulte o banco de dados para obter detalhes das dietas (substitua por sua lógica real)
    dietas = Dieta.query.all()

    # Crie uma lista para armazenar os detalhes das dietas
    detalhes_dietas = []

    # Preencha a lista com os detalhes das dietas
    for dieta in dietas:
        detalhes_dietas.append({
            'objetivo': dieta.objetivo,
            'nivel_atividade': dieta.nivel_atividade,
            'calorias_diarias': dieta.calorias_diarias,
            'proteinas_diarias': dieta.proteinas_diarias,
            'gorduras_diarias': dieta.gorduras_diarias,
            'carboidratos_diarios': dieta.carboidratos_diarios
        })

    # Retorne os detalhes das dietas como JSON
    return jsonify(detalhes_dietas)

#########==================DIETAS_END=================#########

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

log_file_path = 'app.log'
handler = RotatingFileHandler(log_file_path, maxBytes=1000000, backupCount=5)
logging.basicConfig(handlers=[handler], level=logging.DEBUG, format='%(asctime)s [%(levelname)s] - %(message)s')

@app.route('/adicionar-bulking')
def add_example_recipes():
    receitas = [
        {"nome": "Salada de Frango", "descricao": "Salada de frango com vegetais frescos para aumentar as calorias. Uma opção saudável para o bulking.", "calorias": 800, "refeicao": "cafe_da_manha", "imagem": "miniatures/chicken_salad.jpg", "tempo_de_preparo": "15 minutos", "ingredientes": "Peito de frango, alface, tomate, cenoura, azeite, sal, pimenta.", "modo_de_preparo": "Cozinhe o peito de frango, corte em pedaços e misture com os vegetais. Tempere com azeite, sal e pimenta."},
        {"nome": "Arroz Integral com Salmão", "descricao": "Arroz integral nutritivo acompanhado de salmão grelhado, proporcionando uma refeição rica em proteínas e carboidratos.", "calorias": 900, "refeicao": "jantar", "imagem": "miniatures/rice_salmao.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Arroz integral, salmão, azeite, alho, sal, limão.", "modo_de_preparo": "Cozinhe o arroz integral. Tempere o salmão com alho, sal e limão. Grelhe o salmão e sirva sobre o arroz."},
        {"nome": "Omelete de Espinafre", "descricao": "Omelete saudável e recheado com espinafre, uma opção rica em proteínas e vitaminas.", "calorias": 600, "refeicao": "almoco", "imagem": "miniatures/omelete_espinafre.jpg", "tempo_de_preparo": "10 minutos", "ingredientes": "Ovos, espinafre, queijo, sal, pimenta.", "modo_de_preparo": "Bata os ovos, adicione o espinafre e o queijo. Tempere com sal e pimenta. Cozinhe em fogo médio até ficar pronto."},
        {"nome": "Smoothie de Banana e Amendoim", "descricao": "Smoothie energético com banana e amendoim para um lanche reforçado durante o dia.", "calorias": 500, "refeicao": "cafe_da_tarde", "imagem": "miniatures/smoothie_amendoim.jpg", "tempo_de_preparo": "5 minutos", "ingredientes": "Banana, leite, amendoim, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura homogênea."},
        {"nome": "Frango Grelhado com Batata Doce", "descricao": "Prato principal de frango grelhado acompanhado de batata doce, fornecendo proteínas e carboidratos complexos.", "calorias": 850, "refeicao": "almoco", "imagem": "miniatures/batata_doce_frango.jpg", "tempo_de_preparo": "30 minutos", "ingredientes": "Peito de frango, batata doce, azeite, sal, ervas.", "modo_de_preparo": "Tempere o frango e a batata doce com azeite, sal e ervas. Grelhe o frango e asse a batata."},
        {"nome": "Wrap de Atum", "descricao": "Wrap saudável recheado com atum, vegetais e molho de iogurte, ideal para uma refeição leve e rica em proteínas.", "calorias": 750, "refeicao": "jantar", "imagem": "miniatures/wrap_atum.jpg", "tempo_de_preparo": "15 minutos", "ingredientes": "Tortilla integral, atum, alface, tomate, iogurte, limão.", "modo_de_preparo": "Misture o atum com vegetais e molho de iogurte. Coloque no interior da tortilla e enrole."},
        {"nome": "Smoothie de Manga e Aveia", "descricao": "Smoothie refrescante com manga e aveia para um lanche rápido e nutritivo.", "calorias": 400, "refeicao": "cafe_da_tarde", "imagem": "miniatures/smoothie_manga_aveia.jpg", "tempo_de_preparo": "10 minutos", "ingredientes": "Manga, leite, aveia, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura cremosa."},
        {"nome": "Quinoa com Legumes", "descricao": "Prato de quinoa com legumes coloridos, uma opção vegetariana rica em proteínas e fibras.", "calorias": 900, "refeicao": "almoco", "imagem": "miniatures/quinoa_legumes.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Quinoa, abobrinha, cenoura, pimentão, azeite, sal.", "modo_de_preparo": "Cozinhe a quinoa e refogue os legumes no azeite. Misture tudo."},
        {"nome": "Smoothie de Morango e Banana", "descricao": "Smoothie delicioso com morango e banana para uma opção doce e nutritiva.", "calorias": 450, "refeicao": "cafe_da_tarde", "imagem": "miniatures/smoothie_morango_banana.jpg", "tempo_de_preparo": "5 minutos", "ingredientes": "Morango, banana, iogurte, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura suave."},
        {"nome": "Frango Assado com Quinoa", "descricao": "Peito de frango assado acompanhado de quinoa, proporcionando uma refeição completa e nutritiva.", "calorias": 950, "refeicao": "jantar", "imagem": "miniatures/frango_quinoa.jpg", "tempo_de_preparo": "40 minutos", "ingredientes": "Peito de frango, quinoa, brócolis, azeite, sal.", "modo_de_preparo": "Tempere o frango e a quinoa. Asse o frango e misture com a quinoa e brócolis."},
        {"nome": "Wrap de Frango e Abacate", "descricao": "Wrap recheado com frango grelhado, abacate e vegetais frescos, uma opção saudável e saborosa.", "calorias": 800, "refeicao": "almoco", "imagem": "miniatures/wrap_frango_abacate.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Tortilla integral, peito de frango, abacate, alface, tomate.", "modo_de_preparo": "Grelhe o frango e monte o wrap com os ingredientes."},
        {"nome": "Smoothie de Pêssego e Aveia", "descricao": "Smoothie nutritivo com pêssego e aveia para um lanche rápido e saudável.", "calorias": 500, "refeicao": "cafe_da_tarde", "imagem": "miniatures/smoothie_pessego_aveia.jpg", "tempo_de_preparo": "10 minutos", "ingredientes": "Pêssego, leite, aveia, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura cremosa."},
        {"nome": "Macarrão Integral com Frango", "descricao": "Macarrão integral com peito de frango grelhado, uma opção rica em carboidratos e proteínas.", "calorias": 900, "refeicao": "almoco", "imagem": "miniatures/macarrao_com_frango.jpg", "tempo_de_preparo": "25 minutos", "ingredientes": "Macarrão integral, peito de frango, molho de tomate, azeite.", "modo_de_preparo": "Cozinhe o macarrão e grelhe o frango. Misture com molho de tomate e azeite."},
        {"nome": "Smoothie de Abacaxi e Coco", "descricao": "Smoothie tropical com abacaxi e coco para uma opção refrescante e calórica.", "calorias": 450, "refeicao": "cafe_da_tarde", "imagem": "miniatures/smoothie_abacaxi_coco.jpg", "tempo_de_preparo": "7 minutos", "ingredientes": "Abacaxi, leite de coco, iogurte, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura suave."},
        {"nome": "Sopa de Lentilhas", "descricao": "Sopa nutritiva de lentilhas, uma opção rica em proteínas e fibras.", "calorias": 700, "refeicao": "jantar", "imagem": "miniatures/sopa_de_lentilha.jpg", "tempo_de_preparo": "30 minutos", "ingredientes": "Lentilhas, cebola, alho, cenoura, caldo de legumes.", "modo_de_preparo": "Cozinhe as lentilhas com os vegetais e caldo de legumes até ficar macio."},
        {"nome": "Salada de Quinoa", "descricao": "Salada de quinoa com vegetais frescos para uma opção saudável e rica em proteínas.", "calorias": 750, "refeicao": "almoco", "imagem": "miniatures/salada_quinoa.jpg", "tempo_de_preparo": "15 minutos", "ingredientes": "Quinoa, pepino, tomate, azeitonas, azeite, sal, limão.", "modo_de_preparo": "Cozinhe a quinoa e misture com os vegetais. Tempere com azeite, sal e limão."},
        {"nome": "Panquecas de Aveia", "descricao": "Panquecas leves e saudáveis feitas com aveia, ideais para o café da manhã.", "calorias": 500, "refeicao": "cafe_da_manha", "imagem": "miniatures/panquecas_aveia.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Aveia, banana, ovo, leite, canela.", "modo_de_preparo": "Misture a aveia, banana, ovo, leite e canela. Cozinhe em uma frigideira até dourar dos dois lados."},
        {"nome": "Tigela de Açaí", "descricao": "Tigela de açaí com granola, frutas e mel, proporcionando um lanche energético e delicioso.", "calorias": 600, "refeicao": "cafe_da_tarde", "imagem": "miniatures/acai.jpg", "tempo_de_preparo": "10 minutos", "ingredientes": "Açaí, granola, banana, morango, mel.", "modo_de_preparo": "Misture o açaí com granola e decore com frutas. Regue com mel."},
        {"nome": "Hambúrguer de Quinoa", "descricao": "Hambúrguer vegetariano feito com quinoa, uma opção saudável e rica em proteínas.", "calorias": 700, "refeicao": "jantar", "imagem": "miniatures/hamburguer_quinoa.jpg", "tempo_de_preparo": "25 minutos", "ingredientes": "Quinoa, feijão preto, cenoura, cebola, alho, cominho.", "modo_de_preparo": "Cozinhe a quinoa e misture com feijão preto, cenoura, cebola, alho e cominho. Forme hambúrgueres e grelhe."},
        {"nome": "Salada de Frutas", "descricao": "Salada refrescante de frutas variadas para um lanche saudável e colorido.", "calorias": 400, "refeicao": "cafe_da_tarde", "imagem": "miniatures/salada_frutas.jpg", "tempo_de_preparo": "10 minutos", "ingredientes": "Morango, kiwi, manga, uva, mel.", "modo_de_preparo": "Corte as frutas e misture em uma tigela. Regue com mel e sirva gelado."},
        {"nome": "Couscous Marroquino com Vegetais", "descricao": "Couscous marroquino com vegetais grelhados, uma opção leve e saborosa para o almoço.", "calorias": 800, "refeicao": "almoco", "imagem": "miniatures/couscus.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Couscous marroquino, abobrinha, pimentão, berinjela, azeite, hortelã.", "modo_de_preparo": "Prepare o couscous conforme as instruções e misture com vegetais grelhados. Tempere com azeite e hortelã."},
        {"nome": "Smoothie de Melancia e Menta", "descricao": "Smoothie refrescante com melancia e menta para uma bebida veranil e hidratante.", "calorias": 450, "refeicao": "cafe_da_tarde", "imagem": "miniatures/smoothie_melancia.jpg", "tempo_de_preparo": "5 minutos", "ingredientes": "Melancia, menta, limão, água.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura suave."},
        {"nome": "Wraps de Legumes", "descricao": "Wraps vegetarianos recheados com legumes frescos e molho de iogurte, uma opção leve para o jantar.", "calorias": 650, "refeicao": "jantar", "imagem": "miniatures/wrap_legumes.jpg", "tempo_de_preparo": "15 minutos", "ingredientes": "Tortilla integral, abobrinha, cenoura, cogumelos, iogurte.", "modo_de_preparo": "Grelhe os legumes e monte os wraps com molho de iogurte."},
        {"nome": "Bowl de Salmão Grelhado", "descricao": "Bowl nutritivo com salmão grelhado, arroz integral, abacate e vegetais, uma refeição completa.", "calorias": 900, "refeicao": "almoco", "imagem": "miniatures/bowl_salmao.jpg", "tempo_de_preparo": "30 minutos", "ingredientes": "Salmão, arroz integral, abacate, brócolis, cenoura.", "modo_de_preparo": "Grelhe o salmão e prepare os ingredientes. Monte o bowl com todos os elementos."},
        {"nome": "Smoothie de Framboesa e Chia", "descricao": "Smoothie antioxidante com framboesa e sementes de chia para um lanche saudável e nutritivo.", "calorias": 500, "refeicao": "cafe_da_tarde", "imagem": "miniatures/smoothie_framboesa.jpg", "tempo_de_preparo": "8 minutos", "ingredientes": "Framboesa, banana, chia, leite de amêndoas.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura cremosa."},
]

    for receita_data in receitas:
        nova_receita = Receita(**receita_data, categoria="bulking")
        db.session.add(nova_receita)

    db.session.commit()
    return redirect(url_for('receitas'))

@app.route('/adicionar-cutting')
def add_cutting_recipes():
    receitas = [
        {"nome": "Tigela de Quinoa com Abacate", "descricao": "Tigela nutritiva com quinoa, abacate e vegetais frescos.", "calorias": 600, "refeicao": "almoco", "imagem": "miniatures/tigela-de-quinoa-com-abacate-.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Quinoa, abacate, tomate cereja, pepino, azeite, sal.", "modo_de_preparo": "Cozinhe a quinoa e misture com os vegetais. Adicione abacate e tempere."},
        {"nome": "Frango com Brócolis", "descricao": "Prato principal de frango grelhado com brócolis, uma opção rica em proteínas.", "calorias": 550, "refeicao": "jantar", "imagem": "miniatures/frango-com-brocolis.jpg", "tempo_de_preparo": "25 minutos", "ingredientes": "Peito de frango, brócolis, azeite, alho, sal, pimenta.", "modo_de_preparo": "Grelhe o frango e cozinhe o brócolis. Misture com azeite, alho, sal e pimenta."},
        {"nome": "Salada de Atum", "descricao": "Salada leve e proteica com atum, ovos e vegetais variados.", "calorias": 450, "refeicao": "almoco", "imagem": "miniatures/salada-atum.jpg", "tempo_de_preparo": "15 minutos", "ingredientes": "Atum em lata, ovos cozidos, alface, tomate, azeitonas, azeite, sal.", "modo_de_preparo": "Misture todos os ingredientes em uma tigela. Tempere com azeite e sal."},
        {"nome": "Smoothie de Blueberry", "descricao": "Smoothie antioxidante com blueberries, banana e iogurte.", "calorias": 380, "refeicao": "cafe_da_tarde", "imagem": "miniatures/blueberry-smoothie.jpg", "tempo_de_preparo": "8 minutos", "ingredientes": "Blueberries, banana, iogurte, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura suave."},
        {"nome": "Peito de Peru com Aspargos", "descricao": "Peito de peru grelhado com aspargos, uma opção magra e saudável.", "calorias": 500, "refeicao": "jantar", "imagem": "miniatures/frangos-aspargos.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Peito de peru, aspargos, azeite, limão, sal, pimenta.", "modo_de_preparo": "Grelhe o peito de peru e os aspargos. Tempere com azeite, limão, sal e pimenta."},
        {"nome": "Wrap de Legumes Grelhados", "descricao": "Wrap vegetariano com legumes grelhados e molho de iogurte.", "calorias": 520, "refeicao": "almoco", "imagem": "miniatures/wrap-vegetariano.jpeg", "tempo_de_preparo": "15 minutos", "ingredientes": "Tortilla integral, abobrinha, cenoura, pimentão, iogurte.", "modo_de_preparo": "Grelhe os legumes e monte o wrap com molho de iogurte."},
        {"nome": "Smoothie de Maçã e Canela", "descricao": "Smoothie energético com maçã, banana e toque de canela.", "calorias": 400, "refeicao": "cafe_da_tarde", "imagem": "miniatures/suco-de-maçã-com-canela.jpg", "tempo_de_preparo": "7 minutos", "ingredientes": "Maçã, banana, leite, canela, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura suave."},
        {"nome": "Salada de Camarão", "descricao": "Salada fresca com camarões, abacate e molho de limão.", "calorias": 600, "refeicao": "almoco", "imagem": "miniatures/salada-atum.jpg", "tempo_de_preparo": "25 minutos", "ingredientes": "Camarões cozidos, abacate, alface, tomate cereja, limão, azeite, sal.", "modo_de_preparo": "Misture os camarões com os vegetais. Adicione abacate, regue com molho de limão."},
        {"nome": "Macarrão de Abobrinha com Frango", "descricao": "Macarrão de abobrinha com pedaços de frango, uma opção baixa em carboidratos.", "calorias": 480, "refeicao": "jantar", "imagem": "miniatures/macarrao_com_frango.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Abobrinha, peito de frango, molho de tomate, alho, azeite.", "modo_de_preparo": "Faça macarrão de abobrinha e misture com frango, molho de tomate e alho."},
        {"nome": "Smoothie de Pera e Espinafre", "descricao": "Smoothie saudável com pera, espinafre e toque de gengibre.", "calorias": 350, "refeicao": "cafe_da_tarde", "imagem": "miniatures/suco-de-maracuja.jpg", "tempo_de_preparo": "8 minutos", "ingredientes": "Pera, espinafre, gengibre, iogurte.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura suave."},
        {"nome": "Hambúrguer de Frango", "descricao": "Hambúrguer de frango grelhado com guacamole, uma opção leve e saborosa.", "calorias": 550, "refeicao": "almoco", "imagem": "miniatures/hamburguer-frango.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Peito de frango moído, abacate, tomate, cebola, alface.", "modo_de_preparo": "Grelhe o hambúrguer de frango e monte com guacamole e vegetais."},
        {"nome": "Salada de Lentilhas com Feta", "descricao": "Salada de lentilhas com queijo feta, uma opção rica em proteínas e fibras.", "calorias": 450, "refeicao": "jantar", "imagem": "miniatures/salada-de-lentilhas.jpg", "tempo_de_preparo": "25 minutos", "ingredientes": "Lentilhas cozidas, queijo feta, pepino, tomate, azeite, limão.", "modo_de_preparo": "Misture as lentilhas com os vegetais. Adicione queijo feta e tempere."},
        {"nome": "Tacos de Peixe", "descricao": "Tacos leves com peixe grelhado, repolho roxo e molho de iogurte.", "calorias": 500, "refeicao": "almoco", "imagem": "miniatures/dois-tacos.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Filé de peixe, tortillas de milho, repolho roxo, molho de iogurte.", "modo_de_preparo": "Grelhe o peixe e monte os tacos com repolho roxo e molho de iogurte."},
        {"nome": "Smoothie de Kiwi e Coco", "descricao": "Smoothie tropical com kiwi, coco e água de coco.", "calorias": 380, "refeicao": "cafe_da_tarde", "imagem": "miniatures/kiwi-coco.jpg", "tempo_de_preparo": "8 minutos", "ingredientes": "Kiwi, coco ralado, água de coco, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura suave."},
        {"nome": "Bruschetta de Tomate e Manjericão", "descricao": "Bruschettas leves com tomate fresco e manjericão.", "calorias": 350, "refeicao": "jantar", "imagem": "miniatures/brusqueta.jpeg", "tempo_de_preparo": "15 minutos", "ingredientes": "Pão integral, tomate, manjericão, alho, azeite.", "modo_de_preparo": "Toste o pão e cubra com tomate, manjericão, alho e azeite."},
        {"nome": "Salada de Quinoa com Manga", "descricao": "Salada de quinoa com manga, uma opção tropical e nutritiva.", "calorias": 480, "refeicao": "almoco", "imagem": "miniatures/salada_quinoa.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Quinoa cozida, manga, rúcula, cebola roxa, azeite, limão.", "modo_de_preparo": "Misture a quinoa com os vegetais. Adicione manga e tempere."},
        {"nome": "Sanduíche de Frango Grelhado", "descricao": "Sanduíche saudável com frango grelhado, abacate e tomate.", "calorias": 550, "refeicao": "cafe_da_tarde", "imagem": "miniatures/frangos-aspargos.jpg", "tempo_de_preparo": "15 minutos", "ingredientes": "Peito de frango, pão integral, abacate, tomate, alface.", "modo_de_preparo": "Grelhe o frango e monte o sanduíche com os ingredientes."},
        {"nome": "Smoothie de Manga e Hortelã", "descricao": "Smoothie refrescante com manga, hortelã e iogurte.", "calorias": 350, "refeicao": "jantar", "imagem": "miniatures/smoothie_manga_aveia.jpg", "tempo_de_preparo": "8 minutos", "ingredientes": "Manga, hortelã, iogurte, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura suave."},
        {"nome": "Salada Caprese", "descricao": "Salada clássica caprese com tomate, mussarela de búfala e manjericão.", "calorias": 400, "refeicao": "almoco", "imagem": "miniatures/salada_caprese.jpg", "tempo_de_preparo": "15 minutos", "ingredientes": "Tomate, mussarela de búfala, manjericão, azeite, balsâmico.", "modo_de_preparo": "Arrume os ingredientes em um prato. Regue com azeite e balsâmico."},
        {"nome": "Tigela de Frutas com Iogurte", "descricao": "Tigela refrescante com frutas variadas e iogurte.", "calorias": 300, "refeicao": "cafe_da_tarde", "imagem": "miniatures/tijela_frutas.jpg", "tempo_de_preparo": "10 minutos", "ingredientes": "Morango, kiwi, abacaxi, iogurte, granola.", "modo_de_preparo": "Corte as frutas e coloque em uma tigela. Adicione iogurte e granola."},
        {"nome": "Sopa de Abóbora", "descricao": "Sopa cremosa de abóbora com um toque de gengibre.", "calorias": 350, "refeicao": "jantar", "imagem": "miniatures/sopa_abobora.jpg", "tempo_de_preparo": "25 minutos", "ingredientes": "Abóbora, cebola, alho, gengibre, caldo de legumes.", "modo_de_preparo": "Cozinhe os ingredientes e bata no liquidificador até obter um creme."},
        {"nome": "Bowl de Frango com Quinoa", "descricao": "Bowl saudável com frango grelhado, quinoa, abacate e vegetais.", "calorias": 520, "refeicao": "almoco", "imagem": "miniatures/frango_quinoa.jpg", "tempo_de_preparo": "30 minutos", "ingredientes": "Peito de frango, quinoa, abacate, cenoura, brócolis.", "modo_de_preparo": "Grelhe o frango e prepare os ingredientes. Monte o bowl com todos os elementos."},
        {"nome": "Smoothie de Melão e Manjericão", "descricao": "Smoothie refrescante com melão, manjericão e iogurte.", "calorias": 320, "refeicao": "cafe_da_tarde", "imagem": "miniatures/smoothie.jpg", "tempo_de_preparo": "7 minutos", "ingredientes": "Melão, manjericão, iogurte, mel.", "modo_de_preparo": "Bata todos os ingredientes no liquidificador até obter uma mistura suave."},
        {"nome": "Salada de Cuscuz", "descricao": "Salada de cuscuz com grão-de-bico, tomate e hortelã.", "calorias": 450, "refeicao": "jantar", "imagem": "miniatures/Salada-cuscuz.jpg", "tempo_de_preparo": "20 minutos", "ingredientes": "Cuscuz, grão-de-bico cozido, tomate, hortelã, azeite, limão.", "modo_de_preparo": "Misture o cuscuz com os vegetais. Adicione grão-de-bico e tempere."},
        {"nome": "Sanduíche Aberto de Abacate", "descricao": "Sanduíche saudável e delicioso com abacate, tomate e ovo pochê.", "calorias": 480, "refeicao": "almoco", "imagem": "miniatures/sanduiche-abacate.jpg", "tempo_de_preparo": "15 minutos", "ingredientes": "Pão integral, abacate, tomate, ovo, azeite.", "modo_de_preparo": "Toste o pão e cubra com abacate, tomate e ovo pochê. Regue com azeite."},
        {"nome": "Wrap de Salmão Defumado", "descricao": "Wrap leve com salmão defumado, cream cheese e rúcula.", "calorias": 420, "refeicao": "cafe_da_tarde", "imagem": "miniatures/wrap_salmao.jpg", "tempo_de_preparo": "12 minutos", "ingredientes": "Tortilla integral, salmão defumado, cream cheese, rúcula.", "modo_de_preparo": "Espalhe cream cheese na tortilla e adicione salmão e rúcula. Enrole o wrap."},
    ]

    for receita_data in receitas:
        nova_receita = Receita(**receita_data, categoria="cutting")
        db.session.add(nova_receita)

    db.session.commit()
    return redirect(url_for('receitas'))

if __name__ == '__main__':
    app.run()
