from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from . import db
from .models import Usuario
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('auth/login.html')
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Atualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=bool(remember_me))
            
            # Redirect para página solicitada ou dashboard
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.admin_dashboard')
            
            flash(f'Bem-vindo, {user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    username = current_user.username
    logout_user()
    flash(f'Logout realizado com sucesso. Até logo, {username}!', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro (apenas para criação inicial)"""
    # Verificar se já existe um admin
    admin_exists = Usuario.query.filter_by(is_admin=True).first()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        admin_key = request.form.get('admin_key')
        
        # Validações
        if not all([username, email, password, confirm_password]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('auth/register.html', admin_exists=admin_exists)
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('auth/register.html', admin_exists=admin_exists)
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('auth/register.html', admin_exists=admin_exists)
        
        # Verificar se usuário já existe
        if Usuario.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('auth/register.html', admin_exists=admin_exists)
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
            return render_template('auth/register.html', admin_exists=admin_exists)
        
        # Criar usuário
        user = Usuario(username=username, email=email)
        user.set_password(password)
        
        # Se não existe admin e a chave está correta, tornar admin
        if not admin_exists and admin_key == 'admin2025':
            user.is_admin = True
            flash('Primeiro admin criado com sucesso!', 'success')
        else:
            flash('Usuário criado com sucesso!', 'success')
        
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', admin_exists=admin_exists)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Alterar senha do usuário logado"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('auth/change_password.html')
        
        if not current_user.check_password(current_password):
            flash('Senha atual incorreta.', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('As novas senhas não coincidem.', 'error')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('auth/change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('auth/change_password.html')
