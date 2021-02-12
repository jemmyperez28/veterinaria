from flask import Blueprint
from flask_app import cross_origin
from flask import jsonify
from funciones.funciones import requires_auth
from flask import request
from sqlalchemy import exc
from config.db import db

from models import Pet
from schemas import PetSchema

Pet_Schema = PetSchema()
Pets_Schema = PetSchema(many=True)
pets = Blueprint('pets', __name__)



#Pets
@pets.route('/pets', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_pet():
    name = request.json['name']
    birthdate = request.json['birthdate']    
    color = request.json['color']
    bread = request.json['bread']
    owner = request.json['owner']  
    photo = request.json['photo']
    nuevo_pet = Pet(name,birthdate,color,bread,photo,owner)

    try:
        db.session.add(nuevo_pet)
        db.session.commit()
        response = {
                'code': '0',
                'message': 'OK',
                'signature': 'Se Agrego el Pet ' + str(name) + ' Del Dueno ' + str(owner) 
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

@pets.route('/pets/<id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_pet(id):
    pet = Pet.query.get(id)
    result = Pet_Schema.dump(pet)
    return jsonify(result)


@pets.route('/pets/<id>', methods=['PUT'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def update_pet(id):
    pet = Pet.query.get(id)
    name = request.json['name']
    birthdate = request.json['birthdate']    
    color = request.json['color']
    bread = request.json['bread']

    #actualizo campos
    pet.name = name
    pet.birthdate = birthdate
    pet.color = color
    pet.bread = bread

    try:
        db.session.commit()
        response = {
                'code': '0',
                'message': 'OK',
                'signature': 'Se Actualizo la Mascota con id' + str(pet)
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