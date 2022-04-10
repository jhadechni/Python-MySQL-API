from logging import exception
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, render_template,request
from flask_marshmallow import Marshmallow


#Creating flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/votacion5G'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

#Creating database models
#Model for Votante
class Votante(db.Model):
    id_votante = db.Column(db.Integer,primary_key=True)
    name_votante = db.Column(db.String(70))
    apellidos_votante = db.Column(db.String(70))
    tipo_documento = db.Column(db.String(70))
    num_documento = db.Column(db.String(70),unique=True)
    localidad_votante = db.Column(db.String(70))
    votos = db.Column(db.Integer)

    def __init__(self,name_votante,apellidos_votante,tipo_documento,num_documento,localidad_votante,votos):
        self.name_votante = name_votante
        self.apellidos_votante = apellidos_votante
        self.tipo_documento = tipo_documento
        self.num_documento = num_documento
        self.localidad_votante = localidad_votante
        self.votos = votos

#Model for Candidato
class Candidato(db.Model):
    id_candidato = db.Column(db.Integer,primary_key=True)
    name_candidato = db.Column(db.String(70))
    partido = db.Column(db.String(70))
    localidad_candidato = db.Column(db.String(70))

    def __init__(self,name_candidato,partido,localidad_candidato):
        self.name_candidato = name_candidato
        self.partido = partido
        self.localidad_candidato = localidad_candidato

#Model for Voto
class Voto(db.Model):
    id_voto = db.Column(db.Integer,primary_key=True)
    candidato = db.Column(db.Integer,nullable=False)
    votante = db.Column(db.Integer,nullable=False)

    def __init__(self,candidato,votante):
        self.candidato = candidato
        self.votante = votante
       
db.create_all()

#Schemas
class VotanteSchema(ma.Schema):
    class Meta:
        fields = ('id_votante','name_votante','apellidos_votante','tipo_documento','num_documento','localidad_votante','votos')

votante_schema = VotanteSchema()
votantes_schema = VotanteSchema(many=True)

class CandidatoSchema(ma.Schema):
    class Meta:
        fields = ('id_candidato','name_candidato','partido','localidad_candidato')

candidato_schema = CandidatoSchema()
candidatos_schema = CandidatoSchema(many=True)

class VotoSchema(ma.Schema):
    class Meta:
        fields = ('candidato','votante')

voto_schema = VotoSchema()
votos_schema = VotoSchema(many=True)

#Index Route
@app.route('/' , methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/newVotante', methods=['GET'])
def new_votante():
    return render_template("votante.html")


@app.route('/api/newVotante', methods=['POST'])
def create_votante():
    try:
        name = request.form['name_votante']
        apellidos = request.form['apellidos_votante']
        tipo_documento = request.form['tipo_documento']
        num = request.form['num_documento']
        localidad = request.form['localidad_votante']
        n_votante = Votante(name,apellidos,tipo_documento,num,localidad,0)
        db.session.add(n_votante)
        db.session.commit()
        return votante_schema.jsonify(n_votante),200
    except Exception:
        exception(f"[SERVER]: Error --->")
        return jsonify({"msg" : "Error"}),500
    

@app.route('/newCandidato',methods=['GET'])
def new_candidato():
    return render_template("candidato.html")


@app.route('/api/newCandidato',methods=['POST'])
def create_candidato():
    try:
        name = request.form['name_candidato']
        partido = request.form['partido']
        localidad = request.form['localidad_candidato']
        n_candidato = Candidato(name,partido,localidad)
        db.session.add(n_candidato)
        db.session.commit()
        return candidato_schema.jsonify(n_candidato),200
    except Exception:
        exception(f"[SERVER]: Error --->")
        return jsonify({"msg" : "Error"}),500

@app.route('/votar',methods=['GET'])
def votar_view():
    return render_template("voto.html")


@app.route('/api/votar',methods=['POST'])
def votar():
    try:
        votanten = request.form['votante_id']
        candidaton = request.form['candidato_id']
        if votanten and candidaton:
            existv = Votante.query.get(votanten)
            existc = Candidato.query.get(candidaton)
            if existv and existc:
                if existv.localidad_votante == existc.localidad_candidato:
                    if existv.votos == 0:
                            db.session.query(Votante).filter(Votante.id_votante == votanten).update({'votos':Votante.votos + 1})
                            n_voto = Voto(votanten,candidaton)
                            db.session.add(n_voto)
                            db.session.commit()
                            return jsonify({"msg" : "Voto registrado!"}), 200
                    else: 
                        return jsonify({"msg" : "Ya voto previamente"}),500
                else:
                    return jsonify({"msg" : "No tienen la misma localidad!"}),500
             
            else: 
                    return jsonify({"msg" : "No existen"}),500
        else: 
            return jsonify({"msg" : "Debe rellenar los campos"}),500
    except Exception:
        exception(f"[SERVER]: Error --->")
        return jsonify({"msg" : "Error"}),500



if __name__ == "__main__":
    app.run(debug=True)