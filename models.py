from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime , func 
from datetime import datetime

db = SQLAlchemy()
#Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(120),unique = True)
    phone = db.Column(db.Integer, nullable = True)
    pais = db.Column(db.String(200) , nullable = True)
    provincia = db.Column(db.String(200) , nullable = True)
    ciudad = db.Column(db.String(200) , nullable = True)
    distrito = db.Column(db.String(200) , nullable = True)
    direccion = db.Column(db.String(200) , nullable = True)
    role = db.Column(db.Integer, nullable=False)
    pets = db.relationship('Pet',backref='pet_id')
    uservets = db.relationship('UserVet',backref='pet_id')
    fecha_registro = db.Column(db.DateTime,default=datetime.utcnow)
    def __init__(self,name,email,phone,pais,provincia,ciudad,distrito,direccion,role,fecha_registro):
        self.name = name
        self.email = email 
        self.phone = phone 
        self.pais = pais 
        self.provincia = provincia  
        self.ciudad = ciudad 
        self.distrito = distrito 
        self.direccion = direccion 
        self.role = role 
        self.fecha_registro= fecha_registro


class Pet(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255))
    age = db.Column(db.Integer)    
    color = db.Column(db.String(25))
    bread = db.Column(db.String(55))
    owner = db.Column(db.Integer,db.ForeignKey('usuario.id')) 
    def __init__(self,name,age,color,bread,owner):
        self.name= name
        self.age= age   
        self.color= color   
        self.bread= bread   
        self.owner= owner          

class Veterinaria(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    logo = db.Column(db.String(255))    
    ruc = db.Column(db.String(25))
    telefono = db.Column(db.String(25))
    whatsapp = db.Column(db.String(25))
    pais = db.Column(db.String(200))
    provincia = db.Column(db.String(200))
    ciudad = db.Column(db.String(200))
    Distrito = db.Column(db.String(200))
    Address = db.Column(db.String(250))
    status = db.Column(db.Integer,nullable = False)
    fecha_registro = db.Column(db.DateTime,default=datetime.utcnow)
    uservets = db.relationship('UserVet',backref='uservetid')
    services = db.relationship('Services',backref='serviceid')
    

    def __init__(self,name,logo,ruc,telefono,whatsapp,pais,provincia,ciudad,Distrito,Address,status,fecha_registro):
        self.name = name
        self.logo = logo 
        self.ruc = ruc 
        self.telefono = telefono 
        self.whatsapp = whatsapp  
        self.pais = pais 
        self.provincia = provincia 
        self.ciudad = ciudad 
        self.Distrito = Distrito 
        self.Address = Address 
        self.status = status 
        self.fecha_registro =fecha_registro

class UserVet(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    idvet = db.Column(db.Integer,db.ForeignKey('veterinaria.id'))
    iduser = db.Column(db.Integer,db.ForeignKey('usuario.id')) 
    owner = db.Column(db.String(100))
    def __init__(self,idvet,iduser,owner):
        self.idvet = idvet 
        self.iduser = iduser 
        self.owner = owner 

class Services(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    idvet = db.Column(db.Integer,db.ForeignKey('veterinaria.id'))
    tipo = db.Column(db.String(200))
    nombre = db.Column(db.String(200))      
    precio = db.Column(db.Float)
    foto = db.Column(db.String(250))
    def __init__(self,idvet,tipo,nombre,precio,foto):
        self.idvet = idvet
        self.tipo = tipo 
        self.nombre = nombre 
        self.precio = precio 
        self.foto = foto




