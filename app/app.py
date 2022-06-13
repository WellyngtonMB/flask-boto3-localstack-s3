import os
import boto3
import json
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads'  # pasta onde será salvo o arquivo que será enviado para o S3
DOWNLOAD_FOLDER = './downloads'  # pasta onde será salvo o arquivo que será baixado do S3
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # extensões permitidas

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')  # chave de acesso do AWS
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')  # chave de secreta do AWS
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION') # região do AWS
BUCKET_NAME = os.environ.get('BUCKET_NAME')  # nome do bucket
AWS_URL = os.environ.get('AWS_URL')


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# verifica se o arquivo é permitido
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# upload do arquivo
@app.route('/upload', methods=['POST'])
def upload_file(): 
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 400
        file = request.files['file']
        if file.filename == '':            
            return jsonify({'message': 'No file selected for uploading'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) # Craia um nome seguro para o arquivo
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) # Define o caminho que sera salvo o arquivo
            file.save(file_path) # Salva o arquivo localmente
            # Cria a conexão com o S3 (localstack ou aws))
            s3 = boto3.client('s3', endpoint_url=AWS_URL, region_name=AWS_DEFAULT_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            # Envia o arquivo para o S3
            s3.upload_file(file_path, BUCKET_NAME, filename)
            # Verifica se a key idKey é passada
            if 'idKey' not in request.form:
                return jsonify(message='File successfully uploaded'), 201

            # Caso seja enviado do um json junto a requisição, deve ser feito passando através key 'idKey'
            # Modifique o código abaixo para realizar as ações necessárias com o json enviado
            teste_json = json.loads(request.form['idKey']) # Carrega o id do usuário
            teste = teste_json['teste'] # Passa o valor teste para a variável teste
            return jsonify(message='File successfully uploaded', teste=teste), 201
        return jsonify(message='File not allowed'), 400
    except:
        # Caso ocorra algum erro, retorna o erro
        return jsonify(message='Internal Server Error'), 500

# download do arquivo
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        #  file_path - Define o caminho que sera salvo o arquivo
        file_path = app.config['DOWNLOAD_FOLDER'] + '/' + filename
        # Cria a conexão com o S3 (localstack ou aws))
        s3 = boto3.client('s3', endpoint_url=AWS_URL, region_name=AWS_DEFAULT_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        # Baixa o arquivo do S3
        s3.download_file(BUCKET_NAME, filename, file_path)
        # Retorna o arquivo baixado do S3 para o cliente
        return send_file(file_path)
    except:
        # Retorna erro ao cliente
        return jsonify(message='Internal Server Error'), 500
