from flask import Blueprint
from flask_app import cross_origin
from flask import jsonify
from funciones.funciones import requires_auth
from flask import request
from sqlalchemy import exc
from config.db import db

from models import Services
from schemas import ServiceSchema

Service_Schema = ServiceSchema()
Services_Schema = ServiceSchema(many=True)

services = Blueprint('services', __name__)

#Servicios     
@services.route('/servicios', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_servicio():

    idvet = request.json['idvet']
    tipo = request.json['tipo']
    nombre = request.json['nombre']
    precio = request.json['precio']
    foto = request.json['foto']
    nuevo_servicio = Services(idvet,tipo,nombre,precio,foto)
                       
    try:
        db.session.add(nuevo_servicio)
        db.session.commit()
        response = {
                'code': '0',
                'message': 'OK',
                'signature': 'Se Agrego el Servicio ' + nombre 
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

#SERVICIOS DE LA VETERINARIA POR ID
@services.route('/servicios/<id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_servicios(id):
    servicess = Services.query.with_entities(Services.id,Services.idvet,Services.tipo,Services.nombre,Services.precio,Services.foto).filter_by(idvet=id)
    result = Services_Schema.dump(servicess)
    return jsonify(result)

@services.route('/servicios/<id>', methods=['PUT'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def update_servicio(id):
    servicio = Services.query.get(id)
    tipo = request.json['tipo']
    nombre = request.json['nombre']
    precio = request.json['precio']
    foto = request.json['foto']

    #actualizo campos
    servicio.tipo = tipo
    servicio.nombre = nombre
    servicio.precio = precio
    servicio.foto = foto
    try:
        db.session.commit()
        response = {
                'code': '0',
                'message': 'OK',
                'signature': 'Se Actualizo el Servicio con id ' + str(servicio) + str(nombre)
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

@services.route('/servicios/<id>', methods=['DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def delete_servicio(id):
    servicio = Services.query.get(id)
    try:
        db.session.delete(servicio)
        db.session.commit()
        response = {
                'code': '0',
                'message': 'OK',
                'signature': 'Se Elimino el Servicio con id ' + str(servicio) 
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
