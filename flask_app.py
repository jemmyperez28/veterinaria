import json
from six.moves.urllib.request import urlopen
from functools import wraps
from flask import Flask, request, jsonify, _request_ctx_stack , abort
from flask_cors import cross_origin
from jose import jwt
from models import db , Usuario , Pet, Veterinaria, UserVet , Services
from schemas import ma ,UsuarioSchema , PetSchema , VeterinariaSchema , UserVetSchema  , ServiceSchema
from flask_migrate import Migrate
from sqlalchemy import exc


AUTH0_DOMAIN = 'dev-ol5qr49m.us.auth0.com'
API_AUDIENCE = "https://petclinic.pe"
ALGORITHMS = ["RS256"]

app = Flask(__name__)

#desa
#app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:123456@localhost/veterinaria'
#prod
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://jemmyperez:AhNaTcIk28@jemmyperez.mysql.pythonanywhere-services.com/jemmyperez$veterinaria'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)

#db = SQLAlchemy(app)
#ma = Marshmallow(app)

Usuario_Schema = UsuarioSchema()
Usuarios_Schema = UsuarioSchema(many=True)
Pet_Schema = PetSchema()
Pets_Schema = PetSchema(many=True)
Veterinaria_Schema = VeterinariaSchema()
Veterinarias_Schema = VeterinariaSchema(many=True)
UserVet_Schema = UserVetSchema
UserVets_Schema = UserVetSchema(many=True)
Service_Schema = ServiceSchema()
Services_Schema = ServiceSchema(many=True)


# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token

def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated

def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
            for token_scope in token_scopes:
                if token_scope == required_scope:
                    return True
    return False

@app.route("/api/public")
@cross_origin(headers=["Content-Type", "Authorization"])
def public():
    response = "Hello from a public endpoint! You don't need to be authenticated to see this."
    return jsonify(message=response)

# This needs authentication
@app.route("/api/private")
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def private():
    response = "Hello from a private endpoint! You need to be authenticated to see this."
    return jsonify(message=response)

# This needs authorization
@app.route("/api/private-scoped")
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def private_scoped():
    if requires_scope("read:messages"):
        response = "Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this."
        return jsonify(message=response)
    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)

#Rutas
#Usuarios
@app.route('/usuarios', methods=['POST'])
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
    nuevo_usuario = Usuario(name,email,phone,pais,provincia,ciudad,distrito,direccion,role,fecha_registro)
                       

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


@app.route('/usuarios' , methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_usuarios():
        all_usuarios = Usuario.query.all()
        result = Usuarios_Schema.dump(all_usuarios)
        return jsonify(result)


@app.route('/usuarios/<id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_usuario(id):
    usuario = Usuario.query.get(id)
    result = Usuario_Schema.dump(usuario)
    return jsonify(result)

@app.route('/usuarios/<id>', methods=['PUT'])
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

@app.route('/usuarios/<id>', methods=['DELETE'])
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
    
#Pets
@app.route('/pets', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_pet():
    name = request.json['name']
    birthdate = request.json['birthdate']    
    color = request.json['color']
    bread = request.json['bread']
    owner = request.json['owner']  
    nuevo_pet = Pet(name,age,color,bread,owner)

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


@app.route('/pets' , methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_pets():
        all_pets = Pet.query.all()
        result = Pets_Schema.dump(all_pets)
        return jsonify(result)


@app.route('/pets/<id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_pet(id):
    pet = Pet.query.get(id)
    result = Pet_Schema.dump(pet)
    return jsonify(result)


@app.route('/pets/<id>', methods=['PUT'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def update_pet(id):
    pet = Pet.query.get(id)
    name = request.json['name']
    age = request.json['age']    
    color = request.json['color']
    bread = request.json['bread']
    owner = request.json['owner'] 

    #actualizo campos
    pet.name = name
    pet.age = age
    pet.color = color
    pet.bread = bread
    pet.owner = owner

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


#Veterinaria
@app.route('/veterinarias', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_veterinaria():
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
    status = request.json['status'] 
    fecha_registro = request.json['fecha_registro'] 
    id_usuario = request.json['id_usuario']
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

@app.route('/veterinarias' , methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_veterinarias():
        all_veterinarias = Veterinaria.query.all()
        result = Veterinarias_Schema.dump(all_veterinarias)
        return jsonify(result)


@app.route('/veterinarias/<id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_veterinaria(id):
    veterinaria = Veterinaria.query.get(id)
    result = Veterinaria_Schema.dump(veterinaria)
    return jsonify(result)

#UserVet
#Veterinarias que pertenecen a un Usuario
@app.route('/uservet/<user_id>' , methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_uservets(user_id):
        uservets = UserVet.query.with_entities(UserVet.id,UserVet.iduser,UserVet.idvet).filter_by(iduser=user_id)
        result = UserVets_Schema.dump(uservets)
        return jsonify(result)

#Servicios     
@app.route('/servicios', methods=['POST'])
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
@app.route('/servicios/<id>', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_servicios(id):
    servicess = Services.query.with_entities(Services.id,Services.idvet,Services.tipo,Services.nombre,Services.precio,Services.foto).filter_by(idvet=id)
    result = Services_Schema.dump(servicess)
    return jsonify(result)

@app.route('/servicios/<id>', methods=['PUT'])
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

@app.route('/servicios/<id>', methods=['DELETE'])
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













        #Para Desarrollo
#if __name__ == '__main__':
#    app.run(debug = True)