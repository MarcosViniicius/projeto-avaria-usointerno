# 📋 Deploy na Vercel - Sistema de Avarias

## ✅ Status do Projeto
- ✅ Banco de dados: Exclusivamente Supabase PostgreSQL
- ✅ Driver: pg8000 (compatível com Vercel)
- ✅ Configuração: vercel.json otimizado
- ✅ Ambiente: .env configurado para produção

## 🚀 Passos para Deploy

### 1. Preparar o repositório
```bash
# Certificar que todos os arquivos estão commitados
git add .
git commit -m "Configuração final para Vercel com Supabase"
git push origin main
```

### 2. Deploy na Vercel
1. Acesse [vercel.com](https://vercel.com)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente:
   - `DATABASE_URL`: postgresql+pg8000://postgres.bynnyllzvcacyqqczvsd:Mini1000%23@aws-1-us-east-2.pooler.supabase.com:6543/postgres
   - `SECRET_KEY`: gere uma nova chave secreta
   - `SUPABASE_URL`: sua URL do Supabase
   - `SUPABASE_KEY`: sua chave pública do Supabase

### 3. Verificar após deploy
- ✅ Banco conecta corretamente
- ✅ Todas as funcionalidades funcionam
- ✅ PWA instala corretamente

## 📁 Arquivos Importantes
- `requirements.txt`: pg8000 em vez de psycopg2-binary
- `vercel.json`: Configurações otimizadas para Vercel
- `runtime.txt`: Python 3.11 (recomendado para Vercel)
- `.env`: Variáveis de ambiente (não commitado)
- `.env.example`: Template para variáveis

## 🔧 Configurações Especiais

### requirements.txt
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-Login==0.6.3
python-dotenv==1.0.0
pg8000==1.31.4
```

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "run.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "run.py"
    }
  ],
  "env": {
    "DATABASE_URL": "@database_url",
    "SECRET_KEY": "@secret_key",
    "SUPABASE_URL": "@supabase_url",
    "SUPABASE_KEY": "@supabase_key"
  },
  "functions": {
    "run.py": {
      "maxDuration": 30
    }
  }
}
```

### DATABASE_URL Format
```
postgresql+pg8000://postgres.bynnyllzvcacyqqczvsd:Mini1000%23@aws-1-us-east-2.pooler.supabase.com:6543/postgres
```

## 🎯 Funcionalidades Testadas
- ✅ Registro de avarias por setor
- ✅ Scanner de código de barras (PWA)
- ✅ Dashboard administrativo
- ✅ Autenticação e autorização
- ✅ Exportação para Excel
- ✅ Estatísticas e relatórios
- ✅ Banco exclusivamente Supabase

## 🔍 Troubleshooting

### Erro de build na Vercel
- Verificar se pg8000 está no requirements.txt
- Confirmar Python 3.11 no runtime.txt
- Verificar maxLambdaSize no vercel.json

### Erro de conexão com banco
- Verificar DATABASE_URL nas env vars da Vercel
- Confirmar que está usando postgresql+pg8000://
- Verificar credenciais do Supabase

### PWA não funciona
- Verificar manifest.json
- Verificar service worker (sw.js)
- Testar em HTTPS (Vercel fornece automaticamente)
