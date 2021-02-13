from flask import Blueprint
from flask_app import cross_origin
from flask import jsonify
from funciones.funciones import requires_auth
from flask import request 
from sqlalchemy import exc
from config.db import db
from config.keys import INIT_KEY



from models import Usuario
from schemas import UsuarioSchema

Usuario_Schema = UsuarioSchema()
Usuarios_Schema = UsuarioSchema(many=True)

usuarios = Blueprint('usuarios', __name__)


@usuarios.route('/api/public')
@cross_origin(headers=["Content-Type", "Authorization"])
def public():
    response = "Hello from a public endpoint! You don't need to be authenticated to see this."
    return jsonify(message=response)

@usuarios.route('/api/private')
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def private():
    response = "Hello from a private endpoint! You need to be authenticated to see this."
    return jsonify(message=response)


#Usuarios

@usuarios.route('/usuarios/new_user_public', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
def new_user_public():

    r = request.headers['Authorization']

    if r == "Bearer " + str(INIT_KEY):
        name = request.json['name']
        email = request.json['email']
        auth0id = request.json['auth0id']
        role = request.json['role']
        phone = None
        pais = None
        provincia = None
        ciudad = None 
        distrito = None 
        direccion = None 
        fecha_registro = None
        nuevo_usuario = Usuario(name,email,phone,pais,provincia,ciudad,distrito,direccion,role,fecha_registro,auth0id)
        
                        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            response = {
                    'code': '0',
                    'message': 'OK',
                    'signature': 'Se Agrego el Usuario con ID ' + auth0id  
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
    else:
        response = {
                    'code': '0',
                    'message': 'ERROR',
                    'signature': 'TOKEN INICIAL INVALIDO'  
                }
        return jsonify(message=response)


#Usuarios
@usuarios.route('/usuarios', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_usuario():

    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    pais = request.json['pais']
    provincia = request.json['provincia']
    ciudad = request.json['ciudad'] 
    distrito = request.json['distrito']
    direccion = request.json['direccion']
    role = request.json['role']
    fecha_registro  = request.json['fecha_registro'] 
    auth0id = request.json['auth0id']
    nuevo_usuario = Usuario(name,email,phone,pais,provincia,ciudad,distrito,direccion,role,fecha_registro,auth0id)
                       
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        response = {
                'code': '0',
                'message': 'OK',
                'signature': 'Se Agrego el Usuario ' + email 
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


@usuarios.route('/usuarios' , methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_usuarios():
        all_usuarios = Usuario.query.all()
        result = Usuarios_Schema.dump(all_usuarios)
        return jsonify(result)

@usuarios.route('/usuarios/<id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_usuario(id):
    usuario = Usuario.query.get(id)
    result = Usuario_Schema.dump(usuario)
    return jsonify(result)


@usuarios.route('/usuarios/<id>', methods=['PUT'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def update_usuario(id):
    user = Usuario.query.get(id)
    name = request.json['name']
    phone = request.json['phone']
    pais = request.json['pais']
    provincia = request.json['provincia']
    ciudad = request.json['ciudad'] 
    distrito = request.json['distrito']
    direccion = request.json['direccion']
    role = request.json['role']

    #actualizo campos
    user.name = name
    user.phone = phone
    user.pais = pais
    user.provincia = provincia
    user.ciudad = ciudad
    user.distrito = distrito
    user.direccion = direccion
    user.role = role
    try:
        db.session.commit()
        response = {
                'code': '0',
                'message': 'OK',
                'signature': 'Se Actualizo el Usuario con id ' + str(user)
            }
        return jsonify(message=response)
    except exc.SQLAlchemyError as e:
        mensaje = (str(e))
        response = {
                'code': '-1',
                'message': 'Error',
                'signature': mensaje 
            }
        return jsonify(message=response)



@usuarios.route('/usuarios/<id>', methods=['DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def delete_usuario(id):
    user = Usuario.query.get(id)
    try:
        db.session.delete(user)
        db.session.commit()
        response = {
                'code': '0',
                'message': 'OK',
                'signature': 'Se Elimino el Usuario con id ' + str(user)
            }
        return jsonify(message=response)
    except exc.SQLAlchemyError as e:
        mensaje = (str(e))
        response = {
                'code': '-1',
                'message': 'Error',
                'signature': mensaje 
            }
        return jsonify(message=response)