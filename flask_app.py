import json
from six.moves.urllib.request import urlopen
from functools import wraps
from flask import Flask, request, jsonify, _request_ctx_stack
from flask_cors import cross_origin
from jose import jwt

from models import db , Usuario
from schemas import ma ,UsuarioSchema
from flask_migrate import Migrate


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


#Rutas Test
@app.route('/usuarios', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_usuario():

    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    nuevo_usuario = Usuario(name,email,password)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return Usuario_Schema.jsonify(nuevo_usuario)


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
    #usuario = Usuario.query.get(id)
    #return Usuario_schema.jsonify(usuario)
    usuario = Usuario.query.get(id)
    result = Usuario_Schema.dump(usuario)
    return jsonify(result)

@app.route('/usuarios/<id>', methods=['PUT'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def update_usuario(id):
    user = Usuario.query.get(id)
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    
    #actualizo campos
    user.name = name
    db.session.commit()
    return Usuario_Schema.jsonify(user)

@app.route('/usuarios/<id>', methods=['DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def delete_usuario(id):
    user = Usuario.query.get(id)
    print(user)
    db.session.delete(user)
    db.session.commit()

    return Usuario_Schema.jsonify(user)
    

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

#Para Desarrollo
#if __name__ == '__main__':
#    app.run(debug = True)
