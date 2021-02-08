from flask_marshmallow import Marshmallow
ma = Marshmallow()

class UsuarioSchema(ma.Schema):
    class Meta:
        fields = ('id','name','email','phone','pais','provincia','ciudad','distrito','direccion','role','fecha_registro')

class VeterinariaSchema(ma.Schema):
    class Meta:
         fields = ('id','logo','ruc','telefono','whatsapp','pais','provincia','ciudad','Distrito','Address','status','fecha_registro')   

class PetSchema(ma.Schema):
    class Meta: 
        fields = ('id','name','birthdate','color','bread','owner')   

class UserVetSchema(ma.Schema):
    class Meta:
        fields = ('id','idvet','iduser','owner')

class ServiceSchema(ma.Schema):
    class Meta:
        fields = ('id','idvet','tipo','nombre','precio','foto')