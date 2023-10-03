from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import re
import logging
from functools import wraps
from datetime import timedelta
from flask_migrate import Migrate
from datetime import datetime
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter


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

@app.route('/gerar_pdf/<int:receita_id>', methods=['GET'])
def gerar_pdf(receita_id):
    # Obtenha a receita do banco de dados
    receita = Receita.query.get(receita_id)

    # Crie um buffer de bytes para armazenar o PDF
    buffer = BytesIO()

    # Crie o PDF usando o ReportLab
    p = canvas.Canvas(buffer)

    # Adicione o nome da receita ao título do PDF
    p.setTitle(receita.nome)

    # Adicione informações ao PDF
    p.drawString(100, 800, f"Nome: {receita.nome}")
    p.drawString(100, 780, f"Descrição: {receita.descricao}")
    p.drawString(100, 760, f"Calorias: {receita.calorias}")
    p.drawString(100, 740, f"Categoria: {receita.categoria}")
    p.drawString(100, 720, f"Refeição: {receita.refeicao}")
    p.drawString(100, 700, f"Tempo de Preparo: {receita.tempo_de_preparo}")

     # Adicione ingredientes ao PDF
    p.drawString(100, 680, "Ingredientes:")
    ingredientes = receita.ingredientes.split('\n') if receita.ingredientes else []
    y_position = 660
    for ingrediente in ingredientes:
        p.drawString(120, y_position, ingrediente)
        y_position -= 20

    # Adicione modo de preparo ao PDF
    p.drawString(100, y_position, "Modo de Preparo:")
    modo_de_preparo = receita.modo_de_preparo.split('\n') if receita.modo_de_preparo else []
    y_position -= 20
    for passo in modo_de_preparo:
        p.drawString(120, y_position, passo)
        y_position -= 20

    # Adicione uma imagem ao PDF
    if receita.imagem:
        image_path = f"static/{receita.imagem}"  # Certifique-se de ajustar o caminho conforme necessário
        p.drawInlineImage(image_path, 100, 400, width=200, height=200)

    # Salve o PDF
    p.save()

    # Defina o ponteiro do buffer no início
    buffer.seek(0)

    # Crie uma resposta Flask com o PDF
    response = make_response(buffer.read())
    response.mimetype = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={receita.nome}.pdf'

    return response

@app.route('/dashboard/receitas')
def receitas_bulking():
    categoria_filtrada = request.args.get('categoria', default=None, type=str)
    refeicao_filtrada = request.args.get('refeicao', default=None, type=str)
    calorias_max = request.args.get('calorias_max', default=None, type=int)

    query = Receita.query

    if categoria_filtrada:
        query = query.filter_by(categoria=categoria_filtrada)

    if refeicao_filtrada:
        query = query.filter_by(refeicao=refeicao_filtrada)

    if calorias_max is not None:
        query = query.filter(Receita.calorias <= calorias_max)

    receitas = query.all()

    return render_template('receitas.html', receitas=receitas)

@app.route('/adicionar-bulking')
def add_example_recipes():
    # Adicione algumas receitas de exemplo
    receitas = [
        {"nome": "Bulking 1 SALADA MISTA COM PEIXE", "descricao": "Receita para bulking com 2300 kcal enrolado de carne", "calorias": 2300, "refeicao": "cafe_da_manha", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "15 minutos", "ingredientes": "1 xicara de sal, 2 colheres de sopa, 3kg de carne, 80 litros de agua.", "modo_de_preparo": "Coloque 1 xixara no bool, mexa por 15 segundos, 30 segundos no microondas."},
        {"nome": "Bulking 2 Arroz, file e frango a passarinho", "descricao": "Receita para bulking com 2500 kcal", "calorias": 2500, "refeicao": "jantar", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "15 minutos"},
        {"nome": "Bulking 3", "descricao": "Receita para bulking com 2700 kcal", "calorias": 2700, "refeicao": "almoco", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "5 minutos"},
        {"nome": "Bulking 4", "descricao": "Receita para bulking com 3000 kcal", "calorias": 3000, "refeicao": "jantar", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "5 minutos"},
        {"nome": "Bulking 5", "descricao": "Receita para bulking com 3300 kcal", "calorias": 3300, "refeicao": "almoco", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "7 minutos"},
        {"nome": "Bulking 6", "descricao": "Receita para bulking com 3500 kcal", "calorias": 3500, "refeicao": "almoco", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "12 minutos"},
        {"nome": "Bulking 7", "descricao": "Receita para bulking com 3800 kcal", "calorias": 3800, "refeicao": "almoco", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "13  minutos"},
        {"nome": "Bulking 8", "descricao": "Receita para bulking com 4000 kcal", "calorias": 4000, "refeicao": "jantar", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "1 minuto"},
        {"nome": "Bulking 9", "descricao": "Receita para bulking com 4500 kcal", "calorias": 4500, "refeicao": "cafe_da_tarde", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "5 minutos"},
        {"nome": "Bulking 10", "descricao": "Receita para bulking com 5000 kcal", "calorias": 5000, "refeicao": "cafe_da_tarde", "imagem": "miniatures/imagem1.jpg", "tempo_de_preparo": "15 minutos"},
] 

    for receita_data in receitas:
        nova_receita = Receita(**receita_data, categoria="bulking")
        db.session.add(nova_receita)

    db.session.commit()
    return redirect(url_for('receitas'))
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

# Configurar o log para escrever em um arquivo
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s [%(levelname)s] - %(message)s')

if __name__ == '__main__':
    app.run()
