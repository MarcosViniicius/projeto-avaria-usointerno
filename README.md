# Sistema de Registro de Avarias - Deploy Supabase + Vercel

## 📋 Visão Geral

Siste## 🛠️ Tecnologias

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Font Awesome, ZXing-JS
- **Banco**: PostgreSQL (Supabase)
- **Deploy**: Vercel
- **PWA**: Service Workers, Manifest

## 📁 Estrutura do Projeto

````
mercado_app/
├── app/
│   ├── __init__.py          # Configuração principal do Flask
│   ├── models.py            # Modelos do banco (Usuario, Produto, Avaria)
│   ├── routes.py            # Rotas principais e lógica de negócio
│   ├── auth.py              # Autenticação e autorização
│   ├── static/
│   │   ├── css/             # Estilos customizados
│   │   ├── js/              # JavaScript (scanner, validações)
│   │   ├── manifest.json    # Configuração PWA
│   │   └── sw.js           # Service Worker
│   └── templates/
│       ├── admin/           # Templates do painel admin
│       ├── auth/            # Templates de login/registro
│       ├── base.html        # Template base
│       ├── index.html       # Página inicial
│       ├── registro_hortifruti.html
│       └── registro_interno.html
├── .env                     # Variáveis de ambiente (local)
├── .env.example             # Exemplo de configuração
├── .gitignore               # Arquivos ignorados pelo Git
├── config.py                # Configurações da aplicação
├── init_db.py               # Script de inicialização do banco
├── requirements.txt         # Dependências Python
├── run.py                   # Ponto de entrada da aplicação
├── vercel.json              # Configuração para deploy Vercel
└── README.md               # Esta documentação
```para registro de avarias de produtos com scanner de código de barras, desenvolvido em Flask e configurado para deploy na Vercel com banco de dados Supabase.

## 🚀 Deploy na Vercel com Supabase

### 1. Configurar Supabase

1. **Criar projeto no Supabase:**

   - Acesse [supabase.com](https://supabase.com)
   - Crie uma nova conta ou faça login
   - Clique em "New Project"
   - Escolha nome e senha para o banco

2. **Obter credenciais:**
   - No dashboard do projeto, vá em `Settings > API`
   - Copie a `URL` e `anon/public key`
   - Vá em `Settings > Database`
   - Copie a string de conexão (`Connection String`)

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com:

```env
# Configurações do Flask
SECRET_KEY=sua-chave-secreta-super-segura-aqui
FLASK_ENV=production

# Configurações do Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
````

### 3. Instalar Dependências e Inicializar

```bash
# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados no Supabase (opcional - pode usar SQL direto)
python init_db.py
```

### 4. Deploy na Vercel

1. **Preparar repositório:**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Deploy na Vercel:**
   - Acesse [vercel.com](https://vercel.com)
   - Conecte sua conta GitHub
   - Importe o repositório
   - Configure as variáveis de ambiente:
     - `SECRET_KEY`
     - `DATABASE_URL`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `FLASK_ENV=production`

## 📱 Funcionalidades

- **Scanner de Código de Barras**: ZXing-JS integrado
- **Gestão de Produtos**: CRUD completo para produtos
- **Registro de Avarias**: Sistema completo de registro
- **Dashboard Admin**: Estatísticas e controle total
- **Exportação de Dados**: CSV, TXT, JSON
- **Autenticação**: Sistema seguro com Flask-Login
- **PWA Ready**: Funciona como app móvel
- **Responsivo**: Bootstrap 5

## � Credenciais Padrão

Após inicialização:

- **Usuário**: admin
- **Senha**: admin123

⚠️ **IMPORTANTE**: Altere a senha após o primeiro login!

## �️ Tecnologias

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Font Awesome, ZXing-JS
- **Banco**: PostgreSQL (Supabase)
- **Deploy**: Vercel
- **PWA**: Service Workers, Manifest
