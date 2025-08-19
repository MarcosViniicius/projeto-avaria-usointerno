from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo_barras = db.Column(db.String(50), unique=True, nullable=True)
    tipo = db.Column(db.String(50), nullable=False)
    avarias = db.relationship('Avaria', backref='produto', lazy=True, cascade='all, delete-orphan')

class Avaria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    peso = db.Column(db.Float, nullable=True)
    quantidade = db.Column(db.Integer, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Avaria {self.id} - Produto {self.produto_id}>'
