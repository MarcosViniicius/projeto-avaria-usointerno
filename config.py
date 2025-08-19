import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Configuração do banco de dados
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Corrige a URL para usar postgresql:// (compatível com SQLAlchemy 1.4+)
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações do Supabase
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_PUBLISHABLE_KEY = os.environ.get('SUPABASE_PUBLISHABLE_KEY')
    
    # Configurações de produção
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'

class ProductionConfig(Config):
    DEBUG = False
    # Força HTTPS em produção
    PREFERRED_URL_SCHEME = 'https'

# Configuração baseada no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
