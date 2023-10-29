# FlexiFitness


## 🧠 Sobre

Flexi Fitness é uma plataforma que combina Engenharia de Software e saúde, proporcionando aos usuários ferramentas poderosas para um estilo de vida saudável. Melhore sua qualidade de vida com o Flexi Fitness. 

Hoje, mais do que nunca, é essencial tornar a saúde e o bem-estar acessíveis a todos. A Flexi Fitness é a resposta a esse desafio, capacitando as pessoas a conquistar uma vida mais saudável, mais ativa e mais feliz. Junte-se a nós nessa jornada emocionante para alcançar o seu melhor você!

## 🔥 Como rodar a aplicação 
Criação do banco de dados usando PostgreSQL:
1. Abra o banco padrão "psql -U 'usuário do banco'"
2. create database flexifitness;

Comandos para baixar todos os pacotes necessários:
1. Faça o clone da aplicação.
2. "cd NOME_DO_DIRETORIO".
3. python3.7 -mvenv venv
4. venv/bin/pip install -r requirements.txt
5. cp .env.example .env
6. Inicie a aplicação usando "python app.py"
7. Abra um navegador da web e vá para http://localhost:5000

Você deve conseguir rodar um servidor/aplicação de testes.

## 🔥 Como rodar a aplicação via Docker

Lembre-se de já ter baixado e instalado corretamente o docker em sua máquina!

Dentro do projeto digite os seguintes comandos:
1. docker build -t meu_projeto:latest .
2. docker run -p 5000:5000 meu_projeto:latest
3. Sua aplicação Flask deve agora estar acessível em http://localhost:5000

## 🔥 Pacotes e dependências

alembic==1.12.0

Flask==2.2.5

Flask_Bcrypt==1.0.1

Flask_Migrate==4.0.5

flask_sqlalchemy

reportlab

SQLAlchemy

weasyprint==60.1

psycopg2 ==2.9.5

psycopg2-binary ==2.9.5

gunicorn

## 🔥 Documentação

## 🔥 Further Help

Se você precisa de mais ajuda, olhe a documentação necessária dos pacotes que podem estar gerando o problema. Segue algumas que podem lhe ajudar:

Alembic (Migrações de Banco de Dados):
[Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)

Flask (Framework Web):
[Flask Documentation](https://flask.palletsprojects.com/en/3.0.x/)

Flask-Bcrypt (Criptografia de Senhas no Flask):
[Bcrypt Documentation](https://flask-bcrypt.readthedocs.io/en/1.0.1/)

Flask-Migrate (Extensão para Migrações no Flask):
[Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/en/latest/)

Flask-SQLAlchemy (Extensão para Integração do SQLAlchemy com Flask):
[SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/)

ReportLab (Criação de PDFs com Python):
[ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)

SQLAlchemy (Biblioteca de SQL para Python):
[SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/)

WeasyPrint (Renderização de HTML para PDF em Python):
[WeasyPrint Documentation](https://weasyprint.readthedocs.io/)

Psycopg2 (Driver PostgreSQL para Python):
[Psycopg2 Documentation](https://www.psycopg.org/docs/)

Gunicorn (Servidor Web HTTP para WSGI):
[Gunicorn Documentation](https://docs.gunicorn.org/en/stable/)


