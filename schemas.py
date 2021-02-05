from flask_marshmallow import Marshmallow
ma = Marshmallow()

class UsuarioSchema(ma.Schema):
    class Meta:
        fields = ('id','name','email','password')