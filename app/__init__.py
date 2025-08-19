from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Usar configuração simples
    from config import Config
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import Usuario
        return Usuario.query.get(int(user_id))
    
    # Registrar blueprints
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Importar modelos para que o Flask-Migrate os reconheça
    from . import models
    
    return app
