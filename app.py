from flask import Flask, render_template, url_for, redirect, jsonify, request, session
from sqlalchemy import Column, Integer, String
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
global cadastrar
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///protocolo.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] =  'CHA1321'

class Funcionario(db.Model):
    id_func=Column(Integer, primary_key=True, autoincrement=True)
    nomeUsuario = Column(String)
    senha = Column(String)

    def __init__(self, nomeUsuario, senha):
        self.nomeUsuario = nomeUsuario
        self.senha=senha

class Protocolo(db.Model):
    numero      = Column(Integer, primary_key=True, autoincrement=True)
    assunto     = Column(String)
    data        = Column(String)
    responsavel = Column(String)

    def __init__(self, assunto, data, responsavel):
        self.assunto=assunto
        self.data=data
        self.responsavel=responsavel

with app.app_context():
    db.create_all()
  
  
#=======autenticação=======
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField
from wtforms.validators import input_required
from flask_jwt_extended import JWTManager

jwt=JWTManager(app)

class FormLogin(FlaskForm):
    nomeUsuario= StringField("nome de usuario", validators=[input_required()])
    senha = PasswordField("senha", validators=[input_required()])

class FormProtocolo(FlaskForm):
    idProtoc = HiddenField('ID Protocolo')
    assunto = StringField("assunto", validators=[input_required()])
    dat = StringField("data", validators=[input_required()])

@app.route('/', methods=['GET', 'POST'])
def index():
    formLogin = FormLogin()
    if formLogin.validate_on_submit():
        
        nomeUsuario = formLogin.nomeUsuario.data
        
        senha = formLogin.senha.data
               
        return autenticacao(nomeUsuario, senha)
    return render_template('index.html', form = formLogin, login=True)
@app.route('/logout/')
def logout():
    session['funcionario']=None
    return redirect('/')

def autenticacao(nomeUsuario, senha):
    users=recuperaUsuarios()
    if nomeUsuario in users and users[nomeUsuario]==senha:
        session['responsavel'] = nomeUsuario
        return redirect(url_for('visual_protocolo'))
    else:
        return f'usuário ou senha inválida, tente novamente' 

def recuperaUsuarios():
    users = db.session.query(Funcionario).all() 
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
        func = Funcionario(nome, senha)

        db.session.add(func)
        db.session.commit()
        return render_template('index.html', form=formCadastro, login=True)
    return render_template('index.html', form=formCadastro)
#==========protocolos=========
@app.route('/visual_protocolo')
def visual_protocolo():
    form_protocolo = FormProtocolo()
    protocoloDict=prot_dict()
    return render_template("visual_protocolo.html", prot_dicts=protocoloDict, formProtoc = form_protocolo, cadastrar=True)

@app.route('/cad_protocolo/', methods=['POST'])
def cad_protocolo():
    form_protocolo = FormProtocolo()
    
    if form_protocolo.validate_on_submit():
        assunto = form_protocolo.assunto.data
        data =  form_protocolo.dat.data
        responsavel=session['responsavel']
        print(session['responsavel'])
        protocolo = Protocolo(assunto, data, responsavel)

        db.session.add(protocolo)
        db.session.commit()
        
    return redirect(url_for('visual_protocolo'))

@app.route('/edit_protocolo/', methods=['GET', 'POST'])
def edit_protocolo():
    form_protocolo = FormProtocolo()
    idProtoc = request.args.get('idProtoc')
    protocolo = db.session.query(Protocolo).filter_by(numero=idProtoc).first() 
    if request.method=='POST':
        if form_protocolo.validate_on_submit():
            #captura os dados digitados e validados do formulário
            assunto = form_protocolo.assunto.data
            data =  form_protocolo.dat.data
            #atualiza os dados do objeto pelos dados novos
            protocolo.assunto=assunto
            protocolo.data=data
            #insere na seção e depois no banco
            db.session.add(protocolo)
            db.session.commit()            
        return redirect(url_for('visual_protocolo'))
         
    form_protocolo.idProtoc.data = idProtoc

    prot_dicts=prot_dict()
    #agora como eu faço para jogar esses dados [assunto, data] do protoc, nos campos input do formulário
    if idProtoc != None:
        form_protocolo.assunto.data = protocolo.assunto
        form_protocolo.dat.data = protocolo.data
        cadastrar=False
    else:
        cadastrar=True
    return render_template('visual_protocolo.html', protoc=protocolo, prot_dicts=prot_dicts, formProtoc=form_protocolo, cadastrar=cadastrar)
    
def prot_dict():
    protocolos = db.session.query(Protocolo).all()
    protocoloDict={}
    for protocolo in protocolos:
        protocoloDict[protocolo.numero]={"assunto":protocolo.assunto, "data":protocolo.data, "responsavel":protocolo.responsavel}
    return protocoloDict


if __name__ == "__main__":
    app.run(debug=True)
