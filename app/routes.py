from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, Response, make_response
from flask_login import login_required, current_user
from . import db
from .models import Produto, Avaria, Usuario
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import csv
import io
import json

bp = Blueprint('main', __name__)

# Página inicial
@bp.route('/')
def index():
    return render_template('index.html')

# Registro de avaria hortifruti
@bp.route('/registrar/hortifruti', methods=['GET', 'POST'])
def registro_hortifruti():
    if request.method == 'POST':
        try:
            nome_produto = request.form.get('nome_produto')
            peso = request.form.get('peso', type=float)
            
            if not nome_produto or not peso:
                flash('Por favor, preencha todos os campos obrigatórios.', 'error')
                return render_template('registro_hortifruti.html')
            
            # Buscar ou criar o produto
            produto = Produto.query.filter_by(nome=nome_produto, tipo='hortifruti').first()
            if not produto:
                produto = Produto(nome=nome_produto, tipo='hortifruti')
                db.session.add(produto)
                db.session.commit()
            
            # Criar registro de avaria
            avaria = Avaria(produto_id=produto.id, peso=peso)
            db.session.add(avaria)
            db.session.commit()
            
            flash(f'Avaria registrada com sucesso! Produto: {nome_produto}, Peso: {peso}kg', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            flash(f'Erro ao registrar avaria: {str(e)}', 'error')
            return render_template('registro_hortifruti.html')
    
    return render_template('registro_hortifruti.html')

# Registro de avaria uso interno
@bp.route('/registrar/interno', methods=['GET', 'POST'])
def registro_interno():
    if request.method == 'POST':
        try:
            codigo_barras = request.form.get('codigo_barras')
            nome_produto = request.form.get('nome_produto')
            quantidade = request.form.get('quantidade', type=int, default=1)
            
            if not codigo_barras or not nome_produto:
                flash('Por favor, preencha todos os campos obrigatórios.', 'error')
                return render_template('registro_interno.html')
            
            # Buscar ou criar o produto
            produto = Produto.query.filter_by(codigo_barras=codigo_barras, tipo='interno').first()
            if not produto:
                produto = Produto(nome=nome_produto, codigo_barras=codigo_barras, tipo='interno')
                db.session.add(produto)
                db.session.commit()
            else:
                # Atualizar nome se necessário
                if produto.nome != nome_produto:
                    produto.nome = nome_produto
                    db.session.commit()
            
            # Criar registro de avaria
            avaria = Avaria(produto_id=produto.id, quantidade=quantidade)
            db.session.add(avaria)
            db.session.commit()
            
            flash(f'Avaria registrada com sucesso! Produto: {nome_produto}, Código: {codigo_barras}, Quantidade: {quantidade}', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            flash(f'Erro ao registrar avaria: {str(e)}', 'error')
            return render_template('registro_interno.html')
    
    return render_template('registro_interno.html')

# === ÁREA ADMINISTRATIVA ===

@bp.route('/admin')
@login_required
def admin_dashboard():
    """Painel administrativo principal"""
    try:
        # Estatísticas gerais
        total_registros = Avaria.query.count()
        registros_hoje = Avaria.query.filter(
            func.date(Avaria.data_registro) == datetime.now().date()
        ).count()
        registros_semana = Avaria.query.filter(
            Avaria.data_registro >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Produtos mais registrados
        produtos_mais_registrados = db.session.query(
            Produto.nome,
            Produto.tipo,
            func.count(Avaria.id).label('total_registros'),
            func.sum(Avaria.peso).label('peso_total'),
            func.sum(Avaria.quantidade).label('quantidade_total')
        ).join(Avaria).group_by(Produto.id).order_by(desc('total_registros')).limit(10).all()
        
        # Registros recentes
        registros_recentes = db.session.query(Avaria, Produto).join(Produto).order_by(desc(Avaria.data_registro)).limit(20).all()
        
        stats = {
            'total_registros': total_registros,
            'registros_hoje': registros_hoje,
            'registros_semana': registros_semana,
            'produtos_mais_registrados': produtos_mais_registrados,
            'registros_recentes': registros_recentes
        }
        
        return render_template('admin/dashboard.html', stats=stats)
        
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@bp.route('/admin/registros')
@login_required
def admin_registros():
    """Visualização detalhada de todos os registros"""
    try:
        # Filtros
        tipo_filtro = request.args.get('tipo', 'todos')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        produto_filtro = request.args.get('produto', '')
        
        # Query base
        query = db.session.query(Avaria, Produto).join(Produto)
        
        # Aplicar filtros
        if tipo_filtro != 'todos':
            query = query.filter(Produto.tipo == tipo_filtro)
        
        if data_inicio:
            query = query.filter(Avaria.data_registro >= datetime.strptime(data_inicio, '%Y-%m-%d'))
        
        if data_fim:
            query = query.filter(Avaria.data_registro <= datetime.strptime(data_fim + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
        
        if produto_filtro:
            query = query.filter(Produto.nome.ilike(f'%{produto_filtro}%'))
        
        # Paginação
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        registros = query.order_by(desc(Avaria.data_registro)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Lista de produtos para filtro
        produtos = db.session.query(Produto.nome).distinct().order_by(Produto.nome).all()
        produtos_lista = [p[0] for p in produtos]
        
        return render_template('admin/registros.html', 
                             registros=registros,
                             produtos_lista=produtos_lista,
                             filtros={
                                 'tipo': tipo_filtro,
                                 'data_inicio': data_inicio,
                                 'data_fim': data_fim,
                                 'produto': produto_filtro
                             })
        
    except Exception as e:
        flash(f'Erro ao carregar registros: {str(e)}', 'error')
        return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/exportar/<formato>')
def admin_exportar(formato):
    """Exportar dados em diferentes formatos"""
    try:
        # Filtros (mesma lógica da visualização)
        tipo_filtro = request.args.get('tipo', 'todos')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        produto_filtro = request.args.get('produto', '')
        
        # Query base
        query = db.session.query(Avaria, Produto).join(Produto)
        
        # Aplicar filtros
        if tipo_filtro != 'todos':
            query = query.filter(Produto.tipo == tipo_filtro)
        
        if data_inicio:
            query = query.filter(Avaria.data_registro >= datetime.strptime(data_inicio, '%Y-%m-%d'))
        
        if data_fim:
            query = query.filter(Avaria.data_registro <= datetime.strptime(data_fim + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
        
        if produto_filtro:
            query = query.filter(Produto.nome.ilike(f'%{produto_filtro}%'))
        
        registros = query.order_by(desc(Avaria.data_registro)).all()
        
        # Preparar dados para exportação
        dados = []
        for avaria, produto in registros:
            dados.append({
                'id': avaria.id,
                'produto_nome': produto.nome,
                'produto_tipo': produto.tipo,
                'codigo_barras': produto.codigo_barras or '',
                'peso': avaria.peso or '',
                'quantidade': avaria.quantidade or '',
                'data_registro': avaria.data_registro.strftime('%d/%m/%Y %H:%M:%S')
            })
        
        # Gerar arquivo baseado no formato
        if formato == 'csv':
            return exportar_csv(dados)
        elif formato == 'txt':
            return exportar_txt(dados)
        elif formato == 'json':
            return exportar_json(dados)
        else:
            flash('Formato de exportação não suportado.', 'error')
            return redirect(url_for('main.admin_registros'))
            
    except Exception as e:
        flash(f'Erro ao exportar dados: {str(e)}', 'error')
        return redirect(url_for('main.admin_registros'))

def exportar_csv(dados):
    """Exportar dados para CSV"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'id', 'produto_nome', 'produto_tipo', 'codigo_barras', 
        'peso', 'quantidade', 'data_registro'
    ])
    
    writer.writeheader()
    for row in dados:
        writer.writerow(row)
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=avarias_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    
    return response

def exportar_txt(dados):
    """Exportar dados para TXT"""
    output = io.StringIO()
    
    output.write("=== RELATÓRIO DE AVARIAS ===\n")
    output.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    output.write(f"Total de registros: {len(dados)}\n\n")
    
    for i, row in enumerate(dados, 1):
        output.write(f"--- Registro {i} ---\n")
        output.write(f"ID: {row['id']}\n")
        output.write(f"Produto: {row['produto_nome']}\n")
        output.write(f"Tipo: {row['produto_tipo']}\n")
        if row['codigo_barras']:
            output.write(f"Código de Barras: {row['codigo_barras']}\n")
        if row['peso']:
            output.write(f"Peso: {row['peso']} kg\n")
        if row['quantidade']:
            output.write(f"Quantidade: {row['quantidade']}\n")
        output.write(f"Data: {row['data_registro']}\n\n")
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=avarias_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    
    return response

def exportar_json(dados):
    """Exportar dados para JSON"""
    export_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_records': len(dados),
            'format': 'json'
        },
        'data': dados
    }
    
    response = make_response(json.dumps(export_data, indent=2, ensure_ascii=False))
    response.headers['Content-Disposition'] = f'attachment; filename=avarias_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    
    return response

@bp.route('/admin/estatisticas')
def admin_estatisticas():
    """Página de estatísticas detalhadas"""
    try:
        # Estatísticas por tipo
        stats_tipo = db.session.query(
            Produto.tipo,
            func.count(Avaria.id).label('total_registros'),
            func.sum(Avaria.peso).label('peso_total'),
            func.sum(Avaria.quantidade).label('quantidade_total')
        ).join(Avaria).group_by(Produto.tipo).all()
        
        # Estatísticas por período (últimos 30 dias)
        stats_periodo = []
        for i in range(30):
            data = datetime.now().date() - timedelta(days=i)
            count = Avaria.query.filter(func.date(Avaria.data_registro) == data).count()
            stats_periodo.append({
                'data': data.strftime('%d/%m'),
                'registros': count
            })
        
        stats_periodo.reverse()  # Ordem cronológica
        
        # Top 10 produtos com mais avarias
        top_produtos = db.session.query(
            Produto.nome,
            Produto.tipo,
            func.count(Avaria.id).label('total_avarias')
        ).join(Avaria).group_by(Produto.id).order_by(desc('total_avarias')).limit(10).all()
        
        return render_template('admin/estatisticas.html', 
                             stats_tipo=stats_tipo,
                             stats_periodo=stats_periodo,
                             top_produtos=top_produtos)
        
    except Exception as e:
        flash(f'Erro ao carregar estatísticas: {str(e)}', 'error')
        return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/limpar')
def admin_limpar():
    """Página para limpeza de dados"""
    return render_template('admin/limpar.html')

@bp.route('/admin/limpar/confirmar', methods=['POST'])
def admin_limpar_confirmar():
    """Limpar dados antigos (com confirmação)"""
    try:
        acao = request.form.get('acao')
        senha_confirmacao = request.form.get('senha_confirmacao')
        
        # Senha simples para confirmação (em produção, usar algo mais seguro)
        if senha_confirmacao != 'admin123':
            flash('Senha de confirmação incorreta!', 'error')
            return redirect(url_for('main.admin_limpar'))
        
        if acao == 'limpar_30_dias':
            data_limite = datetime.now() - timedelta(days=30)
            registros_antigos = Avaria.query.filter(Avaria.data_registro < data_limite)
            count = registros_antigos.count()
            registros_antigos.delete()
            db.session.commit()
            flash(f'{count} registros anteriores a 30 dias foram removidos.', 'success')
            
        elif acao == 'limpar_tudo':
            count = Avaria.query.count()
            Avaria.query.delete()
            Produto.query.delete()
            db.session.commit()
            flash(f'Todos os {count} registros foram removidos.', 'success')
        
        return redirect(url_for('main.admin_dashboard'))
        
    except Exception as e:
        flash(f'Erro ao limpar dados: {str(e)}', 'error')
        return redirect(url_for('main.admin_limpar'))

# === FUNCIONALIDADES DE EDIÇÃO ===

@bp.route('/admin/editar/avaria/<int:avaria_id>', methods=['GET', 'POST'])
@login_required
def admin_editar_avaria(avaria_id):
    """Editar registro de avaria"""
    try:
        avaria = Avaria.query.get_or_404(avaria_id)
        produto = avaria.produto
        
        if request.method == 'POST':
            # Campos editáveis
            novo_nome_produto = request.form.get('nome_produto')
            novo_codigo_barras = request.form.get('codigo_barras')
            novo_peso = request.form.get('peso', type=float)
            nova_quantidade = request.form.get('quantidade', type=int)
            novas_observacoes = request.form.get('observacoes')
            nova_data = request.form.get('data_registro')
            
            # Validações
            if not novo_nome_produto:
                flash('Nome do produto é obrigatório.', 'error')
                return render_template('admin/editar_avaria.html', avaria=avaria, produto=produto)
            
            # Atualizar produto se necessário
            if produto.nome != novo_nome_produto:
                produto.nome = novo_nome_produto
            
            if produto.tipo == 'interno' and novo_codigo_barras != produto.codigo_barras:
                # Verificar se novo código já existe
                if novo_codigo_barras and Produto.query.filter(
                    Produto.codigo_barras == novo_codigo_barras,
                    Produto.id != produto.id
                ).first():
                    flash('Código de barras já existe em outro produto.', 'error')
                    return render_template('admin/editar_avaria.html', avaria=avaria, produto=produto)
                produto.codigo_barras = novo_codigo_barras
            
            # Atualizar avaria
            if produto.tipo == 'hortifruti':
                avaria.peso = novo_peso
                avaria.quantidade = None
            else:
                avaria.quantidade = nova_quantidade
                avaria.peso = None
            
            avaria.observacoes = novas_observacoes
            
            # Atualizar data se fornecida
            if nova_data:
                try:
                    avaria.data_registro = datetime.strptime(nova_data, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('Formato de data inválido.', 'error')
                    return render_template('admin/editar_avaria.html', avaria=avaria, produto=produto)
            
            db.session.commit()
            
            flash(f'Registro #{avaria.id} atualizado com sucesso!', 'success')
            return redirect(url_for('main.admin_registros'))
        
        return render_template('admin/editar_avaria.html', avaria=avaria, produto=produto)
        
    except Exception as e:
        flash(f'Erro ao editar registro: {str(e)}', 'error')
        return redirect(url_for('main.admin_registros'))

@bp.route('/admin/editar/produto/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def admin_editar_produto(produto_id):
    """Editar produto"""
    try:
        produto = Produto.query.get_or_404(produto_id)
        
        if request.method == 'POST':
            novo_nome = request.form.get('nome')
            novo_codigo = request.form.get('codigo_barras')
            
            if not novo_nome:
                flash('Nome do produto é obrigatório.', 'error')
                return render_template('admin/editar_produto.html', produto=produto)
            
            # Verificar se código já existe em outro produto
            if novo_codigo and produto.tipo == 'interno':
                produto_existente = Produto.query.filter(
                    Produto.codigo_barras == novo_codigo,
                    Produto.id != produto.id
                ).first()
                if produto_existente:
                    flash('Código de barras já existe em outro produto.', 'error')
                    return render_template('admin/editar_produto.html', produto=produto)
            
            produto.nome = novo_nome
            if produto.tipo == 'interno':
                produto.codigo_barras = novo_codigo
            db.session.commit()
            
            flash(f'Produto "{produto.nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('main.admin_produtos'))
        
        return render_template('admin/editar_produto.html', produto=produto)
        
    except Exception as e:
        flash(f'Erro ao editar produto: {str(e)}', 'error')
        return redirect(url_for('main.admin_produtos'))

@bp.route('/admin/produtos')
@login_required
def admin_produtos():
    """Gestão de produtos"""
    try:
        # Filtros
        tipo_filtro = request.args.get('tipo', 'todos')
        busca = request.args.get('busca', '')
        
        # Query base
        query = Produto.query
        
        # Aplicar filtros
        if tipo_filtro != 'todos':
            query = query.filter(Produto.tipo == tipo_filtro)
        
        if busca:
            query = query.filter(
                db.or_(
                    Produto.nome.ilike(f'%{busca}%'),
                    Produto.codigo_barras.ilike(f'%{busca}%')
                )
            )
        
        # Paginação
        page = request.args.get('page', 1, type=int)
        per_page = 30
        
        produtos = query.order_by(Produto.nome).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/produtos.html', 
                             produtos=produtos,
                             filtros={
                                 'tipo': tipo_filtro,
                                 'busca': busca
                             })
        
    except Exception as e:
        flash(f'Erro ao carregar produtos: {str(e)}', 'error')
        return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/deletar/avaria/<int:avaria_id>', methods=['POST'])
@login_required
def admin_deletar_avaria(avaria_id):
    """Deletar registro de avaria"""
    try:
        avaria = Avaria.query.get_or_404(avaria_id)
        produto_nome = avaria.produto.nome
        
        db.session.delete(avaria)
        db.session.commit()
        
        flash(f'Registro de avaria #{avaria_id} ({produto_nome}) deletado com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao deletar registro: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_registros'))

@bp.route('/admin/deletar/produto/<int:produto_id>', methods=['POST'])
@login_required
def admin_deletar_produto(produto_id):
    """Deletar produto e todos seus registros"""
    try:
        produto = Produto.query.get_or_404(produto_id)
        produto_nome = produto.nome
        num_avarias = len(produto.avarias)
        
        # Deletar produto (cascade deleta as avarias)
        db.session.delete(produto)
        db.session.commit()
        
        flash(f'Produto "{produto_nome}" e {num_avarias} registros de avaria deletados com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao deletar produto: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_produtos'))

@bp.route('/admin/usuarios')
@login_required
def admin_usuarios():
    """Gestão de usuários (apenas para admins)"""
    try:
        if not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem gerenciar usuários.', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        usuarios = Usuario.query.order_by(Usuario.id.desc()).all()
        
        return render_template('admin/usuarios.html', usuarios=usuarios)
        
    except Exception as e:
        flash(f'Erro ao carregar usuários: {str(e)}', 'error')
        return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/usuarios/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def admin_toggle_admin(user_id):
    """Alternar status de admin do usuário"""
    try:
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        user = Usuario.query.get_or_404(user_id)
        
        if user.id == current_user.id:
            flash('Você não pode remover seus próprios privilégios de admin.', 'error')
            return redirect(url_for('main.admin_usuarios'))
        
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = 'promovido a' if user.is_admin else 'removido de'
        flash(f'Usuário {user.username} {status} administrador.', 'success')
        
    except Exception as e:
        flash(f'Erro ao alterar privilégios: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_usuarios'))
