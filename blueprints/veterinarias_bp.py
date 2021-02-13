from flask import Blueprint
from flask_app import cross_origin
from flask import jsonify
from funciones.funciones import requires_auth
from flask import request
from sqlalchemy import exc
from config.db import db
from funciones.funciones import decodificar_token

from models import Veterinaria , UserVet , Usuario
from schemas import VeterinariaSchema

Veterinaria_Schema = VeterinariaSchema()
Veterinarias_Schema = VeterinariaSchema(many=True)

veterinarias = Blueprint('veterinarias', __name__)


#Veterinaria
@veterinarias.route('/veterinarias', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_veterinaria():

    auth0cod = decodificar_token()
    id_usuario = Usuario.query.with_entities(Usuario.id).filter_by(auth0id=auth0cod)
    print(id_usuario)

    name = request.json['name']
    logo = request.json['logo']    
    ruc = request.json['ruc']
    telefono = request.json['telefono']
    whatsapp = request.json['whatsapp']  
    pais = request.json['pais'] 
    provincia = request.json['provincia'] 
    ciudad = request.json['ciudad'] 
    Distrito = request.json['Distrito'] 
    Address = request.json['Address'] 
    status = 1
    fecha_registro = None
    nuevo_veterinaria = Veterinaria(name,logo,ruc,telefono,whatsapp,pais,provincia,ciudad,Distrito,Address,status,fecha_registro)                           
    try:
        db.session.add(nuevo_veterinaria)
        db.session.flush()
        nuevo_uservet = UserVet(nuevo_veterinaria.id,id_usuario,'1')
        db.session.add(nuevo_uservet)
        db.session.flush()
        db.session.commit()
        response = {
                'code': '0',
                'message': 'OK',
                'signature': 'Se Agrego la Veterinaria ' + str(name) + 'Pertenece a Usuario:' + str(nuevo_uservet.iduser)
            }
        return jsonify(message=response)
    except exc.SQLAlchemyError as e:
        mensaje = (str(e))
        response = {
                'code': '-1',
                'message': 'Error',
                'signature': mensaje 
            }
        #return jsonify(message=response)
        return jsonify(message=response)

@veterinarias.route('/veterinarias' , methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_veterinarias():
        all_veterinarias = Veterinaria.query.all()
        result = Veterinarias_Schema.dump(all_veterinarias)
        return jsonify(result)

@veterinarias.route('/veterinarias/<id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_veterinaria(id):
    veterinaria = Veterinaria.query.get(id)
    result = Veterinaria_Schema.dump(veterinaria)
    return jsonify(result)

