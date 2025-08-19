#!/usr/bin/env python3
"""
Script alternativo para inicializar o banco no Supabase
Usando Flask-Migrate para criar as tabelas
"""

import os
from dotenv import load_dotenv
from flask import Flask
from app import create_app, db
from app.models import Usuario, Produto, Avaria
from werkzeug.security import generate_password_hash

# Carregar variáveis de ambiente
load_dotenv()

def init_db_with_flask():
    """Inicializa o banco usando Flask-Migrate"""
    
    print("🚀 INICIALIZANDO BANCO COM FLASK")
    print("=" * 50)
    
    try:
        # Criar aplicação Flask
        app = create_app('production')
        
        with app.app_context():
            print("📋 Criando tabelas com SQLAlchemy...")
            
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar se já existe um usuário admin
            admin_exists = Usuario.query.filter_by(username='admin').first()
            
            if not admin_exists:
                print("👤 Criando usuário administrador...")
                admin_user = Usuario(
                    username='admin',
                    email='admin@avarias.com',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True
                )
                db.session.add(admin_user)
                
                print("📦 Criando produtos de exemplo...")
                produtos_exemplo = [
                    Produto(nome='Arroz 5kg', tipo='interno', codigo_barras='7891234567890'),
                    Produto(nome='Feijão 1kg', tipo='interno', codigo_barras='7891234567891'),
                    Produto(nome='Açúcar 1kg', tipo='interno', codigo_barras='7891234567892'),
                    Produto(nome='Óleo de Soja 900ml', tipo='interno', codigo_barras='7891234567893'),
                    Produto(nome='Maçã', tipo='hortifruti'),
                    Produto(nome='Banana', tipo='hortifruti'),
                    Produto(nome='Laranja', tipo='hortifruti'),
                    Produto(nome='Tomate', tipo='hortifruti'),
                ]
                
                for produto in produtos_exemplo:
                    db.session.add(produto)
                
                db.session.commit()
                print("✅ Dados iniciais criados com sucesso!")
                print("\n📋 Credenciais do administrador:")
                print("   Usuário: admin")
                print("   Senha: admin123")
                print("   ⚠️  ALTERE A SENHA APÓS O PRIMEIRO LOGIN!")
            else:
                print("✅ Usuário administrador já existe.")
            
            # Verificar dados
            total_usuarios = Usuario.query.count()
            total_produtos = Produto.query.count()
            total_avarias = Avaria.query.count()
            
            print(f"\n📊 Dados no banco:")
            print(f"   👥 Usuários: {total_usuarios}")
            print(f"   📦 Produtos: {total_produtos}")
            print(f"   ⚠️  Avarias: {total_avarias}")
            
            print("\n🎉 Banco de dados inicializado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {str(e)}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

if __name__ == '__main__':
    print("🏗️  INICIALIZAÇÃO ALTERNATIVA DO BANCO")
    print("=" * 50)
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não configurada!")
        exit(1)
    
    print(f"🔗 Conectando com: {database_url[:50]}...")
    
    if init_db_with_flask():
        print("\n✅ Processo concluído com sucesso!")
        print("\n📝 Próximos passos:")
        print("1. Execute 'python run.py' para testar localmente")
        print("2. Configure as variáveis de ambiente no Vercel")
        print("3. Faça o deploy da aplicação")
    else:
        print("\n❌ Falha na inicialização.")
        print("\n💡 Alternativas:")
        print("1. Execute o SQL manualmente no Supabase Dashboard")
        print("2. Verifique se a URL do banco está correta")
        print("3. Teste a conexão diretamente no Supabase")
