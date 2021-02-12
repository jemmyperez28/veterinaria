import json
from six.moves.urllib.request import urlopen
from functools import wraps
from flask import Flask, request, jsonify, _request_ctx_stack , abort
from flask_cors import cross_origin
from jose import jwt
from models import Usuario , Pet, Veterinaria, UserVet , Services
from config.db import db
from schemas import ma ,UsuarioSchema , PetSchema , VeterinariaSchema , UserVetSchema  , ServiceSchema
from flask_migrate import Migrate
from blueprints.usuarios_bp import usuarios
from blueprints.pets_bp import pets
from blueprints.veterinarias_bp import veterinarias
from blueprints.uservet_bp import uservets
from blueprints.servicios_bp import services
from funciones.funciones import *

app = Flask(__name__)
app.config.from_object('config.settings')

db.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)




@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

#Registro de Rutas
app.register_blueprint(usuarios)
app.register_blueprint(pets)
app.register_blueprint(veterinarias)
app.register_blueprint(uservets)
app.register_blueprint(services)




        #Para Desarrollo
if __name__ == '__main__':
    app.run(debug = True)