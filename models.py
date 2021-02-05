from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
#Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(120),unique = True , nullable=False)
    password = db.Column(db.String(255))

    def __init__(self,name,email,password):
        self.name = name
        self.email = email 
        self.password = password 