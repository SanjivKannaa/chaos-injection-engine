from extensions import db
from datetime import datetime

class Resources(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resourceName = db.Column(db.String(50), nullable=False, unique=True)
    privateIP = db.Column(db.String(15), nullable=False, unique=True)
    publicIP = db.Column(db.String(15), nullable=True)
