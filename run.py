import os
from app import create_app

# Criar instância da aplicação
app = create_app()

# Para Vercel, a aplicação deve estar disponível como 'app'
# e também suportar execução local
if __name__ == '__main__':
    # Configuração para desenvolvimento local
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
