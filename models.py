from app import db
from sqlalchemy.dialects.postgresql import JSON

class SolarPanel(db.Model):
    __tablename__ = 'solarpanel'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15))
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(250))
    
    
    def __init__(self, ip_address, email, name):
        self.ip_address = ip_address
        self.email = email
        self.name = name
    
    def __repr__(self):
        return '<id {}>'.format(self.id)
    