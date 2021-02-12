from flask import Blueprint
from flask_app import cross_origin
from flask import jsonify
from funciones.funciones import requires_auth
from flask import request
from sqlalchemy import exc
from config.db import db

from models import UserVet
from schemas import UserVetSchema

UserVet_Schema = UserVetSchema
UserVets_Schema = UserVetSchema(many=True)

uservets = Blueprint('uservets', __name__)


#UserVet
#Veterinarias que pertenecen a un Usuario
@uservets.route('/uservet/<user_id>' , methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_uservets(user_id):
        uservets = UserVet.query.with_entities(UserVet.id,UserVet.iduser,UserVet.idvet).filter_by(iduser=user_id)
        result = UserVets_Schema.dump(uservets)
        return jsonify(result)