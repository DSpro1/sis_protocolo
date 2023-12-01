from flask import Flask, render_template, url_for, redirect, jsonify, request
from sqlalchemy import Column, Integer, String
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///protocolo.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] =  'CHA1321'

class Administrador(db.Model):
    id_adm=Column(Integer, primary_key=True, autoincrement=True)
    nomeUsuario = Column(String)
    senha = Column(String)


    def __init__(self, nomeUsuario, senha):
        self.nomeUsuario = nomeUsuario
        self.senha=senha

class Protocolo(db.Model):
    numero= Column(Integer, primary_key=True, autoincrement=True)
    assunto = Column(String)
    data=Column(String)

    def __init__(self, assunto, data):
        self.assunto=assunto
        self.data=data

with app.app_context():
    db.drop_all()
    db.create_all()
  
#=======autenticação=======
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import input_required
from flask_jwt_extended import JWTManager

jwt=JWTManager(app)

class FormLogin(FlaskForm):
    nomeUsuario= StringField("nomeUsuario", validators=[input_required()])
    senha = StringField("senha", validators=[input_required()])

class FormProtocolo(FlaskForm):
    assunto = StringField("assunto", validators=[input_required()])
    data = StringField("data", validators=[input_required()])

@app.route('/', methods=['GET', 'POST'])
def index():
    formLogin = FormLogin()
    if formLogin.validate_on_submit(): #testado
        
        nomeUsuario = formLogin.nomeUsuario.data
        senha = formLogin.senha.data
               
        return autenticacao(nomeUsuario, senha)
    return render_template('index.html', form = formLogin, login=True)

def autenticacao(nomeUsuario, senha):
    users=recuperaUsuarios()
    if nomeUsuario in users and users[nomeUsuario]==senha:
        return redirect(url_for('visual_protocolo'))
    else:
        return f'usuário ou senha inválida, tente novamente' 

def recuperaUsuarios():
    users = db.session.query(Administrador).all() 
    users_dict={}
    for user in users:
        users_dict[user.nomeUsuario]=user.senha
    return users_dict

@app.route("/cadastra_usuario", methods=['GET', 'POST'])
def cadastraUsuario():
    formCadastro = FormLogin()
    if formCadastro.validate_on_submit():
        nome = formCadastro.nomeUsuario.data
        senha=formCadastro.senha.data
        adm = Administrador(nome, senha)
        db.session.add(adm)
        db.session.commit()
    return render_template('index.html', form=formCadastro)
#==========protocolos=========
@app.route('/visual_protocolo')
def visual_protocolo():
    protocolos = db.session.query(Protocolo).all()
    protocoloDict={}
    for protocolo in protocolos:
        protocoloDict[protocolo.numero]={"assunto":protocolo.assunto, "data":protocolo.data}
    return jsonify(protocoloDict)

@app.route('/cad_protocolo', methods=['GET', 'POST'])
def cad_protocolo():
    form_protocolo = FormProtocolo()
    
    if form_protocolo.validate_on_submit():
        assunto = form_protocolo.assunto.data
        data =  form_protocolo.data.data
        protocolo = Protocolo(assunto, data)
        db.session.add(protocolo)
        db.session.commit()
        return "cadastrado com sucesso"
        
    return render_template('/cadastraProtocolo.html', formProtoc = form_protocolo)

if __name__ == "__main__":
    app.run(debug=True)