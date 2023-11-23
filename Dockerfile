# Use a imagem oficial do Python
FROM python:3.7.3

# Create a non-root user
RUN useradd -m myuser

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos necessários para o contêiner
COPY requirements.txt .
COPY app /app

# Instale as dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponha a porta em que a aplicação está sendo executada
EXPOSE 5000

# Configure a variável de ambiente do Flask
ENV FLASK_APP=app.py

# Comando para executar a aplicação quando o contêiner for iniciado
CMD ["flask", "run", "--host=0.0.0.0"]
